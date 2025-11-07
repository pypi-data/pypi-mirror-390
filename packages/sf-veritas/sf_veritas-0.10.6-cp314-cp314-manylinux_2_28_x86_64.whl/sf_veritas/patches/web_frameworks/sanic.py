"""
OTEL-STYLE PURE ASYNC PATTERN:
• Call C extension directly AFTER response sent
• C queues to lock-free ring buffer and returns in ~1µs
• ASGI event loop returns instantly (doesn't wait)
• C background thread does ALL work with GIL released
• This should MATCH OTEL performance (identical pattern)

KEY INSIGHT: No Python threads! C extension handles everything.
"""

import gc
import inspect
from collections import defaultdict
from threading import Lock
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
    SF_NETWORKHOP_CAPTURE_ENABLED,
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

_SKIP_TRACING_ATTR = "_sf_skip_tracing"

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# OTEL-STYLE: No thread pool! Pure async, call C extension directly
# C extension has its own background worker thread

# Pre-registered endpoint IDs (maps endpoint function id -> endpoint_id from C extension)
_ENDPOINT_REGISTRY: dict[int, int] = {}

# Track which Sanic app instances have been registered (to support multiple apps)
_REGISTERED_APPS: set[int] = set()

# Request data storage (keyed by request id)
_request_data_lock = Lock()
_request_data = defaultdict(dict)


def _should_trace_endpoint(endpoint_fn) -> bool:
    """Check if endpoint should be traced."""
    if getattr(endpoint_fn, _SKIP_TRACING_ATTR, False):
        return False

    code = getattr(endpoint_fn, "__code__", None)
    if not code:
        return False

    filename = code.co_filename
    if not _is_user_code(filename):
        return False

    # Skip Strawberry GraphQL handlers
    if getattr(endpoint_fn, "__module__", "").startswith("strawberry"):
        return False

    return True


def _pre_register_endpoints(app, routes_to_skip: Optional[List[str]] = None):
    """Pre-register all endpoints at startup."""
    routes_to_skip = routes_to_skip or []
    count = 0
    skipped = 0

    app_id = id(app)

    # Check if this app has already been registered
    if app_id in _REGISTERED_APPS:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[_pre_register_endpoints]] App {app_id} already registered, skipping",
                log=False,
            )
        return

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            f"[[_pre_register_endpoints]] Starting registration for app {app_id}, app has {len(app.router.routes)} routes",
            log=False,
        )

    # Iterate through all routes in the Sanic router
    for route in app.router.routes:
        if not hasattr(route, "handler"):
            skipped += 1
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_pre_register_endpoints]] Skipping route (no handler): {route}",
                    log=False,
                )
            continue

        original_endpoint = route.handler
        endpoint_fn_id = id(original_endpoint)

        # Check if this specific endpoint function is already registered
        if endpoint_fn_id in _ENDPOINT_REGISTRY:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_pre_register_endpoints]] Endpoint function {original_endpoint.__name__ if hasattr(original_endpoint, '__name__') else original_endpoint} already registered (id={_ENDPOINT_REGISTRY[endpoint_fn_id]}), skipping",
                    log=False,
                )
            continue

        # Check for @skip_network_tracing on the wrapped function BEFORE unwrapping
        if getattr(original_endpoint, _SKIP_TRACING_ATTR, False):
            skipped += 1
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_pre_register_endpoints]] Skipping endpoint (marked with @skip_network_tracing): {original_endpoint.__name__ if hasattr(original_endpoint, '__name__') else original_endpoint}",
                    log=False,
                )
            continue

        unwrapped = _unwrap_user_func(original_endpoint)

        if not _should_trace_endpoint(unwrapped):
            skipped += 1
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_pre_register_endpoints]] Skipping endpoint (not user code): {unwrapped.__name__ if hasattr(unwrapped, '__name__') else unwrapped}",
                    log=False,
                )
            continue

        code = unwrapped.__code__
        line_no_str = str(code.co_firstlineno)
        name = unwrapped.__name__
        filename = code.co_filename

        # Extract route pattern from Sanic route (e.g., "/log/<n>")
        route_pattern = getattr(route, "path", None)

        # Check if route should be skipped based on wildcard patterns
        if should_skip_route(route_pattern, routes_to_skip):
            skipped += 1
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_pre_register_endpoints]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                    log=False,
                )
            continue

        endpoint_id = register_endpoint(
            line=line_no_str,
            column="0",
            name=name,
            entrypoint=filename,
            route=route_pattern,
        )

        if endpoint_id < 0:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_pre_register_endpoints]] Failed to register {name} (endpoint_id={endpoint_id})",
                    log=False,
                )
            continue

        _ENDPOINT_REGISTRY[endpoint_fn_id] = endpoint_id
        count += 1

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[patch_sanic]] Registered: {name} @ {filename}:{line_no_str} route={route_pattern} (endpoint_fn_id={endpoint_fn_id}, endpoint_id={endpoint_id})",
                log=False,
            )

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            f"[[patch_sanic]] Total endpoints registered: {count}, skipped: {skipped}",
            log=False,
        )

    # Only mark this app as registered if we actually registered user endpoints
    # This allows retry on startup event if routes weren't ready yet
    if count > 0:
        _REGISTERED_APPS.add(app_id)
        if SF_DEBUG and app_config._interceptors_initialized:
            print(f"[[patch_sanic]] App {app_id} marked as registered", log=False)
            print(
                f"[[patch_sanic]] OTEL-STYLE: Pure async, direct C call (no Python threads)",
                log=False,
            )
            print(
                f"[[patch_sanic]] Request headers capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS else 'DISABLED'}",
                log=False,
            )
            print(
                f"[[patch_sanic]] Request body capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_REQUEST_BODY else 'DISABLED'}",
                log=False,
            )
            print(
                f"[[patch_sanic]] Response headers capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS else 'DISABLED'}",
                log=False,
            )
            print(
                f"[[patch_sanic]] Response body capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY else 'DISABLED'}",
                log=False,
            )
            print(
                f"[[patch_sanic]] C extension queues to background worker with GIL released",
                log=False,
            )
    else:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[patch_sanic]] No user endpoints registered yet for app {app_id}, will retry on startup",
                log=False,
            )


def patch_sanic(routes_to_skip: Optional[List[str]] = None):
    """
    OTEL-STYLE PURE ASYNC:
    • Direct C call IMMEDIATELY after response completes
    • Sanic returns instantly (C queues and returns in ~1µs)
    • C background thread does all network work with GIL released
    • This is TRUE zero overhead!
    """
    routes_to_skip = routes_to_skip or []

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_sanic]] patching sanic...", log=False)

    try:
        from sanic import Sanic
    except ImportError:
        return

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_sanic]] Patching Sanic.__init__", log=False)

    orig_init = Sanic.__init__

    def patched_init(self, *args, **kwargs):
        """
        After the original Sanic app is created we attach:
        • request middleware – capture header propagation + request headers/body
        • response middleware – emit NetworkHop with response headers/body
        • universal exception handler – capture all exceptions
        """
        # Let Sanic build the app normally
        orig_init(self, *args, **kwargs)

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[patch_sanic]] patched_init called - about to register middleware",
                log=False,
            )

        # 1. Request middleware: header propagation + request capture
        async def _capture_request(request):
            # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
            set_current_request_path(request.path)

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Sanic]] _capture_request called for {request.method} {request.path}",
                    log=False,
                )
            try:
                # PERFORMANCE: Single-pass bytes-level header scan (no dict allocation until needed)
                # Scan headers once, only decode what we need, use latin-1 (fast 1:1 byte map)
                incoming_trace_raw = None  # bytes
                funcspan_raw = None  # bytes
                req_headers = None  # dict[str,str] only if capture enabled

                capture_req_headers = (
                    SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache
                )

                # Sanic headers are already decoded strings, so we work with them directly
                # Convert to lowercase for comparison
                if capture_req_headers:
                    req_headers = dict(request.headers)
                    # Extract special headers
                    for k, v in request.headers.items():
                        k_lower = k.lower()
                        if k_lower == SAILFISH_TRACING_HEADER.lower():
                            incoming_trace_raw = v
                        elif k_lower == "x-sf3-functionspancaptureoverride":
                            funcspan_raw = v
                else:
                    # Just extract special headers
                    for k, v in request.headers.items():
                        k_lower = k.lower()
                        if k_lower == SAILFISH_TRACING_HEADER.lower():
                            incoming_trace_raw = v
                        elif k_lower == "x-sf3-functionspancaptureoverride":
                            funcspan_raw = v

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
                funcspan_override_header = funcspan_raw
                if funcspan_override_header:
                    try:
                        set_funcspan_override(funcspan_override_header)
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Sanic]] Set function span override from header: {funcspan_override_header}",
                                log=False,
                            )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Sanic]] Failed to set function span override: {e}",
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
                                    f"[[Sanic]] Initialized outbound header base (base={base_trace[:16]}...)",
                                    log=False,
                                )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Sanic]] Failed to initialize outbound header base: {e}",
                            log=False,
                        )

                # OPTIMIZATION: Skip ALL capture infrastructure if not capturing network hops
                # We still needed to set up trace_id and outbound header base above (for outbound call tracing)
                # but we can skip all request/response capture overhead
                if not SF_NETWORKHOP_CAPTURE_ENABLED:
                    return

                # Use request id as key for storing data
                req_id = id(request)

                # Store captured request headers (already captured in single-pass scan above if enabled)
                if req_headers:
                    with _request_data_lock:
                        _request_data[req_id]["headers"] = req_headers
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Sanic]] Captured request headers: {len(req_headers)} headers",
                            log=False,
                        )

                # Capture request body if enabled
                if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
                    try:
                        # Sanic request.body is available as bytes
                        body = request.body
                        if body:
                            req_body = body[:_REQUEST_LIMIT_BYTES]
                            with _request_data_lock:
                                _request_data[req_id]["body"] = req_body
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Sanic]] Request body capture: {len(req_body)} bytes (method={request.method})",
                                    log=False,
                                )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Sanic]] Failed to capture request body: {e}",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Sanic]] Request middleware error: {e}", log=False)

        try:
            self.register_middleware(_capture_request, attach_to="request")
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_sanic]] Successfully registered request middleware",
                    log=False,
                )
        except TypeError:  # Sanic<22 compatibility
            self.register_middleware(_capture_request, "request")
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_sanic]] Successfully registered request middleware (legacy)",
                    log=False,
                )

        # 2. Response middleware: OTEL-STYLE NetworkHop emission with response capture
        async def _emit_hop(request, response):
            """
            OTEL-STYLE: Emit network hop in response middleware.
            In Sanic, response middleware runs after handler but before send.
            """
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Sanic]] _emit_hop called for {request.method} {request.path}",
                    log=False,
                )
            req_id = id(request)
            try:
                handler = getattr(request, "route", None)
                if not handler:
                    return
                fn = getattr(handler, "handler", None)
                if not fn:
                    return

                # Use the pre-registered endpoint ID
                endpoint_id = _ENDPOINT_REGISTRY.get(id(fn))
                if endpoint_id is None or endpoint_id < 0:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Sanic]] Skipping NetworkHop (endpoint not registered or endpoint_id={endpoint_id})",
                            log=False,
                        )
                    return

                if endpoint_id is not None and endpoint_id >= 0:
                    try:
                        # OPTIMIZATION: Use get_sf_trace_id() directly instead of get_or_set_sf_trace_id()
                        # Trace ID is GUARANTEED to be set at request start
                        # This saves ~11-12μs by avoiding tuple unpacking and conditional logic
                        session_id = get_sf_trace_id()

                        # Get captured request data
                        req_headers = None
                        req_body = None
                        with _request_data_lock:
                            req_data = _request_data.get(req_id, {})
                            req_headers = req_data.get("headers")
                            req_body = req_data.get("body")

                        # Capture response headers if enabled
                        resp_headers = None
                        if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS and response:
                            try:
                                # Sanic response.headers is a dict-like object
                                resp_headers = dict(response.headers)
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Sanic]] Captured response headers: {len(resp_headers)} headers",
                                        log=False,
                                    )
                            except Exception as e:
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Sanic]] Failed to capture response headers: {e}",
                                        log=False,
                                    )

                        # Capture response body if enabled
                        resp_body = None
                        if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY and response:
                            try:
                                # Sanic response.body is bytes
                                if hasattr(response, "body") and response.body:
                                    if isinstance(response.body, bytes):
                                        resp_body = response.body[
                                            :_RESPONSE_LIMIT_BYTES
                                        ]
                                        if (
                                            SF_DEBUG
                                            and app_config._interceptors_initialized
                                        ):
                                            print(
                                                f"[[Sanic]] Captured response body: {len(resp_body)} bytes",
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
                                                f"[[Sanic]] Captured response body (str): {len(resp_body)} bytes",
                                                log=False,
                                            )
                            except Exception as e:
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Sanic]] Failed to capture response body: {e}",
                                        log=False,
                                    )

                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Sanic]] About to emit network hop: endpoint_id={endpoint_id}, "
                                f"req_headers={'present' if req_headers else 'None'}, "
                                f"req_body={len(req_body) if req_body else 0} bytes, "
                                f"resp_headers={'present' if resp_headers else 'None'}, "
                                f"resp_body={len(resp_body) if resp_body else 0} bytes",
                                log=False,
                            )

                        # Direct C call - queues to background worker, returns instantly
                        # Extract route and query params from request
                        raw_path = request.path
                        raw_query = (
                            request.query_string.encode("utf-8")
                            if request.query_string
                            else b""
                        )

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
                                f"[[Sanic]] Emitted network hop: endpoint_id={endpoint_id} "
                                f"session={session_id}",
                                log=False,
                            )
                    except Exception as e:  # noqa: BLE001 S110
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Sanic]] Failed to emit network hop: {e}", log=False
                            )
                    finally:
                        # Clean up request data to prevent memory leak
                        with _request_data_lock:
                            _request_data.pop(req_id, None)

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
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Sanic]] Response middleware error: {e}", log=False)
                # Clean up on error too
                with _request_data_lock:
                    _request_data.pop(req_id, None)

                # CRITICAL: Clear C TLS to prevent stale data in thread pools
                clear_c_tls_parent_trace_id()

                # CRITICAL: Clear outbound header base to prevent stale cached headers
                clear_outbound_header_base()

                # CRITICAL: Clear trace_id to ensure fresh generation for next request
                clear_trace_id()

                # CRITICAL: Clear current request path to prevent stale data in thread pools
                clear_current_request_path()

        try:
            self.register_middleware(_emit_hop, attach_to="response")
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_sanic]] Successfully registered response middleware",
                    log=False,
                )
        except TypeError:
            self.register_middleware(_emit_hop, "response")
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_sanic]] Successfully registered response middleware (legacy)",
                    log=False,
                )

        # 3. Universal exception handler
        async def _capture_exception(request, exception):
            """
            Called for any exception – user errors, abort/HTTPException,
            or Sanic-specific errors. Forward to custom_excepthook
            and then fall back to Sanic's default error handler.
            """
            try:
                custom_excepthook(type(exception), exception, exception.__traceback__)
            except Exception:
                pass  # Don't let exception handler crash

            # Delegate to default handler to keep standard 4xx/5xx payload
            try:
                response = request.app.error_handler.default(request, exception)
                if inspect.isawaitable(response):
                    response = await response
                return response
            except Exception:
                # If default handler fails, just re-raise
                raise exception

        # Register for base Exception class to catch everything
        try:
            self.error_handler.add(Exception, _capture_exception)
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[Sanic]] Failed to register exception handler: {e}", log=False)

        # Try to register endpoints immediately if routes are already defined
        # This handles apps where routes are defined before __init__ completes
        if (
            hasattr(self, "router")
            and hasattr(self.router, "routes")
            and self.router.routes
        ):
            try:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_sanic]] Routes already defined ({len(self.router.routes)} routes), registering immediately",
                        log=False,
                    )
                _pre_register_endpoints(self, routes_to_skip)
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_sanic]] Immediate registration failed: {e}",
                        log=False,
                    )

        # Register on after_server_start event as a fallback (for routes added after __init__)
        @self.listener("after_server_start")
        async def _sf_startup(app, loop):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_sanic]] After server start event fired, registering endpoints",
                    log=False,
                )
            # _pre_register_endpoints now checks if this app was already registered
            _pre_register_endpoints(self, routes_to_skip)
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_sanic]] ZERO-OVERHEAD pattern activated (truly async, no blocking)",
                    log=False,
                )

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_sanic]] OTEL-style middlewares + exception handler installed",
                log=False,
            )

    Sanic.__init__ = patched_init

    # Also patch any existing Sanic instances that were created before patching
    # This handles the case where app = Sanic() happens before setup_interceptors()
    for obj in gc.get_objects():
        try:
            # Wrap in try-except to safely handle lazy objects (e.g., Django settings)
            # that trigger initialization on attribute access
            if isinstance(obj, Sanic):
                # Check if this app already has our middleware
                # In Sanic, middlewares are stored in a list
                has_our_middleware = False
                if hasattr(obj, "middlewares"):
                    # Check if any middleware matches our function names
                    for mw in obj.middlewares:
                        if hasattr(mw, "__name__") and mw.__name__ in (
                            "_capture_request",
                            "_emit_hop",
                        ):
                            has_our_middleware = True
                            break

                if not has_our_middleware:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[patch_sanic]] Retroactively patching existing Sanic app",
                            log=False,
                        )

                    # We can't easily retroactively add middleware to an already-created Sanic app
                    # Just try to register endpoints if they exist
                    if (
                        hasattr(obj, "router")
                        and hasattr(obj.router, "routes")
                        and obj.router.routes
                    ):
                        try:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[patch_sanic]] Retroactive immediate registration ({len(obj.router.routes)} routes)",
                                    log=False,
                                )
                            _pre_register_endpoints(obj, routes_to_skip)
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[patch_sanic]] Retroactive immediate registration failed: {e}",
                                    log=False,
                                )
        except Exception:
            # Silently skip objects that fail isinstance checks (e.g., Django lazy settings)
            pass

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_sanic]] OTEL-style patch applied", log=False)


def patch_sanic_cors():
    """
    Patch Sanic CORS middleware to automatically inject Sailfish headers.

    SAFE: Only modifies CORS if CORSMiddleware is used by the application.
    This works for both sanic-cors and sanic-ext CORS implementations.
    """
    # Try to patch sanic-ext CORS first
    try:
        from sanic_ext.extensions.http.cors import cors

        # Check if already patched
        if hasattr(cors, "_sf_cors_patched"):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_sanic_cors]] sanic-ext already patched, skipping",
                    log=False,
                )
            return

        # Patch the cors configuration function
        original_cors_init = cors.__init__ if hasattr(cors, "__init__") else None

        if original_cors_init:

            def patched_cors_init(self, *args, allow_headers=None, **kwargs):
                # Intercept allow_headers parameter
                if should_inject_headers(allow_headers):
                    allow_headers = inject_sailfish_headers(allow_headers)
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            "[[patch_sanic_cors]] Injected Sailfish headers into sanic-ext CORS",
                            log=False,
                        )

                # Call original init with potentially modified headers
                original_cors_init(self, *args, allow_headers=allow_headers, **kwargs)

            cors.__init__ = patched_cors_init
            cors._sf_cors_patched = True

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_sanic_cors]] Successfully patched sanic-ext CORS",
                    log=False,
                )
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_sanic_cors]] sanic-ext not found, trying sanic-cors",
                log=False,
            )

    # Try to patch sanic-cors
    try:
        from sanic_cors import CORS

        # Check if already patched
        if hasattr(CORS, "_sf_cors_patched"):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_sanic_cors]] sanic-cors already patched, skipping",
                    log=False,
                )
            return

        original_cors_init = CORS.__init__

        def patched_cors_init(self, app=None, *args, allow_headers=None, **kwargs):
            # Intercept allow_headers parameter
            if should_inject_headers(allow_headers):
                allow_headers = inject_sailfish_headers(allow_headers)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[patch_sanic_cors]] Injected Sailfish headers into sanic-cors",
                        log=False,
                    )

            # Call original init with potentially modified headers
            original_cors_init(self, app, *args, allow_headers=allow_headers, **kwargs)

        CORS.__init__ = patched_cors_init
        CORS._sf_cors_patched = True

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_sanic_cors]] Successfully patched sanic-cors",
                log=False,
            )
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_sanic_cors]] sanic-cors not found, skipping CORS patching",
                log=False,
            )


# Call CORS patching
patch_sanic_cors()
