"""
Context-var propagation  +  first-hop NetworkHop emission.
"""

# ------------------------------------------------------------------ #
# Shared helpers (same as Django/FastAPI utils)
# ------------------------------------------------------------------ #
import inspect
import sysconfig
from functools import lru_cache
from typing import Any, Callable, List, Optional, Set, Tuple

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
from .utils import _is_user_code, _unwrap_user_func, should_skip_route

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Routes to skip (set by patch_blacksheep)
_ROUTES_TO_SKIP = []


# ------------------------------------------------------------------ #
# Middleware
# ------------------------------------------------------------------ #
async def _sf_tracing_middleware(request, handler):
    """
    OTEL-STYLE BlackSheep middleware that:
    1. Propagates trace-id from SAILFISH_TRACING_HEADER.
    2. Captures request headers/body if enabled.
    3. Captures endpoint metadata and registers endpoint.
    4. Calls handler and captures exceptions.
    5. Captures response headers/body if enabled.
    6. Emits NetworkHop AFTER handler completes (OTEL-style zero-overhead).
    """
    # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
    request_path = request.url.path if hasattr(request.url, 'path') else str(request.url)
    set_current_request_path(request_path)

    # PERFORMANCE: Single-pass bytes-level header scan (no dict allocation until needed)
    # Scan headers once, only decode what we need, use latin-1 (fast 1:1 byte map)
    # BlackSheep headers are tuples of (bytes, bytes)
    hdr_items = request.headers if hasattr(request.headers, "__iter__") else []
    incoming_trace_raw = None  # bytes
    funcspan_raw = None  # bytes
    req_headers = None  # dict[str,str] only if capture enabled

    capture_req_headers = SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache

    if capture_req_headers:
        # build the dict while we're scanning
        tmp = {}
        for k, v in hdr_items:
            # BlackSheep headers are bytes
            kl = k.lower() if isinstance(k, bytes) else k.encode().lower()
            if kl == SAILFISH_TRACING_HEADER_BYTES:
                incoming_trace_raw = v
            elif kl == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                funcspan_raw = v
            # decode using latin-1 for speed
            tmp[k.decode("latin-1") if isinstance(k, bytes) else k] = (
                v.decode("latin-1") if isinstance(v, bytes) else v
            )
        req_headers = tmp
    else:
        for k, v in hdr_items:
            kl = k.lower() if isinstance(k, bytes) else k.encode().lower()
            if kl == SAILFISH_TRACING_HEADER_BYTES:
                incoming_trace_raw = v
            elif kl == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                funcspan_raw = v

    # 1. CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
    if incoming_trace_raw:
        # Incoming X-Sf3-Rid header provided - use it
        incoming_trace = (
            incoming_trace_raw.decode("latin-1")
            if isinstance(incoming_trace_raw, bytes)
            else str(incoming_trace_raw)
        )
        get_or_set_sf_trace_id(incoming_trace, is_associated_with_inbound_request=True)
    else:
        # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
        generate_new_trace_id()

    # Optional funcspan override (decode only if present)
    funcspan_override_header = None
    if funcspan_raw:
        funcspan_override_header = (
            funcspan_raw.decode("latin-1")
            if isinstance(funcspan_raw, bytes)
            else str(funcspan_raw)
        )
        try:
            set_funcspan_override(funcspan_override_header)
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Blacksheep.middleware]] Set function span override from header: {funcspan_override_header}",
                    log=False,
                )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Blacksheep.middleware]] Failed to set function span override: {e}",
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
                        f"[[Blacksheep.middleware]] Initialized outbound header base (base={base_trace[:16]}...)",
                        log=False,
                    )
    except Exception as e:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[Blacksheep.middleware]] Failed to initialize outbound header base: {e}",
                log=False,
            )

    # 3. Capture request body if enabled
    req_body = None
    if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
        try:
            # BlackSheep provides async read method
            # For GET requests, this will typically be empty
            body = await request.read()
            req_body = body[:_REQUEST_LIMIT_BYTES] if body else None
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Blacksheep]] Request body capture: {len(body) if body else 0} bytes (method={request.method})",
                    log=False,
                )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[Blacksheep]] Failed to capture request body: {e}", log=False)

    # 4. Capture endpoint metadata and register endpoint
    endpoint_id = None
    if not getattr(request, "_sf_hop_sent", False):
        user_fn = _unwrap_user_func(handler)
        if (
            inspect.isfunction(user_fn)
            and _is_user_code(user_fn.__code__.co_filename)
            and not user_fn.__module__.startswith("strawberry")
        ):
            fname = user_fn.__code__.co_filename
            lno = user_fn.__code__.co_firstlineno
            fname_str = user_fn.__name__
            hop_key = (fname, lno)

            # Get route pattern if available
            route_pattern = getattr(request, "route_pattern", None)
            route_str = str(route_pattern) if route_pattern else None

            # Check if route should be skipped
            if route_str and should_skip_route(route_str, _ROUTES_TO_SKIP):
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[BlackSheep]] Skipping endpoint (route matches skip pattern): {route_str}",
                        log=False,
                    )
                return await handler(request)

            # Get or register endpoint
            endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
            if endpoint_id is None:
                endpoint_id = register_endpoint(
                    line=str(lno),
                    column="0",
                    name=fname_str,
                    entrypoint=fname,
                    route=route_str,
                )
                if endpoint_id >= 0:
                    _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Blacksheep]] Registered endpoint: {fname_str} @ {fname}:{lno} (id={endpoint_id})",
                            log=False,
                        )

            request._sf_hop_sent = True
            request._sf_endpoint_id = endpoint_id

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Blacksheep]] Captured endpoint: {fname_str} ({fname}:{lno}) endpoint_id={endpoint_id}",
                    log=False,
                )

    # 5. Call handler and capture exceptions (with cleanup in finally)
    try:
        try:
            response = await handler(request)
        except Exception as exc:  # ← includes HTTPException & friends
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise  # Let BlackSheep build the response

        # 6. Capture response headers if enabled
        resp_headers = None
        if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS and endpoint_id is not None:
            try:
                # BlackSheep response headers are in _headers (list of tuples)
                if hasattr(response, "_headers") and response._headers:
                    resp_headers = {
                        k.decode() if isinstance(k, bytes) else k: (
                            v.decode() if isinstance(v, bytes) else v
                        )
                        for k, v in response._headers
                    }
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Blacksheep]] Captured response headers from _headers: {len(resp_headers)} headers",
                            log=False,
                        )
                elif hasattr(response, "headers") and response.headers:
                    # Fallback to headers property
                    resp_headers = {
                        k.decode() if isinstance(k, bytes) else k: (
                            v.decode() if isinstance(v, bytes) else v
                        )
                        for k, v in response.headers
                    }
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Blacksheep]] Captured response headers from headers: {len(resp_headers)} headers",
                            log=False,
                        )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Blacksheep]] Failed to capture response headers: {e}",
                        log=False,
                    )

        # 7. Capture response body if enabled
        resp_body = None
        if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY and endpoint_id is not None:
            try:
                # BlackSheep response.content is a Content object that needs special handling
                if hasattr(response, "content") and response.content:
                    content_obj = response.content

                    # Check if it's a blacksheep.contents.Content object
                    if hasattr(content_obj, "body"):
                        # Content object has a body attribute
                        if isinstance(content_obj.body, bytes):
                            resp_body = content_obj.body[:_RESPONSE_LIMIT_BYTES]
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Blacksheep]] Captured from content.body (bytes): {len(resp_body)} bytes",
                                    log=False,
                                )
                        elif isinstance(content_obj.body, str):
                            resp_body = content_obj.body.encode("utf-8")[
                                :_RESPONSE_LIMIT_BYTES
                            ]
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Blacksheep]] Captured from content.body (str): {len(resp_body)} bytes",
                                    log=False,
                                )
                    elif isinstance(content_obj, bytes):
                        resp_body = content_obj[:_RESPONSE_LIMIT_BYTES]
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Blacksheep]] Captured from content (bytes): {len(resp_body)} bytes",
                                log=False,
                            )
                    elif isinstance(content_obj, str):
                        resp_body = content_obj.encode("utf-8")[:_RESPONSE_LIMIT_BYTES]
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Blacksheep]] Captured from content (str): {len(resp_body)} bytes",
                                log=False,
                            )

                # Fallback: try direct body attribute
                if not resp_body and hasattr(response, "body") and response.body:
                    if isinstance(response.body, bytes):
                        resp_body = response.body[:_RESPONSE_LIMIT_BYTES]
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Blacksheep]] Captured from body (bytes): {len(resp_body)} bytes",
                                log=False,
                            )
                    elif isinstance(response.body, str):
                        resp_body = response.body.encode("utf-8")[
                            :_RESPONSE_LIMIT_BYTES
                        ]
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Blacksheep]] Captured from body (str): {len(resp_body)} bytes",
                                log=False,
                            )

                if SF_DEBUG and not resp_body:
                    print(
                        f"[[Blacksheep]] No response body captured (content type: {type(response.content) if hasattr(response, 'content') else 'N/A'})",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Blacksheep]] Failed to capture response body: {e}",
                        log=False,
                    )

        # 8. OTEL-STYLE: Emit network hop AFTER handler completes
        if endpoint_id is not None and endpoint_id >= 0:
            try:
                _, session_id = get_or_set_sf_trace_id()

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Blacksheep]] About to emit network hop: endpoint_id={endpoint_id}, "
                        f"req_headers={'present' if req_headers else 'None'}, "
                        f"req_body={len(req_body) if req_body else 0} bytes, "
                        f"resp_headers={'present' if resp_headers else 'None'}, "
                        f"resp_body={len(resp_body) if resp_body else 0} bytes",
                        log=False,
                    )

                # Direct C call - queues to background worker, returns instantly
                # Extract route and query params from request
                # BlackSheep's request.url.path returns bytes, need to decode to string
                path_value = (
                    request.url.path
                    if hasattr(request.url, "path")
                    else str(request.url)
                )
                raw_path = (
                    path_value.decode("utf-8")
                    if isinstance(path_value, bytes)
                    else path_value
                )

                # Handle None/empty from request.url.query (when no query string)
                raw_query_value = (
                    request.url.query if hasattr(request.url, "query") else None
                )
                if raw_query_value is None or raw_query_value == "":
                    raw_query = b""
                elif isinstance(raw_query_value, bytes):
                    raw_query = raw_query_value
                else:
                    raw_query = raw_query_value.encode("utf-8")

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
                        f"[[Blacksheep]] Emitted network hop: endpoint_id={endpoint_id} "
                        f"session={session_id}",
                        log=False,
                    )
            except Exception as e:  # noqa: BLE001 S110
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Blacksheep]] Failed to emit network hop: {e}", log=False)

        return response
    finally:
        # CRITICAL: Clear C TLS to prevent stale data in thread pools
        # This runs even if handler raises exception!
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


# ------------------------------------------------------------------ #
# Monkey-patch Application.__init__
# ------------------------------------------------------------------ #
def patch_blacksheep(routes_to_skip: Optional[List[str]] = None):
    """
    Injects the tracing middleware into every BlackSheep Application.
    Safe no-op if BlackSheep isn't installed or already patched.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        from blacksheep import Application
    except ImportError:
        return

    if getattr(Application, "__sf_tracing_patched__", False):
        return  # already patched

    original_init = Application.__init__

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Put our middleware first so we run before user middlewares
        self.middlewares.insert(0, _sf_tracing_middleware)

    Application.__init__ = patched_init
    Application.__sf_tracing_patched__ = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_blacksheep]] tracing middleware installed", log=False)

    # ── CORS patching ──────────────────────────────────────────────────
    patch_blacksheep_cors()


def patch_blacksheep_cors():
    """
    Patch BlackSheep's Application.use_cors to automatically inject Sailfish headers.

    SAFE: Only modifies allow_headers if the application sets it.
    Similar to Flask CORS patching - intercepts the configuration before it's applied.
    """
    try:
        from blacksheep import Application
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_blacksheep_cors]] BlackSheep Application not available, skipping",
                log=False,
            )
        return

    # Check if already patched
    if hasattr(Application, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_blacksheep_cors]] Already patched, skipping", log=False)
        return

    # Patch Application.use_cors to intercept and modify allow_headers parameter
    original_use_cors = Application.use_cors

    def patched_use_cors(self, *args, **kwargs):
        # Intercept allow_headers parameter
        if "allow_headers" in kwargs:
            original_headers = kwargs["allow_headers"]
            if should_inject_headers(original_headers):
                kwargs["allow_headers"] = inject_sailfish_headers(original_headers)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_blacksheep_cors]] Injected Sailfish headers into use_cors: {original_headers} -> {kwargs['allow_headers']}",
                        log=False,
                    )

        # Call original use_cors with potentially modified headers
        return original_use_cors(self, *args, **kwargs)

    Application.use_cors = patched_use_cors
    Application._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_blacksheep_cors]] Successfully patched BlackSheep Application.use_cors",
            log=False,
        )
