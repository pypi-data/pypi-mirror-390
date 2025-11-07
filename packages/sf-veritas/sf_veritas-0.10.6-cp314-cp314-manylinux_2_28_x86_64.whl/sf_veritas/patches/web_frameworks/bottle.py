from typing import List, Optional

from ... import app_config
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
from .utils import _is_user_code, _unwrap_user_func, should_skip_route  # cached helpers

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Module-level variable for routes to skip (set by patch_bottle)
_ROUTES_TO_SKIP = []


# ------------------------------------------------------------------------------------
# 1. Hop-capturing plugin ----------------------------------------------------------------
# ------------------------------------------------------------------------------------
class _SFTracingPlugin:
    """Bottle plugin (API v2) – wraps each route callback exactly once."""

    name = "sf_network_hop"
    api = 2

    def apply(self, callback, route):
        # 1. Resolve real user function
        real_fn = _unwrap_user_func(callback)
        mod = real_fn.__module__
        code = getattr(real_fn, "__code__", None)

        # 2. Skip library frames and Strawberry GraphQL handlers
        if (
            not code
            or not _is_user_code(code.co_filename)
            or mod.startswith("strawberry")
        ):
            return callback  # no wrapping

        filename, line_no, fn_name = (
            code.co_filename,
            code.co_firstlineno,
            real_fn.__name__,
        )
        hop_key = (filename, line_no)

        # Get route pattern from route object
        route_pattern = getattr(route, "rule", None) if route else None

        # Check if route should be skipped
        if should_skip_route(route_pattern, _ROUTES_TO_SKIP):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Bottle]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                    log=False,
                )
            return callback  # no wrapping

        # Pre-register endpoint
        endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
        if endpoint_id is None:
            endpoint_id = register_endpoint(
                line=str(line_no),
                column="0",
                name=fn_name,
                entrypoint=filename,
                route=route_pattern,
            )
            if endpoint_id >= 0:
                _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Bottle]] Registered endpoint: {fn_name} @ {filename}:{line_no} (id={endpoint_id})",
                        log=False,
                    )

        # 3. Wrapper that stores endpoint_id for after_request hook
        from bottle import request  # local to avoid hard dep

        def _wrapped(*args, **kwargs):  # noqa: ANN001
            sent = request.environ.setdefault("_sf_hops_sent", set())
            if hop_key not in sent:
                # OTEL-STYLE: Store endpoint_id for after_request hook
                request.environ["_sf_endpoint_id"] = endpoint_id
                sent.add(hop_key)

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Bottle]] Captured endpoint: {fn_name} ({filename}:{line_no}) endpoint_id={endpoint_id}",
                        log=False,
                    )

            return callback(*args, **kwargs)

        return _wrapped


# ------------------------------------------------------------------------------------
# 2. Request hooks: before (header + body capture) + after (OTEL-style emission) ----
# ------------------------------------------------------------------------------------
def _install_request_hooks(app):
    from bottle import request, response

    @app.hook("before_request")
    def _extract_sf_trace_and_capture_request():
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(request.path)

        # PERFORMANCE: Single-pass bytes-level header scan (no dict allocation until needed)
        # Scan headers once, only decode what we need, use latin-1 (fast 1:1 byte map)
        incoming_trace_raw = None  # bytes
        funcspan_raw = None  # bytes
        req_headers = None  # dict[str,str] only if capture enabled

        capture_req_headers = SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache

        # Convert Bottle headers to list of tuples for scanning
        # Bottle request.headers is a WSGIHeaderDict, iterate over items
        if capture_req_headers:
            # decode once using latin-1 (1:1 bytes, faster than utf-8 and never throws)
            tmp = {}
            for k, v in request.headers.items():
                k_bytes = k.lower().encode("latin-1")
                v_bytes = v.encode("latin-1")
                if k_bytes == SAILFISH_TRACING_HEADER_BYTES:
                    incoming_trace_raw = v_bytes
                elif k_bytes == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                    funcspan_raw = v_bytes
                # build the dict while we're here
                tmp[k] = v
            req_headers = tmp
            request.environ["_sf_request_headers"] = req_headers
        else:
            for k, v in request.headers.items():
                k_bytes = k.lower().encode("latin-1")
                if k_bytes == SAILFISH_TRACING_HEADER_BYTES:
                    incoming_trace_raw = v.encode("latin-1")
                elif k_bytes == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                    funcspan_raw = v.encode("latin-1")
                # no dict build
            request.environ["_sf_request_headers"] = None

        # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        if incoming_trace_raw:
            # Incoming X-Sf3-Rid header provided - use it
            incoming_trace = incoming_trace_raw.decode("latin-1")
            get_or_set_sf_trace_id(
                incoming_trace, is_associated_with_inbound_request=True
            )
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # Optional funcspan override (decode only if present)
        funcspan_override_header = (
            funcspan_raw.decode("latin-1") if funcspan_raw else None
        )
        if funcspan_override_header:
            try:
                set_funcspan_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Bottle.before_request]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Bottle.before_request]] Failed to set function span override: {e}",
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
                            f"[[Bottle.before_request]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Bottle.before_request]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # Capture request body if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # Bottle request.body is a cached property
                body = request.body.read(_REQUEST_LIMIT_BYTES)
                request.environ["_sf_request_body"] = body if body else None
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Bottle]] Request body capture: {len(body) if body else 0} bytes (method={request.method})",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Bottle]] Failed to capture request body: {e}", log=False)
                request.environ["_sf_request_body"] = None
        else:
            request.environ["_sf_request_body"] = None

    @app.hook("after_request")
    def _emit_network_hop():
        """
        OTEL-STYLE: Emit network hop AFTER response is built.
        Bottle's after_request hook runs after the handler completes.
        Captures response headers/body if enabled.
        """
        try:
            endpoint_id = request.environ.get("_sf_endpoint_id")
            if endpoint_id is not None and endpoint_id >= 0:
                try:
                    _, session_id = get_or_set_sf_trace_id()

                    # Get captured request data
                    req_headers = request.environ.get("_sf_request_headers")
                    req_body = request.environ.get("_sf_request_body")

                    # Capture response headers if enabled
                    resp_headers = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                        try:
                            resp_headers = dict(response.headers)
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Bottle]] Captured response headers: {len(resp_headers)} headers",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Bottle]] Failed to capture response headers: {e}",
                                    log=False,
                                )

                    # Capture response body if enabled
                    resp_body = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                        try:
                            # Bottle response.body is bytes
                            if hasattr(response, "body") and response.body:
                                if isinstance(response.body, bytes):
                                    resp_body = response.body[:_RESPONSE_LIMIT_BYTES]
                                    if (
                                        SF_DEBUG
                                        and app_config._interceptors_initialized
                                    ):
                                        print(
                                            f"[[Bottle]] Captured from body (bytes): {len(resp_body)} bytes",
                                            log=False,
                                        )
                                elif isinstance(response.body, str):
                                    resp_body = response.body.encode("utf-8")[
                                        :_RESPONSE_LIMIT_BYTES
                                    ]
                                    if (
                                        SF_DEBUG
                                        and app_config._interceptors_initialized
                                    ):
                                        print(
                                            f"[[Bottle]] Captured from body (str): {len(resp_body)} bytes",
                                            log=False,
                                        )
                                elif isinstance(response.body, list):
                                    # Body is a list of bytes
                                    resp_body = b"".join(response.body)[
                                        :_RESPONSE_LIMIT_BYTES
                                    ]
                                    if (
                                        SF_DEBUG
                                        and app_config._interceptors_initialized
                                    ):
                                        print(
                                            f"[[Bottle]] Captured from body (list): {len(resp_body)} bytes",
                                            log=False,
                                        )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Bottle]] Failed to capture response body: {e}",
                                    log=False,
                                )

                    # Extract raw path and query string for C to parse
                    raw_path = request.path  # e.g., "/log"
                    raw_query = (
                        request.query_string.encode("utf-8")
                        if request.query_string
                        else b""
                    )  # e.g., b"foo=5"

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Bottle]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                            f"[[Bottle]] Emitted network hop: endpoint_id={endpoint_id} "
                            f"session={session_id}",
                            log=False,
                        )
                except Exception as e:  # noqa: BLE001 S110
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(f"[[Bottle]] Failed to emit network hop: {e}", log=False)
        finally:
            # CRITICAL: Clear C TLS to prevent stale data in thread pools
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


# ------------------------------------------------------------------------------------
# NEW: Global error-handler wrapper for Bottle
# ------------------------------------------------------------------------------------
def _install_error_handler(app):
    """
    Replace ``app.default_error_handler`` so *any* exception or HTTPError
    (including those raised via ``abort()`` or ``HTTPError(status=500)``)
    is reported to ``custom_excepthook`` before Bottle builds the response.

    Bottle always funnels errors through this function, regardless of debug
    mode. See Bottle docs on *Error Handlers*.
    """
    original_handler = app.default_error_handler

    def _sf_error_handler(error):
        # Forward full traceback (HTTPError keeps it on .__traceback__)
        custom_excepthook(type(error), error, getattr(error, "__traceback__", None))
        return original_handler(error)

    app.default_error_handler = _sf_error_handler


# ------------------------------------------------------------------------------------
# 3. Public patch function – call this once at startup
# ------------------------------------------------------------------------------------
def patch_bottle(routes_to_skip: Optional[List[str]] = None):
    """
    • Adds before_request header propagation + body/header capture.
    • Installs NetworkHop plugin (covers all current & future routes).
    • Installs after_request hook for OTEL-style network hop emission.
    • Wraps default_error_handler so exceptions (incl. HTTPError 500) are captured.
    Safe no-op if Bottle is not installed or already patched.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        import bottle
    except ImportError:  # Bottle absent
        return

    if getattr(bottle.Bottle, "__sf_tracing_patched__", False):
        return

    # ---- patch Bottle.__init__ ----------------------------------------------------
    original_init = bottle.Bottle.__init__

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # OTEL-STYLE: Install request hooks (before + after)
        _install_request_hooks(self)

        # Install hop plugin (Plugin API v2 ― applies to all routes, past & future)
        self.install(_SFTracingPlugin())

        # Exception capture (HTTPError 500 or any uncaught Exception)
        _install_error_handler(self)

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_bottle]] OTEL-style hooks + plugin + error handler installed",
                log=False,
            )

    bottle.Bottle.__init__ = patched_init
    bottle.Bottle.__sf_tracing_patched__ = True

    # ---- CORS patching --------------------------------------------------------
    patch_bottle_cors()


def patch_bottle_cors():
    """
    Patch Bottle's Response to automatically inject Sailfish headers into CORS.

    SAFE: Only modifies Access-Control-Allow-Headers if the application sets it.
    Bottle doesn't have a standard CORS library, so we patch Response.set_header
    to intercept and modify CORS headers.
    """
    try:
        import bottle
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_bottle_cors]] Bottle not available, skipping", log=False)
        return

    # Check if already patched
    if hasattr(bottle.Response, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_bottle_cors]] Already patched, skipping", log=False)
        return

    # Patch Response.set_header to intercept and modify Access-Control-Allow-Headers
    original_set_header = bottle.Response.set_header

    def patched_set_header(self, name, value):
        # Intercept Access-Control-Allow-Headers header
        if name.lower() == "access-control-allow-headers":
            if should_inject_headers(value):
                value = inject_sailfish_headers(value)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[patch_bottle_cors]] Injected Sailfish headers into Access-Control-Allow-Headers",
                        log=False,
                    )

        # Call original set_header
        return original_set_header(self, name, value)

    bottle.Response.set_header = patched_set_header
    bottle.Response._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_bottle_cors]] Successfully patched Bottle Response.set_header",
            log=False,
        )
