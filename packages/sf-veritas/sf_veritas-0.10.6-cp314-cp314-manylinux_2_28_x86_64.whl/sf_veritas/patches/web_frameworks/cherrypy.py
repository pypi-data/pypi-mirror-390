"""
CherryPy web framework patch for OTEL-style network hop capture.
Captures request/response headers and bodies when enabled via env vars.
"""

import inspect
import sys
import types
from typing import Any, Callable, Iterable, List, Optional, Set

from ... import _sffuncspan_config, app_config
from ...constants import (
    FUNCSPAN_OVERRIDE_HEADER_BYTES,
    SAILFISH_TRACING_HEADER,
    SAILFISH_TRACING_HEADER_BYTES,
)
from ...custom_excepthook import custom_excepthook
from ...env_vars import (
    SF_DEBUG,
    SF_NETWORKHOP_CAPTURE_REQUEST_BODY,
    SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS,
    SF_NETWORKHOP_CAPTURE_RESPONSE_BODY,
    SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS,
    SF_NETWORKHOP_REQUEST_LIMIT_MB,
    SF_NETWORKHOP_RESPONSE_LIMIT_MB,
)
from ...fast_network_hop import fast_send_network_hop_fast, register_endpoint
from ...thread_local import (
    clear_c_tls_parent_trace_id,
    clear_current_request_path,
    clear_outbound_header_base,
    clear_trace_id,
    generate_new_trace_id,
    get_or_set_sf_trace_id,
    get_sf_trace_id,
    set_current_request_path,
    set_funcspan_override,
    set_outbound_header_base,
)
from .cors_utils import inject_sailfish_headers, should_inject_headers
from .utils import _is_user_code, should_skip_route

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Routes to skip (set by patch_cherrypy)
_ROUTES_TO_SKIP = []

# ------------------------------------------------------------------ #
#  Robust un-wrapper (handles LateParamPageHandler, etc.)
# ------------------------------------------------------------------ #
_ATTR_CANDIDATES: Iterable[str] = (
    "resolver",
    "func",
    "python_func",
    "_resolver",
    "wrapped_func",
    "__func",
    "callable",  # CherryPy handlers
)


def _unwrap_user_func(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Walk through the layers of wrappers/decorators/handler objects around *fn*
    and return the first plain Python *function* object that:
        • lives in user-land code (per _is_user_code)
        • has a real __code__ object.
    The search is breadth-first and robust to cyclic references.
    """
    seen: Set[int] = set()
    queue = [fn]

    while queue:
        current = queue.pop()
        cid = id(current)
        if cid in seen:
            continue
        seen.add(cid)

        # ── 1. Bound methods (types.MethodType) ──────────────────────────
        # CherryPy's LateParamPageHandler.callable is usually a bound method.
        if isinstance(current, types.MethodType):
            queue.append(current.__func__)
            continue  # don't inspect the MethodType itself any further

        # ── 2. Plain user function?  ─────────────────────────────────────
        if inspect.isfunction(current) and _is_user_code(
            getattr(current.__code__, "co_filename", "")
        ):
            return current

        # ── 3. CherryPy PageHandler exposes `.callable` ──────────────────
        target = getattr(current, "callable", None)
        if callable(target):
            queue.append(target)

        # ── 4. functools.wraps chain (`__wrapped__`) ─────────────────────
        wrapped = getattr(current, "__wrapped__", None)
        if callable(wrapped):
            queue.append(wrapped)

        # ── 5. Other common wrapper attributes ───────────────────────────
        for attr in _ATTR_CANDIDATES:
            val = getattr(current, attr, None)
            if callable(val):
                queue.append(val)

        # ── 6. Objects with a user-defined __call__ method ───────────────
        call_attr = getattr(current, "__call__", None)
        if (
            callable(call_attr)
            and inspect.isfunction(call_attr)
            and _is_user_code(getattr(call_attr.__code__, "co_filename", ""))
        ):
            queue.append(call_attr)

        # ── 7. Closure cells inside functions / inner scopes ─────────────
        code_obj = getattr(current, "__code__", None)
        clos = getattr(current, "__closure__", None)
        if code_obj and clos:
            for cell in clos:
                cell_val = cell.cell_contents
                if callable(cell_val):
                    queue.append(cell_val)

    # Fallback: return the original callable (likely framework code)
    return fn


# 2b.  Exception-capture tool  (runs *after* an error is detected)
def _exception_capture_tool():
    """
    CherryPy calls the ‘before_error_response' hook whenever it is about to
    finalise an error page, regardless of whether the error is a framework
    HTTPError/HTTPRedirect or an uncaught Python exception.
    We tap that hook and forward the traceback to Sailfish.
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_value:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[SFTracingCherryPy]] captured exception: {exc_value!r}",
                log=False,
            )
        custom_excepthook(exc_type, exc_value, exc_tb)


# ------------------------------------------------------------------ #
#  Main patch entry-point
# ------------------------------------------------------------------ #
def patch_cherrypy(routes_to_skip: Optional[List[str]] = None):
    """
    • Propagate SAILFISH_TRACING_HEADER header → ContextVar.
    • Emit one NetworkHop for the first *user* handler frame in each request.
    • Capture **all** CherryPy exceptions (HTTPError, HTTPRedirect, uncaught
      Python errors) and forward them to `custom_excepthook`.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        import cherrypy  # CherryPy may not be installed
    except ImportError:
        return

    # ──────────────────────────────────────────────────────────────────
    # 1.  Header propagation – monkey-patch Application.__call__
    # ──────────────────────────────────────────────────────────────────
    env_key = "HTTP_" + SAILFISH_TRACING_HEADER.upper().replace("-", "_")
    funcspan_key = "HTTP_X_SF3_FUNCTIONSPANCAPTUREOVERRIDE"

    if not getattr(cherrypy.Application, "__sf_hdr_patched__", False):
        orig_call = cherrypy.Application.__call__

        def patched_call(self, environ, start_response):
            # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
            request_path = environ.get("PATH_INFO", "")
            set_current_request_path(request_path)

            # PERFORMANCE: Single-pass header scan (extract both headers in one pass)
            incoming_trace_raw = environ.get(env_key)
            funcspan_override_header = environ.get(funcspan_key)

            # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
            if incoming_trace_raw:
                # Incoming X-Sf3-Rid header provided - use it
                get_or_set_sf_trace_id(
                    incoming_trace_raw, is_associated_with_inbound_request=True
                )
            else:
                # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
                generate_new_trace_id()

            # Optional funcspan override
            if funcspan_override_header:
                try:
                    set_funcspan_override(funcspan_override_header)
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[CherryPy.application_call]] Set function span override from header: {funcspan_override_header}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[CherryPy.application_call]] Failed to set function span override: {e}",
                            log=False,
                        )

            # Initialize outbound base without list/allocs from split()
            try:
                trace_id = get_sf_trace_id()
                if trace_id:
                    s = str(trace_id)
                    i = s.find("/")  # session
                    j = s.find("/", i + 1) if i != -1 else -1  # page
                    if j != -1:
                        base_trace = s[:j]  # "session/page"
                        set_outbound_header_base(
                            base_trace=base_trace,
                            parent_trace_id=s,  # "session/page/uuid"
                            funcspan=funcspan_override_header,
                        )
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[CherryPy.application_call]] Initialized outbound header base (base={base_trace[:16]}...)",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[CherryPy.application_call]] Failed to initialize outbound header base: {e}",
                        log=False,
                    )

            # NOTE: Cleanup moved to _emit_network_hop_tool() to ensure trace_id is available for emission
            return orig_call(self, environ, start_response)

        cherrypy.Application.__call__ = patched_call
        cherrypy.Application.__sf_hdr_patched__ = True

    # ──────────────────────────────────────────────────────────────────
    # 2a.  OTEL-STYLE: Capture endpoint metadata and request data before handler
    # ──────────────────────────────────────────────────────────────────
    def _capture_endpoint_tool():
        """OTEL-STYLE: Capture endpoint metadata and request data before handler runs."""
        req = cherrypy.serving.request  # thread-local current request
        handler = getattr(req, "handler", None)
        if not callable(handler):
            return

        real_fn = _unwrap_user_func(handler)
        # Skip GraphQL (Strawberry) or non-user code
        if real_fn.__module__.startswith("strawberry"):
            return
        code = getattr(real_fn, "__code__", None)
        if not code or not _is_user_code(code.co_filename):
            return

        hop_key = (code.co_filename, code.co_firstlineno)

        # Get route pattern if available
        route_pattern = req.path_info

        # Check if route should be skipped
        if route_pattern and should_skip_route(route_pattern, _ROUTES_TO_SKIP):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[CherryPy]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                    log=False,
                )
            return

        # Get or register endpoint
        endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
        if endpoint_id is None:
            endpoint_id = register_endpoint(
                line=str(code.co_firstlineno),
                column="0",
                name=real_fn.__name__,
                entrypoint=code.co_filename,
                route=route_pattern,
            )
            if endpoint_id >= 0:
                _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[CherryPy]] Registered endpoint: {real_fn.__name__} @ {code.co_filename}:{code.co_firstlineno} (id={endpoint_id})",
                        log=False,
                    )

        # Store endpoint_id for emission after handler
        req._sf_endpoint_id = endpoint_id

        # Capture request headers if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
            try:
                req_headers = dict(req.headers)
                req._sf_request_headers = req_headers
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[CherryPy]] Captured request headers: {len(req_headers)} headers",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[CherryPy]] Failed to capture request headers: {e}",
                        log=False,
                    )

        # Capture request body if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # CherryPy: request.body is a RequestBody object with a read() method
                # Reading the body consumes it, but CherryPy caches it in request.body.fp
                # First try to get cached body, otherwise read it
                if hasattr(req.body, "fp") and hasattr(req.body.fp, "read"):
                    # Save current position
                    current_pos = req.body.fp.tell()
                    req.body.fp.seek(0)
                    body = req.body.fp.read(_REQUEST_LIMIT_BYTES)
                    # Restore position so handler can read it
                    req.body.fp.seek(current_pos)
                else:
                    # Fallback: read directly (this consumes the body)
                    body = req.body.read(_REQUEST_LIMIT_BYTES)

                if body:
                    req._sf_request_body = body
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[CherryPy]] Request body capture: {len(body)} bytes (method={req.method})",
                            log=False,
                        )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[CherryPy]] Failed to capture request body: {e}", log=False
                    )

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[CherryPy]] Captured endpoint: {real_fn.__name__} "
                f"({code.co_filename}:{code.co_firstlineno}) endpoint_id={endpoint_id}",
                log=False,
            )

    # OTEL-STYLE: Emit network hop AFTER handler completes with response data
    def _emit_network_hop_tool():
        """OTEL-STYLE: Emit network hop after handler completes, capturing response data."""
        req = cherrypy.serving.request
        resp = cherrypy.serving.response
        endpoint_id = getattr(req, "_sf_endpoint_id", None)

        if endpoint_id is not None and endpoint_id >= 0:
            # try:
            # OPTIMIZATION: Use get_sf_trace_id() directly instead of get_or_set_sf_trace_id()
            # Trace ID is GUARANTEED to be set at request start in patched_call
            # This saves ~11-12μs by avoiding tuple unpacking and conditional logic
            # session_id = get_sf_trace_id() # PREVIOUSLY WAS get_sf_trace_id()
            session_id = get_sf_trace_id()
            if session_id is None:
                return  # No trace_id available, skip emission
            # C extension expects string, not UUID object
            session_id = str(session_id)

            # Get captured request data
            req_headers = getattr(req, "_sf_request_headers", None)
            req_body = getattr(req, "_sf_request_body", None)

            # Capture response headers if enabled
            resp_headers = None
            if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                try:
                    resp_headers = dict(resp.headers)
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[CherryPy]] Captured response headers: {len(resp_headers)} headers",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[CherryPy]] Failed to capture response headers: {e}",
                            log=False,
                        )

            # Capture response body if enabled
            resp_body = None
            if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                try:
                    # CherryPy response.body is a list of byte strings
                    if resp.body:
                        if isinstance(resp.body, list):
                            body_bytes = b"".join(resp.body)
                        elif isinstance(resp.body, bytes):
                            body_bytes = resp.body
                        elif isinstance(resp.body, str):
                            body_bytes = resp.body.encode("utf-8")
                        else:
                            # Try to iterate
                            body_bytes = b"".join(
                                (b if isinstance(b, bytes) else str(b).encode("utf-8"))
                                for b in resp.body
                            )

                        if body_bytes:
                            resp_body = body_bytes[:_RESPONSE_LIMIT_BYTES]
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[CherryPy]] Captured response body: {len(resp_body)} bytes",
                                    log=False,
                                )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[CherryPy]] Failed to capture response body: {e}",
                            log=False,
                        )

            # Extract raw path and query string for C to parse
            raw_path = req.path_info  # e.g., "/log"
            raw_query = (
                req.query_string.encode("utf-8") if req.query_string else b""
            )  # e.g., b"foo=5"

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[CherryPy]] About to emit network hop: endpoint_id={endpoint_id}, "
                    f"raw_path={raw_path}, ",
                    f"raw_query_string={raw_query}, ",
                    f"req_headers={'present' if req_headers else 'None'}, "
                    f"req_body={len(req_body) if req_body else 0} bytes, "
                    f"resp_headers={'present' if resp_headers else 'None'}, "
                    f"resp_body={len(resp_body) if resp_body else 0} bytes",
                    log=False,
                )

            # Direct C call - queues to background worker, returns instantly
            # C will parse route and query_params from raw data
            fast_send_network_hop_fast(
                session_id=session_id,
                endpoint_id=endpoint_id,
                raw_path=raw_path,
                raw_query_string=raw_query,
                request_headers=req_headers,
                request_body=req_body,
                response_headers=resp_headers,
                response_body=resp_body,
            )

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[CherryPy]] Emitted network hop: endpoint_id={endpoint_id} "
                    f"session={session_id}",
                    log=False,
                )
            # except Exception as e:  # noqa: BLE001 S110
            #     if SF_DEBUG and app_config._interceptors_initialized:
            #         print(f"[[CherryPy]] Failed to emit network hop: {e}", log=False)

        # CRITICAL: Clear C TLS to prevent stale data in thread pools
        # This cleanup MUST happen AFTER emission, not in patched_call's finally block
        # because on_end_request hook runs AFTER the WSGI __call__ returns
        clear_c_tls_parent_trace_id()

        # CRITICAL: Clear outbound header base to prevent stale cached headers
        # ContextVar does NOT automatically clean up in thread pools - must clear explicitly
        clear_outbound_header_base()

        # CRITICAL: Clear trace_id to ensure fresh generation for next request
        # Without this, get_or_set_sf_trace_id() reuses trace_id from previous request
        # causing X-Sf4-Prid to stay constant when no incoming X-Sf3-Rid header
        clear_trace_id()

        # CRITICAL: Clear current request path to prevent stale data in thread pools
        clear_current_request_path()

        # Clear function span override for this request (thread-local cleanup)
        try:
            _sffuncspan_config.clear_thread_override()
        except Exception:
            pass

    if not hasattr(cherrypy.tools, "sf_capture_endpoint"):
        cherrypy.tools.sf_capture_endpoint = cherrypy.Tool(
            "before_handler", _capture_endpoint_tool, priority=5
        )

    if not hasattr(cherrypy.tools, "sf_emit_network_hop"):
        cherrypy.tools.sf_emit_network_hop = cherrypy.Tool(
            "on_end_resource",
            _emit_network_hop_tool,
            priority=5,
            # "on_end_request", _emit_network_hop_tool, priority=5
        )

    # ──────────────────────────────────────────────────────────────────
    # 2b.  Exception-capture tool  (runs before error response)
    # ──────────────────────────────────────────────────────────────────
    def _exception_capture_tool():
        exc_type, exc_value, exc_tb = sys.exc_info()
        if exc_value:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[SFTracingCherryPy]] captured exception: {exc_value!r}",
                    log=False,
                )
            custom_excepthook(exc_type, exc_value, exc_tb)

    if not hasattr(cherrypy.tools, "sf_exception_capture"):
        cherrypy.tools.sf_exception_capture = cherrypy.Tool(
            "before_error_response", _exception_capture_tool, priority=100
        )

    # ──────────────────────────────────────────────────────────────────
    # 3.  Enable all tools globally
    # ──────────────────────────────────────────────────────────────────
    cherrypy.config.update(
        {
            "tools.sf_capture_endpoint.on": True,
            "tools.sf_emit_network_hop.on": True,
            "tools.sf_exception_capture.on": True,
        }
    )

    # ──────────────────────────────────────────────────────────────────
    # 4️⃣  Ensure every new Application inherits the tool settings
    # ──────────────────────────────────────────────────────────────────
    if not getattr(cherrypy.Application, "__sf_app_patched__", False):
        orig_app_init = cherrypy.Application.__init__

        def patched_app_init(self, root, script_name="", config=None):
            config = config or {}
            root_conf = config.setdefault("/", {})
            root_conf.setdefault("tools.sf_capture_endpoint.on", True)
            root_conf.setdefault("tools.sf_emit_network_hop.on", True)
            root_conf.setdefault("tools.sf_exception_capture.on", True)
            orig_app_init(self, root, script_name, config)

        cherrypy.Application.__init__ = patched_app_init
        cherrypy.Application.__sf_app_patched__ = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_cherrypy]] OTEL-style NetworkHop & Exception tools globally enabled",
            log=False,
        )

    # ── CORS patching ──────────────────────────────────────────────────
    patch_cherrypy_cors()


def patch_cherrypy_cors():
    """
    Patch CherryPy's Response to automatically inject Sailfish headers into CORS.

    SAFE: Only modifies Access-Control-Allow-Headers if the application sets it.
    CherryPy doesn't have a standard CORS library, so we patch Response to intercept
    header setting.
    """
    try:
        import cherrypy
        from cherrypy._cprequest import Response
        from cherrypy.lib.httputil import HeaderMap
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_cherrypy_cors]] CherryPy not available, skipping", log=False)
        return

    # Check if already patched (use Response class directly, not thread-local proxy)
    if hasattr(Response, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_cherrypy_cors]] Already patched, skipping", log=False)
        return

    # Patch HeaderMap.__setitem__ to intercept header setting
    # CherryPy uses HeaderMap for response headers
    original_headers_setitem = HeaderMap.__setitem__

    def patched_headers_setitem(self, name, value):
        # Intercept Access-Control-Allow-Headers header
        if name.lower() == "access-control-allow-headers":
            if should_inject_headers(value):
                injected = inject_sailfish_headers(value)
                # Convert list back to comma-separated string for CherryPy
                if isinstance(injected, list):
                    value = ", ".join(injected)
                else:
                    value = injected
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_cherrypy_cors]] Injected Sailfish headers into Access-Control-Allow-Headers: {value}",
                        log=False,
                    )

        # Call original __setitem__
        return original_headers_setitem(self, name, value)

    HeaderMap.__setitem__ = patched_headers_setitem
    Response._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_cherrypy_cors]] Successfully patched CherryPy Response headers",
            log=False,
        )

    # ── Patch cherrypy-cors library if installed ────────────────────────
    try:
        import cherrypy_cors
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_cherrypy_cors]] cherrypy-cors not installed, skipping library patch",
                log=False,
            )
        return

    # Check if already patched
    if hasattr(cherrypy_cors, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_cherrypy_cors]] cherrypy-cors already patched, skipping",
                log=False,
            )
        return

    # Patch the CORS class's _add_prefligt_headers method
    try:
        from cherrypy_cors import CORS

        original_add_preflight = CORS._add_prefligt_headers

        def patched_add_preflight(self, allowed_methods, max_age):
            # Call original to set up basic headers
            original_add_preflight(self, allowed_methods, max_age)

            # Now intercept and enhance the Access-Control-Allow-Headers if it was set
            rh = self.resp_headers
            CORS_ALLOW_HEADERS = "Access-Control-Allow-Headers"

            if CORS_ALLOW_HEADERS in rh:
                current_value = rh[CORS_ALLOW_HEADERS]
                if should_inject_headers(current_value):
                    injected = inject_sailfish_headers(current_value)
                    # Convert list back to comma-separated string
                    if isinstance(injected, list):
                        rh[CORS_ALLOW_HEADERS] = ", ".join(injected)
                    else:
                        rh[CORS_ALLOW_HEADERS] = injected

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[patch_cherrypy_cors]] Injected Sailfish headers into cherrypy-cors CORS_ALLOW_HEADERS: {rh[CORS_ALLOW_HEADERS]}",
                            log=False,
                        )

        CORS._add_prefligt_headers = patched_add_preflight
        cherrypy_cors._sf_cors_patched = True

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_cherrypy_cors]] Successfully patched cherrypy-cors library",
                log=False,
            )
    except Exception as e:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[patch_cherrypy_cors]] Failed to patch cherrypy-cors: {e}",
                log=False,
            )
