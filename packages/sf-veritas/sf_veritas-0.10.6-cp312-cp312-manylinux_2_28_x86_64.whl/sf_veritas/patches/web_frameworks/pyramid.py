import inspect
import sys
import sysconfig
from functools import lru_cache
from typing import Any, Callable, List, Optional, Set, Tuple

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
from .utils import _is_user_code, should_skip_route  # cached helpers

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Routes to skip (set by patch_pyramid)
_ROUTES_TO_SKIP = []


# ------------------------------------------------------------------ #
# 1.2 Tween factory: header + one-shot profile tracer + exceptions   #
# ------------------------------------------------------------------ #
def _sf_tracing_tween_factory(handler, registry):
    """
    OTEL-STYLE Pyramid tween that:
      • Reads SAILFISH_TRACING_HEADER header → ContextVar.
      • Captures request headers and body when enabled.
      • Sets a one-shot profiler to capture endpoint metadata and pre-register endpoint.
      • Captures response headers and body when enabled.
      • Emits NetworkHop AFTER handler completes (OTEL-style zero-overhead).
      • Funnels *all* exceptions (including HTTPException) through
        `custom_excepthook` before letting Pyramid continue normal handling.
    """

    def _tween(request):
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(request.path)

        # ── 1) Propagate incoming trace header ──────────────────────────
        # PERFORMANCE: Single-pass bytes-level header scan (matching FastAPI pattern)
        hdr = request.headers.get(SAILFISH_TRACING_HEADER)
        funcspan_override_header = request.headers.get(
            "X-Sf3-FunctionSpanCaptureOverride"
        )

        # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        if hdr:
            get_or_set_sf_trace_id(hdr, is_associated_with_inbound_request=True)
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # Check for function span capture override header (highest priority!)
        if funcspan_override_header:
            try:
                set_funcspan_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid.tween]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid.tween]] Failed to set function span override: {e}",
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
                            f"[[Pyramid.tween]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Pyramid.tween]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # ── 2) Capture request headers if enabled ────────────────────────
        req_headers = None
        if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
            try:
                req_headers = dict(request.headers)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid]] Captured request headers: {len(req_headers)} headers",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid]] Failed to capture request headers: {e}", log=False
                    )

        # ── 3) Capture request body if enabled ────────────────────────────
        req_body = None
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # Pyramid: request.body gives bytes
                body = request.body
                if body:
                    req_body = body[:_REQUEST_LIMIT_BYTES]
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Pyramid]] Request body capture: {len(req_body)} bytes",
                            log=False,
                        )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Pyramid]] Failed to capture request body: {e}", log=False)

        # ── 4) OTEL-STYLE: One-shot tracer to capture endpoint metadata and pre-register ──
        endpoint_id = None

        def tracer(frame, event, _arg):
            nonlocal endpoint_id
            if event != "call":  # only Python calls
                return tracer
            fn_path = frame.f_code.co_filename
            if _is_user_code(fn_path):
                # Skip Strawberry GraphQL handlers
                try:
                    fn_module = frame.f_globals.get("__name__", "")
                    if fn_module.startswith("strawberry"):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Pyramid]] Skipping endpoint (Strawberry GraphQL handler): {fn_module}",
                                log=False,
                            )
                        sys.setprofile(None)
                        return None
                except Exception:
                    pass

                hop_key = (fn_path, frame.f_lineno)

                # Get route pattern if available
                route_pattern = request.path

                # Check if route should be skipped
                if route_pattern and should_skip_route(route_pattern, _ROUTES_TO_SKIP):
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Pyramid]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                            log=False,
                        )
                    sys.setprofile(None)
                    return None

                # Pre-register endpoint if not already registered
                endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
                if endpoint_id is None:
                    endpoint_id = register_endpoint(
                        line=str(frame.f_lineno),
                        column="0",
                        name=frame.f_code.co_name,
                        entrypoint=fn_path,
                        route=route_pattern,
                    )
                    if endpoint_id >= 0:
                        _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Pyramid]] Registered endpoint: {frame.f_code.co_name} @ "
                                f"{fn_path}:{frame.f_lineno} (id={endpoint_id})",
                                log=False,
                            )

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid]] Captured endpoint: {frame.f_code.co_name} "
                        f"({fn_path}:{frame.f_lineno}) endpoint_id={endpoint_id}",
                        log=False,
                    )

                sys.setprofile(None)  # disable after first capture
                return None
            return tracer

        sys.setprofile(tracer)

        # ── 5) Call downstream handler & capture **all** exceptions ─────
        try:
            response = handler(request)
        except Exception as exc:  # HTTPException included
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise  # re-raise for Pyramid
        finally:
            sys.setprofile(None)  # safety-net cleanup

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

        # ── 6) Capture response headers if enabled ────────────────────────
        resp_headers = None
        if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
            try:
                resp_headers = dict(response.headers)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid]] Captured response headers: {len(resp_headers)} headers",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid]] Failed to capture response headers: {e}",
                        log=False,
                    )

        # ── 7) Capture response body if enabled ────────────────────────────
        resp_body = None
        if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
            try:
                # Pyramid: response.body gives bytes (or use app_iter for streaming)
                if hasattr(response, "body"):
                    body = response.body
                    if body:
                        resp_body = body[:_RESPONSE_LIMIT_BYTES]
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Pyramid]] Captured response body: {len(resp_body)} bytes",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid]] Failed to capture response body: {e}", log=False
                    )

        # ── 8) OTEL-STYLE: Emit network hop AFTER handler completes ─────
        if endpoint_id is not None and endpoint_id >= 0:
            try:
                _, session_id = get_or_set_sf_trace_id()

                # Extract raw path and query string for C to parse
                raw_path = request.path  # e.g., "/log"
                raw_query = (
                    request.query_string.encode("utf-8")
                    if request.query_string
                    else b""
                )  # e.g., b"foo=5"

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Pyramid]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                        f"[[Pyramid]] Emitted network hop: endpoint_id={endpoint_id} "
                        f"session={session_id}",
                        log=False,
                    )
            except Exception as e:  # noqa: BLE001 S110
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Pyramid]] Failed to emit network hop: {e}", log=False)

        return response

    return _tween


# ------------------------------------------------------------------ #
# 1.3 Monkey-patch Configurator to auto-add our tween               #
# ------------------------------------------------------------------ #
def patch_pyramid(routes_to_skip: Optional[List[str]] = None):
    """
    Ensure every Pyramid Configurator implicitly registers our tween
    at the INVOCATION stage (just above MAIN).
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        import pyramid.config
        import pyramid.tweens
    except ImportError:
        return  # Pyramid not installed

    original_init = pyramid.config.Configurator.__init__

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Use a dotted name—implicit ordering places it just above MAIN
        dotted = f"{_sf_tracing_tween_factory.__module__}._sf_tracing_tween_factory"
        # 'over=pyramid.tweens.MAIN' ensures our tween runs *before* the main handler
        self.add_tween(dotted, over=pyramid.tweens.MAIN)

    pyramid.config.Configurator.__init__ = patched_init

    # ---- CORS patching --------------------------------------------------------
    patch_pyramid_cors()


def patch_pyramid_cors():
    """
    Patch Pyramid's Response to automatically inject Sailfish headers into CORS.

    SAFE: Only modifies Access-Control-Allow-Headers if the application sets it.
    Pyramid doesn't have a standard CORS library built-in, but users often use
    pyramid-cors or set headers manually. We patch Response.headerlist to intercept.
    """
    try:
        from pyramid.response import Response
        from webob.headers import ResponseHeaders
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_pyramid_cors]] Pyramid Response not available, skipping",
                log=False,
            )
        return

    # Check if already patched
    if hasattr(ResponseHeaders, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_pyramid_cors]] Already patched, skipping", log=False)
        return

    # Patch ResponseHeaders.__setitem__ to intercept header setting
    # Pyramid uses WebOb's ResponseHeaders for response.headers
    original_setitem = ResponseHeaders.__setitem__

    def patched_setitem(self, name, value):
        # Intercept Access-Control-Allow-Headers header
        if name.lower() == "access-control-allow-headers":
            if should_inject_headers(value):
                injected = inject_sailfish_headers(value)
                # CRITICAL: Convert list back to comma-separated string for WSGI
                # WSGI requires header values to be strings, not lists
                if isinstance(injected, list):
                    value = ", ".join(injected)
                else:
                    value = injected
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_pyramid_cors]] Injected Sailfish headers into Access-Control-Allow-Headers: {value}",
                        log=False,
                    )

        # Call original __setitem__
        return original_setitem(self, name, value)

    ResponseHeaders.__setitem__ = patched_setitem
    ResponseHeaders._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_pyramid_cors]] Successfully patched Pyramid ResponseHeaders.__setitem__",
            log=False,
        )
