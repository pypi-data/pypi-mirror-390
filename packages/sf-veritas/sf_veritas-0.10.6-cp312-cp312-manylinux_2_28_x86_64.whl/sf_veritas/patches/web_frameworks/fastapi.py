"""
OTEL-STYLE PURE ASYNC PATTERN:
• Call C extension directly AFTER response sent
• C queues to lock-free ring buffer and returns in ~1µs
• ASGI event loop returns instantly (doesn't wait)
• C background thread does ALL work with GIL released
• This should MATCH OTEL performance (identical pattern)

KEY INSIGHT: No Python threads! C extension handles everything.
"""

import asyncio
import functools
import gc
import json
from typing import Callable, List, Optional

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

try:
    import fastapi
    from starlette.types import ASGIApp, Message, Receive, Scope, Send
except ImportError:

    def patch_fastapi(routes_to_skip: Optional[List[str]] = None):
        return

else:

    # Pre-registered endpoint IDs (maps endpoint function id -> endpoint_id from C extension)
    _ENDPOINT_REGISTRY: dict[int, int] = {}

    # Track which FastAPI app instances have been registered (to support multiple apps)
    _REGISTERED_APPS: set[int] = set()

    def _truncate_if_needed(data: bytes, limit: int) -> bytes:
        """Truncate data to limit if needed."""
        if len(data) <= limit:
            return data
        return data[:limit] + b"... [TRUNCATED]"

    def _serialize_headers(headers: list) -> str:
        """Serialize headers to JSON string (fast path)."""
        try:
            return json.dumps(
                {k.decode(): v.decode() for k, v in headers}, separators=(",", ":")
            )
        except Exception:  # noqa: BLE001
            return "{}"

    class SFZeroOverheadMiddleware:
        """ZERO-OVERHEAD network hop capture middleware.

        OTEL-STYLE PATTERN:
        - Call C extension directly AFTER send completes
        - C queues message and returns in ~1µs (lock-free ring buffer)
        - C background thread does ALL network work with GIL released
        - ASGI event loop never blocks!

        This matches OTEL's performance because we use the same pattern!
        """

        def __init__(self, app: ASGIApp):
            self.app = app

        async def __call__(self, scope: Scope, receive: Receive, send: Send):
            if scope.get("type") != "http":
                await self.app(scope, receive, send)
                return

            # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
            request_path = scope.get("path", "")
            set_current_request_path(request_path)

            # Always print to verify middleware is being called
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[SFZeroOverheadMiddleware.__call__]] HTTP request to {request_path}, type={scope.get('type')}",
                    log=False,
                )

            # PERFORMANCE: Single-pass bytes-level header scan (no dict allocation until needed)
            # Scan headers once on bytes, only decode what we need, use latin-1 (fast 1:1 byte map)
            hdr_tuples = scope.get("headers") or ()
            incoming_trace_raw = None  # bytes
            funcspan_raw = None  # bytes
            req_headers = None  # dict[str,str] only if capture enabled

            capture_req_headers = SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache

            if capture_req_headers:
                # decode once using latin-1 (1:1 bytes, faster than utf-8 and never throws)
                tmp = {}
                for k, v in hdr_tuples:
                    kl = k.lower()
                    if kl == SAILFISH_TRACING_HEADER_BYTES:
                        incoming_trace_raw = v
                    elif kl == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                        funcspan_raw = v
                    # build the dict while we're here
                    tmp[k.decode("latin-1")] = v.decode("latin-1")
                req_headers = tmp
            else:
                for k, v in hdr_tuples:
                    kl = k.lower()
                    if kl == SAILFISH_TRACING_HEADER_BYTES:
                        incoming_trace_raw = v
                    elif kl == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                        funcspan_raw = v
                    # no dict build

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
                            f"[[SFZeroOverheadMiddleware]] Set function span override from header: {funcspan_override_header}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[SFZeroOverheadMiddleware]] Failed to set function span override: {e}",
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
                                f"[[SFZeroOverheadMiddleware]] Initialized outbound header base (base={base_trace[:16]}...)",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[SFZeroOverheadMiddleware]] Failed to initialize outbound header base: {e}",
                        log=False,
                    )

            # OPTIMIZATION: Skip ALL capture infrastructure if not capturing network hops
            # We still needed to set up trace_id and outbound header base above (for outbound call tracing)
            # but we can skip all request/response capture overhead
            if not SF_NETWORKHOP_CAPTURE_ENABLED:
                await self.app(scope, receive, send)
                return

            # NOTE: req_headers already captured in single-pass scan above (if enabled)

            # Capture request body if enabled (must intercept receive)
            req_body_chunks = []

            # OPTIMIZATION: Only wrap receive if we need to capture request body
            if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:

                async def wrapped_receive():
                    message = await receive()
                    if message["type"] == "http.request":
                        body = message.get("body", b"")
                        if body:
                            req_body_chunks.append(body)
                    return message

            else:
                wrapped_receive = receive

            # Capture response headers and body if enabled
            resp_headers = None
            resp_body_chunks = []

            # OPTIMIZATION: Cache debug flag check (avoid repeated lookups)
            _debug_enabled = SF_DEBUG and app_config._interceptors_initialized

            # OPTIMIZATION: Cache capture flags (avoid repeated global lookups in hot path)
            _capture_resp_headers = SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS
            _capture_resp_body = SF_NETWORKHOP_CAPTURE_RESPONSE_BODY

            async def wrapped_send(message: Message):
                nonlocal resp_headers

                # ULTRA-FAST PATH: Most messages just pass through without any processing
                # Only http.response.body (final) triggers network hop collection
                msg_type = message.get("type")

                # FAST PATH: Early exit for non-body messages (http.response.start, etc.)
                if msg_type != "http.response.body":
                    # Capture response headers if needed (only on http.response.start)
                    if _capture_resp_headers and msg_type == "http.response.start":
                        try:
                            resp_headers = {
                                k.decode(): v.decode()
                                for k, v in message.get("headers", [])
                            }
                        except Exception:
                            pass
                    await send(message)
                    return

                # BODY PATH: Capture body chunks if needed
                if _capture_resp_body:
                    body = message.get("body", b"")
                    if body:
                        resp_body_chunks.append(body)

                # Send the actual message first
                await send(message)

                # OPTIMIZATION: Early exit if there's more body chunks coming
                if message.get("more_body", False):
                    return

                # NOW we can get the endpoint (it's been populated by the router)
                endpoint_fn = scope.get("endpoint")
                if not endpoint_fn:
                    return  # Early exit if no endpoint

                endpoint_id = _ENDPOINT_REGISTRY.get(id(endpoint_fn))
                if endpoint_id is None or endpoint_id < 0:
                    if _debug_enabled:
                        print(
                            f"[[SFZeroOverheadMiddleware]] Skipping NetworkHop (endpoint_id={endpoint_id}), registry has {len(_ENDPOINT_REGISTRY)} endpoints",
                            log=False,
                        )
                    return  # Early exit if invalid endpoint

                if _debug_enabled:
                    print(
                        f"[[SFZeroOverheadMiddleware]] Response complete for {scope.get('path')}, endpoint_fn={endpoint_fn.__name__ if hasattr(endpoint_fn, '__name__') else endpoint_fn}, endpoint_id={endpoint_id}",
                        log=False,
                    )

                # Only proceed if we have valid endpoint
                try:
                    # OPTIMIZATION: Use get_sf_trace_id() directly instead of get_or_set_sf_trace_id()
                    # Trace ID is GUARANTEED to be set at request start (lines 111-118)
                    # This saves ~11-12μs by avoiding tuple unpacking and conditional logic
                    session_id = get_sf_trace_id()

                    # OPTIMIZATION: Consolidate body chunks efficiently
                    req_body = None
                    if req_body_chunks:
                        joined = b"".join(req_body_chunks)
                        req_body = (
                            joined
                            if len(joined) <= _REQUEST_LIMIT_BYTES
                            else joined[:_REQUEST_LIMIT_BYTES]
                        )

                    resp_body = None
                    if resp_body_chunks:
                        joined = b"".join(resp_body_chunks)
                        resp_body = (
                            joined
                            if len(joined) <= _RESPONSE_LIMIT_BYTES
                            else joined[:_RESPONSE_LIMIT_BYTES]
                        )

                    # Direct C call - it queues to background worker, returns instantly
                    # No need to check SF_NETWORKHOP_CAPTURE_ENABLED - we return early if it's False (line 170)
                    fast_send_network_hop_fast(
                        session_id=session_id,
                        endpoint_id=endpoint_id,
                        raw_path=scope["path"],
                        raw_query_string=scope["query_string"],
                        request_headers=req_headers,
                        request_body=req_body,
                        response_headers=resp_headers,
                        response_body=resp_body,
                    )
                    if _debug_enabled:
                        print(
                            f"[[SFZeroOverheadMiddleware]] Emitted NetworkHop for endpoint_id={endpoint_id}",
                            log=False,
                        )
                except Exception as e:  # noqa: BLE001 S110
                    if _debug_enabled:
                        print(
                            f"[[SFZeroOverheadMiddleware]] Failed to emit NetworkHop: {e}",
                            log=False,
                        )

            try:
                await self.app(scope, wrapped_receive, wrapped_send)
            except Exception as exc:  # noqa: BLE001
                custom_excepthook(type(exc), exc, exc.__traceback__)
                raise
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

    def _should_trace_endpoint(endpoint_fn: Callable) -> bool:
        """Check if endpoint should be traced."""
        if getattr(endpoint_fn, _SKIP_TRACING_ATTR, False):
            return False

        code = getattr(endpoint_fn, "__code__", None)
        if not code:
            return False

        filename = code.co_filename
        if not _is_user_code(filename):
            return False

        if getattr(endpoint_fn, "__module__", "").startswith("strawberry"):
            return False

        return True

    def _pre_register_endpoints(
        app: "fastapi.FastAPI", routes_to_skip: Optional[List[str]] = None
    ):
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
                f"[[_pre_register_endpoints]] Starting registration for app {app_id}, app has {len(app.routes)} routes",
                log=False,
            )

        for route in app.routes:
            if not hasattr(route, "endpoint"):
                skipped += 1
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[_pre_register_endpoints]] Skipping route (no endpoint): {route}",
                        log=False,
                    )
                continue

            original_endpoint = route.endpoint
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

            # Extract route pattern (e.g., "/log/{n}")
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
                    f"[[patch_fastapi]] Registered: {name} @ {filename}:{line_no_str} route={route_pattern} (endpoint_fn_id={endpoint_fn_id}, endpoint_id={endpoint_id})",
                    log=False,
                )

        if SF_DEBUG and app_config._interceptors_initialized:
            print(f"[[patch_fastapi]] Total endpoints registered: {count}", log=False)

        # Only mark this app as registered if we actually registered user endpoints
        # This allows retry on startup event if routes weren't ready yet
        if count > 0:
            _REGISTERED_APPS.add(app_id)
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[patch_fastapi]] App {app_id} marked as registered", log=False)
                print(
                    f"[[patch_fastapi]] OTEL-STYLE: Pure async, direct C call (no Python threads)",
                    log=False,
                )
                print(
                    f"[[patch_fastapi]] Request headers capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS else 'DISABLED'}",
                    log=False,
                )
                print(
                    f"[[patch_fastapi]] Request body capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_REQUEST_BODY else 'DISABLED'}",
                    log=False,
                )
                print(
                    f"[[patch_fastapi]] Response headers capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS else 'DISABLED'}",
                    log=False,
                )
                print(
                    f"[[patch_fastapi]] Response body capture: {'ENABLED' if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY else 'DISABLED'}",
                    log=False,
                )
                print(
                    f"[[patch_fastapi]] C extension queues to background worker with GIL released",
                    log=False,
                )
        else:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_fastapi]] No user endpoints registered yet for app {app_id}, will retry on startup",
                    log=False,
                )

    def patch_fastapi(routes_to_skip: Optional[List[str]] = None):
        """
        OTEL-STYLE PURE ASYNC:
        • Direct C call IMMEDIATELY after send completes
        • ASGI returns instantly (C queues and returns in ~1µs)
        • C background thread does all network work with GIL released
        • This is TRUE zero overhead!
        """
        routes_to_skip = routes_to_skip or []

        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_fastapi]] Patching FastAPI.__init__", log=False)

        original_init = fastapi.FastAPI.__init__

        def patched_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_fastapi]] FastAPI app created: {self.__class__.__name__}",
                    log=False,
                )

            # Install zero-overhead middleware
            self.add_middleware(SFZeroOverheadMiddleware)

            # Try to register endpoints immediately if routes are already defined
            # This handles apps where routes are defined before __init__ completes
            if hasattr(self, "routes") and self.routes:
                try:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[patch_fastapi]] Routes already defined ({len(self.routes)} routes), registering immediately",
                            log=False,
                        )
                    _pre_register_endpoints(self, routes_to_skip)
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[patch_fastapi]] Immediate registration failed: {e}",
                            log=False,
                        )

            # Also register on startup event as a fallback (for routes added after __init__)
            @self.on_event("startup")
            async def _sf_startup():
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[patch_fastapi]] Startup event fired, registering endpoints",
                        log=False,
                    )
                # _pre_register_endpoints now checks if this app was already registered
                _pre_register_endpoints(self, routes_to_skip)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[patch_fastapi]] ZERO-OVERHEAD pattern activated (truly async, no blocking)",
                        log=False,
                    )

        fastapi.FastAPI.__init__ = patched_init

        # Also patch any existing FastAPI instances that were created before patching
        # This handles the case where app = FastAPI() happens before setup_interceptors()
        for obj in gc.get_objects():
            try:
                # Wrap in try-except to safely handle lazy objects (e.g., Django settings)
                # that trigger initialization on attribute access
                if isinstance(obj, fastapi.FastAPI):
                    # Check if this app already has our middleware
                    has_our_middleware = any(
                        m.__class__.__name__ == "SFZeroOverheadMiddleware"
                        for m in getattr(obj, "user_middleware", [])
                    )
                    if not has_our_middleware:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[patch_fastapi]] Retroactively patching existing FastAPI app",
                                log=False,
                            )
                        obj.add_middleware(SFZeroOverheadMiddleware)

                        # Try immediate registration if routes exist
                        if obj.routes:
                            try:
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[patch_fastapi]] Retroactive immediate registration ({len(obj.routes)} routes)",
                                        log=False,
                                    )
                                _pre_register_endpoints(obj, routes_to_skip)
                            except Exception as e:
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[patch_fastapi]] Retroactive immediate registration failed: {e}",
                                        log=False,
                                    )

                        @obj.on_event("startup")
                        async def _sf_startup_retro():
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    "[[patch_fastapi]] Retroactive startup event fired",
                                    log=False,
                                )
                            # _pre_register_endpoints now checks if this app was already registered
                            _pre_register_endpoints(obj, routes_to_skip)
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    "[[patch_fastapi]] Retroactive registration complete",
                                    log=False,
                                )
            except Exception:
                # Silently skip objects that fail isinstance checks (e.g., Django lazy settings)
                pass

    def patch_fastapi_cors():
        """
        Patch Starlette's CORSMiddleware to automatically inject Sailfish headers.

        SAFE: Only modifies CORS if CORSMiddleware is used by the application.
        This works for both FastAPI and Starlette apps.
        """
        try:
            from starlette.middleware.cors import CORSMiddleware
        except ImportError:
            # Starlette not installed, skip patching
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_fastapi_cors]] Starlette CORSMiddleware not found, skipping",
                    log=False,
                )
            return

        # Check if already patched
        if hasattr(CORSMiddleware, "_sf_cors_patched"):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("[[patch_fastapi_cors]] Already patched, skipping", log=False)
            return

        original_cors_init = CORSMiddleware.__init__

        def patched_cors_init(
            self,
            app,
            allow_origins=(),
            allow_methods=(),
            allow_headers=(),
            allow_credentials=False,
            allow_origin_regex=None,
            expose_headers=(),
            max_age=600,
        ):
            # Intercept allow_headers parameter
            if should_inject_headers(allow_headers):
                allow_headers = inject_sailfish_headers(allow_headers)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[patch_fastapi_cors]] Injected Sailfish headers into CORSMiddleware",
                        log=False,
                    )

            # Call original init with potentially modified headers
            original_cors_init(
                self,
                app,
                allow_origins=allow_origins,
                allow_methods=allow_methods,
                allow_headers=allow_headers,
                allow_credentials=allow_credentials,
                allow_origin_regex=allow_origin_regex,
                expose_headers=expose_headers,
                max_age=max_age,
            )

        CORSMiddleware.__init__ = patched_cors_init
        CORSMiddleware._sf_cors_patched = True

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_fastapi_cors]] Successfully patched Starlette CORSMiddleware",
                log=False,
            )

    # Call CORS patching
    patch_fastapi_cors()
