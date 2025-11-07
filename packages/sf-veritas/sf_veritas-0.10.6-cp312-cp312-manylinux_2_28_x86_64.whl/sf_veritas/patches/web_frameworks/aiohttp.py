"""
Context-propagation + user-code NetworkHop emission for every aiohttp
request, while skipping Strawberry GraphQL views.

OTEL-STYLE: Emits network hops AFTER handler completes (zero-overhead).
"""

from typing import List, Optional

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

# LAZY IMPORT: Import inside function to avoid circular import with _sfnetworkhop
# from ...fast_network_hop import fast_send_network_hop_fast, register_endpoint
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

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs (maps (filename, lineno) tuple -> endpoint_id from C extension)
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Track which aiohttp app instances have been registered (to support multiple apps)
_REGISTERED_APPS: set[int] = set()

# Routes to skip (set by patch_aiohttp)
_ROUTES_TO_SKIP = []

# ------------------------------------------------------------------ #
# shared helpers
# ------------------------------------------------------------------ #
from .utils import _is_user_code, _unwrap_user_func, should_skip_route  # cached


def _should_trace_endpoint(handler) -> bool:
    """Check if endpoint should be traced."""
    real_fn = _unwrap_user_func(handler)
    if not callable(real_fn):
        return False

    if getattr(real_fn, "__module__", "").startswith("strawberry"):
        return False

    code = getattr(real_fn, "__code__", None)
    if not code:
        return False

    if not _is_user_code(code.co_filename):
        return False

    return True


def _pre_register_endpoints(app, routes_to_skip: Optional[List[str]] = None):
    """Pre-register all endpoints at startup."""
    # LAZY IMPORT: Import here to avoid circular import with _sfnetworkhop
    from ...fast_network_hop import register_endpoint

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
            f"[[_pre_register_endpoints]] Starting registration for app {app_id}",
            log=False,
        )

    # Iterate through all routes in the router
    if not hasattr(app, "router") or not hasattr(app.router, "_resources"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[_pre_register_endpoints]] App has no router or resources, skipping",
                log=False,
            )
        return

    for resource in app.router._resources:
        if not hasattr(resource, "_routes"):
            continue

        for route in resource._routes:
            if not hasattr(route, "_handler"):
                skipped += 1
                continue

            handler = route._handler
            if not _should_trace_endpoint(handler):
                skipped += 1
                continue

            unwrapped = _unwrap_user_func(handler)
            code = unwrapped.__code__
            key = (code.co_filename, code.co_firstlineno)

            # Check if this specific endpoint is already registered
            if key in _ENDPOINT_REGISTRY:
                continue

            # Extract route pattern
            route_pattern = None
            if hasattr(resource, "_path"):
                route_pattern = resource._path
            elif hasattr(resource, "canonical"):
                route_pattern = resource.canonical

            # Check if route should be skipped based on wildcard patterns
            if route_pattern and should_skip_route(route_pattern, routes_to_skip):
                skipped += 1
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[_pre_register_endpoints]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                        log=False,
                    )
                continue

            endpoint_id = register_endpoint(
                line=str(code.co_firstlineno),
                column="0",
                name=unwrapped.__name__,
                entrypoint=code.co_filename,
                route=route_pattern,
            )

            if endpoint_id < 0:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[_pre_register_endpoints]] Failed to register {unwrapped.__name__} (endpoint_id={endpoint_id})",
                        log=False,
                    )
                continue

            _ENDPOINT_REGISTRY[key] = endpoint_id
            count += 1

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_aiohttp]] Registered: {unwrapped.__name__} @ {code.co_filename}:{code.co_firstlineno} route={route_pattern} (endpoint_id={endpoint_id})",
                    log=False,
                )

    if SF_DEBUG and app_config._interceptors_initialized:
        print(f"[[patch_aiohttp]] Total endpoints registered: {count}", log=False)

    # Only mark this app as registered if we actually registered user endpoints
    if count > 0:
        _REGISTERED_APPS.add(app_id)
        if SF_DEBUG and app_config._interceptors_initialized:
            print(f"[[patch_aiohttp]] App {app_id} marked as registered", log=False)
    else:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[patch_aiohttp]] No user endpoints registered yet for app {app_id}",
                log=False,
            )


# ------------------------------------------------------------------ #
# monkey-patch
# ------------------------------------------------------------------ #
def patch_aiohttp(routes_to_skip: Optional[List[str]] = None):
    """
    OTEL-STYLE PURE ASYNC:
    • Prepends middleware that propagates SAILFISH_TRACING_HEADER
    • Captures endpoint metadata before handler
    • Emits NetworkHop AFTER handler completes (zero-overhead)
    • Patches Application.add_route(s) for RouteTableDef support
    Safe no-op if aiohttp isn't installed.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        from aiohttp import web
    except ImportError:  # aiohttp missing
        return

    # ===========================================================
    # 1 | OTEL-STYLE Middleware
    # ===========================================================
    @web.middleware
    async def _sf_tracing_middleware(request: web.Request, handler):
        """
        OTEL-STYLE aiohttp middleware that:
        1 - Seed ContextVar from the inbound SAILFISH_TRACING_HEADER header.
        2 - Capture request headers/body if enabled.
        3 - Captures endpoint metadata and register endpoint.
        4 - Call handler and capture exceptions.
        5 - Capture response headers/body if enabled.
        6 - Emits NetworkHop AFTER handler completes (OTEL-style zero-overhead).
        """
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(request.path)

        # LAZY IMPORT: Import here to avoid circular import with _sfnetworkhop
        from ...fast_network_hop import fast_send_network_hop_fast, register_endpoint

        # PERFORMANCE: Single-pass bytes-level header scan (no dict allocation until needed)
        # Scan headers once on bytes, only decode what we need, use latin-1 (fast 1:1 byte map)
        # aiohttp uses CIMultiDict for headers, need to iterate raw tuples
        hdr_items = request.headers.items() if hasattr(request.headers, "items") else []
        incoming_trace_raw = None  # bytes or str
        funcspan_raw = None  # bytes or str
        req_headers = None  # dict[str,str] only if capture enabled

        capture_req_headers = SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache

        if capture_req_headers:
            # build the dict while we're scanning
            tmp = {}
            for k, v in hdr_items:
                # aiohttp headers are already strings, check as string first
                if isinstance(k, str):
                    kl = k.lower()
                    if kl == SAILFISH_TRACING_HEADER.lower():
                        incoming_trace_raw = v
                    elif kl == "x-sf3-functionspancaptureoverride":
                        funcspan_raw = v
                    tmp[k] = v
                else:
                    # fallback for bytes
                    kl = k.lower() if isinstance(k, bytes) else k.encode().lower()
                    if kl == SAILFISH_TRACING_HEADER_BYTES:
                        incoming_trace_raw = v
                    elif kl == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                        funcspan_raw = v
                    tmp[k.decode("latin-1") if isinstance(k, bytes) else k] = (
                        v.decode("latin-1") if isinstance(v, bytes) else v
                    )
            req_headers = tmp
        else:
            for k, v in hdr_items:
                if isinstance(k, str):
                    kl = k.lower()
                    if kl == SAILFISH_TRACING_HEADER.lower():
                        incoming_trace_raw = v
                    elif kl == "x-sf3-functionspancaptureoverride":
                        funcspan_raw = v
                else:
                    kl = k.lower() if isinstance(k, bytes) else k.encode().lower()
                    if kl == SAILFISH_TRACING_HEADER_BYTES:
                        incoming_trace_raw = v
                    elif kl == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                        funcspan_raw = v

        # 1. CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        if incoming_trace_raw:
            # Incoming X-Sf3-Rid header provided - use it
            incoming_trace = (
                incoming_trace_raw
                if isinstance(incoming_trace_raw, str)
                else incoming_trace_raw.decode("latin-1")
            )
            get_or_set_sf_trace_id(
                incoming_trace, is_associated_with_inbound_request=True
            )
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # Optional funcspan override (decode only if present)
        funcspan_override_header = None
        if funcspan_raw:
            funcspan_override_header = (
                funcspan_raw
                if isinstance(funcspan_raw, str)
                else funcspan_raw.decode("latin-1")
            )
            try:
                set_funcspan_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[aiohttp.middleware]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[aiohttp.middleware]] Failed to set function span override: {e}",
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
                            f"[[aiohttp.middleware]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[aiohttp.middleware]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # 3. Capture request body if enabled
        req_body = None
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # aiohttp Request.read() returns the body
                body = await request.read()
                req_body = body[:_REQUEST_LIMIT_BYTES] if body else None
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[aiohttp]] Request body capture: {len(body) if body else 0} bytes (method={request.method})",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[aiohttp]] Failed to capture request body: {e}", log=False)

        # 4. OTEL-STYLE: Capture endpoint metadata and register endpoint
        endpoint_id = None
        real_fn = _unwrap_user_func(handler)
        if callable(real_fn) and not real_fn.__module__.startswith("strawberry"):
            code = getattr(real_fn, "__code__", None)
            if code and _is_user_code(code.co_filename):
                key = (code.co_filename, code.co_firstlineno)
                sent = request.setdefault("sf_hops_sent", set())
                if key not in sent:
                    fname = code.co_filename
                    lno = code.co_firstlineno
                    fname_str = real_fn.__name__

                    # Get route pattern if available
                    route_pattern = getattr(request.match_info, "route", None)
                    route_str = str(
                        route_pattern.resource.canonical if route_pattern else None
                    )

                    # Check if route should be skipped
                    if route_str and should_skip_route(route_str, _ROUTES_TO_SKIP):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Aiohttp]] Skipping endpoint (route matches skip pattern): {route_str}",
                                log=False,
                            )
                        return

                    # Get or register endpoint
                    endpoint_id = _ENDPOINT_REGISTRY.get(key)
                    if endpoint_id is None:
                        endpoint_id = register_endpoint(
                            line=str(lno),
                            column="0",
                            name=fname_str,
                            entrypoint=fname,
                            route=route_str,
                        )
                        if endpoint_id >= 0:
                            _ENDPOINT_REGISTRY[key] = endpoint_id
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[aiohttp]] Registered endpoint: {fname_str} @ {fname}:{lno} (id={endpoint_id})",
                                    log=False,
                                )

                    sent.add(key)
                    request["sf_endpoint_id"] = endpoint_id

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[aiohttp]] Captured endpoint: {fname_str} ({fname}:{lno}) endpoint_id={endpoint_id}",
                            log=False,
                        )

        # 5. Call handler and capture exceptions (with cleanup in finally)
        try:
            try:
                response = await handler(request)
            except Exception as exc:  # ← captures *all* errors
                custom_excepthook(type(exc), exc, exc.__traceback__)
                raise  # re-raise for aiohttp

            # 6. Capture response headers if enabled
            resp_headers = None
            if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS and endpoint_id is not None:
                try:
                    resp_headers = dict(response.headers)
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[aiohttp]] Captured response headers: {len(resp_headers)} headers",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[aiohttp]] Failed to capture response headers: {e}",
                            log=False,
                        )

            # 7. Capture response body if enabled
            resp_body = None
            if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY and endpoint_id is not None:
                try:
                    # aiohttp Response has body or text attribute
                    if hasattr(response, "body") and response.body:
                        if isinstance(response.body, bytes):
                            resp_body = response.body[:_RESPONSE_LIMIT_BYTES]
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[aiohttp]] Captured from body (bytes): {len(resp_body)} bytes",
                                    log=False,
                                )
                        elif isinstance(response.body, str):
                            resp_body = response.body.encode("utf-8")[
                                :_RESPONSE_LIMIT_BYTES
                            ]
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[aiohttp]] Captured from body (str): {len(resp_body)} bytes",
                                    log=False,
                                )
                    elif hasattr(response, "text") and response.text:
                        resp_body = response.text.encode("utf-8")[
                            :_RESPONSE_LIMIT_BYTES
                        ]
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[aiohttp]] Captured from text: {len(resp_body)} bytes",
                                log=False,
                            )

                    if SF_DEBUG and not resp_body:
                        print(f"[[aiohttp]] No response body captured", log=False)
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[aiohttp]] Failed to capture response body: {e}",
                            log=False,
                        )

            # 8. OTEL-STYLE: Emit network hop AFTER handler completes
            if endpoint_id is not None and endpoint_id >= 0:
                try:
                    _, session_id = get_or_set_sf_trace_id()

                    # Extract raw path and query string for C to parse
                    raw_path = str(request.path)  # e.g., "/log"
                    raw_query = (
                        request.query_string.encode("utf-8")
                        if request.query_string
                        else b""
                    )  # e.g., b"foo=5"

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[aiohttp]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                            f"[[aiohttp]] Emitted network hop: endpoint_id={endpoint_id} "
                            f"session={session_id}",
                            log=False,
                        )
                except Exception as e:  # noqa: BLE001 S110
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(f"[[aiohttp]] Failed to emit network hop: {e}", log=False)

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

    # ===========================================================
    # 2 | Patch Application.__init__ to insert middleware
    # ===========================================================
    original_init = web.Application.__init__

    def patched_init(self, *args, middlewares=None, **kwargs):
        mlist = list(middlewares or [])
        mlist.insert(0, _sf_tracing_middleware)  # prepend → runs first
        original_init(self, *args, middlewares=mlist, **kwargs)
        _patch_router(self.router)  # apply once per app

        # Try to register endpoints immediately if routes are already defined
        if (
            hasattr(self, "router")
            and hasattr(self.router, "_resources")
            and self.router._resources
        ):
            try:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_aiohttp]] Routes already defined, registering immediately",
                        log=False,
                    )
                _pre_register_endpoints(self, routes_to_skip)
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_aiohttp]] Immediate registration failed: {e}",
                        log=False,
                    )

        # Register on_startup hook as a fallback (for routes added after __init__)
        async def _sf_startup(app):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_aiohttp]] Startup event fired, registering endpoints",
                    log=False,
                )
            _pre_register_endpoints(app, routes_to_skip)

        self.on_startup.append(_sf_startup)

    web.Application.__init__ = patched_init

    # ===========================================================
    # 3 | Patch router.add_route / add_routes for future calls
    # ===========================================================
    def _patch_router(router):
        if getattr(router, "_sf_tracing_patched", False):
            return  # already done

        orig_add_route = router.add_route
        orig_add_routes = router.add_routes

        def _wrap_and_add(method, path, handler, *a, **kw):  # noqa: ANN001
            return orig_add_route(method, path, _wrap_handler(handler), *a, **kw)

        def _wrap_handler(h):
            # strawberry skip & user-code check happen in middleware,
            # but wrapping here avoids duplicate stack frames
            return _unwrap_user_func(h) or h

        def _new_add_routes(routes):
            wrapped = [
                (
                    (m, p, _wrap_handler(h), *rest)  # route is (method,path,handler,…)
                    if len(r) >= 3
                    else r
                )
                for r in routes
                for (m, p, h, *rest) in (r,)  # unpack safely
            ]
            return orig_add_routes(wrapped)

        router.add_route = _wrap_and_add
        router.add_routes = _new_add_routes
        router._sf_tracing_patched = True
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_aiohttp]] router hooks installed", log=False)

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_aiohttp]] OTEL-style middleware + init patch applied", log=False)

    # ===========================================================
    # 4 | Patch aiohttp-cors if installed
    # ===========================================================
    def patch_aiohttp_cors():
        """
        Patch aiohttp-cors to automatically inject Sailfish headers.

        SAFE: Only modifies CORS if aiohttp-cors is installed and used.
        """
        try:
            import aiohttp_cors
        except ImportError:
            # aiohttp-cors not installed, skip patching
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_aiohttp_cors]] aiohttp-cors not installed, skipping",
                    log=False,
                )
            return

        # Check if already patched
        if hasattr(aiohttp_cors.CorsConfig, "_sf_cors_patched"):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("[[patch_aiohttp_cors]] Already patched, skipping", log=False)
            return

        # Patch CorsConfig.__init__ to intercept defaults parameter
        original_init = aiohttp_cors.CorsConfig.__init__

        def patched_init(self, app, *, defaults=None, router_adapter=None):
            # Intercept and modify defaults parameter
            if defaults:
                modified_defaults = {}
                for origin, resource_options in defaults.items():
                    # Handle both ResourceOptions objects and dicts
                    if isinstance(resource_options, aiohttp_cors.ResourceOptions):
                        # ResourceOptions object - access allow_headers attribute
                        if hasattr(resource_options, "allow_headers"):
                            original_headers = resource_options.allow_headers
                            if should_inject_headers(original_headers):
                                # Create new ResourceOptions with modified headers
                                # Convert frozenset to list for allow_methods and expose_headers
                                allow_methods = resource_options.allow_methods
                                if isinstance(allow_methods, frozenset):
                                    allow_methods = list(allow_methods)

                                expose_headers = resource_options.expose_headers
                                if isinstance(expose_headers, frozenset):
                                    expose_headers = list(expose_headers)

                                modified_defaults[origin] = aiohttp_cors.ResourceOptions(
                                    allow_credentials=resource_options.allow_credentials,
                                    expose_headers=expose_headers,
                                    allow_headers=inject_sailfish_headers(original_headers),
                                    allow_methods=allow_methods,
                                    max_age=resource_options.max_age,
                                )
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[patch_aiohttp_cors]] Injected Sailfish headers into defaults for origin {origin}",
                                        log=False,
                                    )
                            else:
                                modified_defaults[origin] = resource_options
                        else:
                            modified_defaults[origin] = resource_options
                    elif isinstance(resource_options, dict) and "allow_headers" in resource_options:
                        # Dict config - modify directly
                        original_headers = resource_options["allow_headers"]
                        if should_inject_headers(original_headers):
                            modified_config = resource_options.copy()
                            modified_config["allow_headers"] = inject_sailfish_headers(original_headers)
                            modified_defaults[origin] = modified_config
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[patch_aiohttp_cors]] Injected Sailfish headers into defaults dict for origin {origin}",
                                    log=False,
                                )
                        else:
                            modified_defaults[origin] = resource_options
                    else:
                        modified_defaults[origin] = resource_options

                defaults = modified_defaults

            # Call original init with modified defaults
            original_init(self, app, defaults=defaults, router_adapter=router_adapter)

        aiohttp_cors.CorsConfig.__init__ = patched_init

        # Patch CorsConfig.add method (for route-specific overrides)
        original_add = aiohttp_cors.CorsConfig.add

        def patched_add(self, route, config=None):
            # Intercept the config and modify allow_headers
            if config:
                modified_config = {}
                for origin, resource_config in config.items():
                    if isinstance(resource_config, aiohttp_cors.ResourceOptions):
                        # ResourceOptions object
                        if hasattr(resource_config, "allow_headers"):
                            original_headers = resource_config.allow_headers
                            if should_inject_headers(original_headers):
                                # Convert frozenset to list for allow_methods and expose_headers
                                allow_methods = resource_config.allow_methods
                                if isinstance(allow_methods, frozenset):
                                    allow_methods = list(allow_methods)

                                expose_headers = resource_config.expose_headers
                                if isinstance(expose_headers, frozenset):
                                    expose_headers = list(expose_headers)

                                modified_config[origin] = aiohttp_cors.ResourceOptions(
                                    allow_credentials=resource_config.allow_credentials,
                                    expose_headers=expose_headers,
                                    allow_headers=inject_sailfish_headers(original_headers),
                                    allow_methods=allow_methods,
                                    max_age=resource_config.max_age,
                                )
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        "[[patch_aiohttp_cors]] Injected Sailfish headers into CorsConfig.add()",
                                        log=False,
                                    )
                            else:
                                modified_config[origin] = resource_config
                        else:
                            modified_config[origin] = resource_config
                    elif isinstance(resource_config, dict) and "allow_headers" in resource_config:
                        original_headers = resource_config["allow_headers"]
                        if should_inject_headers(original_headers):
                            modified = resource_config.copy()
                            modified["allow_headers"] = inject_sailfish_headers(original_headers)
                            modified_config[origin] = modified
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    "[[patch_aiohttp_cors]] Injected Sailfish headers into CorsConfig.add()",
                                    log=False,
                                )
                        else:
                            modified_config[origin] = resource_config
                    else:
                        modified_config[origin] = resource_config

                config = modified_config

            # Call original add
            return original_add(self, route, config)

        aiohttp_cors.CorsConfig.add = patched_add
        aiohttp_cors.CorsConfig._sf_cors_patched = True

        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_aiohttp_cors]] Successfully patched aiohttp-cors", log=False)

    # Call CORS patching
    patch_aiohttp_cors()
