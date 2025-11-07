"""
• SFTracingQuartASGIMiddleware: pulls SAILFISH_TRACING_HEADER into your ContextVar.
• patch_quart(): wraps Quart.__init__, installs middleware and
  redefines .route so that each user-land view emits one NetworkHop.
"""

import asyncio
import inspect
import sysconfig
from functools import lru_cache, wraps
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
from .utils import _unwrap_user_func  # your cached helpers
from .utils import _is_user_code, should_skip_route

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Module-level variable for routes to skip (set by patch_quart)
_ROUTES_TO_SKIP = []

try:
    import quart
    from quart.app import Quart
    from quart.wrappers import Response
except ImportError:
    # Quart not installed → no-op
    def patch_quart(routes_to_skip: Optional[List[str]] = None):
        return

else:
    # ──────────────────────────────────────────────────────────
    # OTEL-STYLE: Request hooks (before + after) - Flask-style
    # ──────────────────────────────────────────────────────────
    def _install_request_hooks(app):
        """Install Flask-style before/after request hooks for Quart."""
        from quart import g, request

        @app.before_request
        async def _extract_sf_header():
            """OTEL-STYLE: Extract trace header and capture request data before handler."""
            # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
            set_current_request_path(request.path)

            rid = request.headers.get(SAILFISH_TRACING_HEADER)
            if rid:
                get_or_set_sf_trace_id(rid, is_associated_with_inbound_request=True)
            else:
                # No incoming header - generate fresh trace_id for this request
                generate_new_trace_id()

            # Check for function span capture override header (highest priority!)
            funcspan_override_header = request.headers.get(
                "X-Sf3-FunctionSpanCaptureOverride"
            )
            if funcspan_override_header:
                try:
                    set_funcspan_override(funcspan_override_header)
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart.before_request]] Set function span override from header: {funcspan_override_header}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart.before_request]] Failed to set function span override: {e}",
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
                                f"[[Quart.before_request]] Initialized outbound header base (base={base_trace[:16]}...)",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Quart.before_request]] Failed to initialize outbound header base: {e}",
                        log=False,
                    )

            # Capture request headers if enabled
            if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
                try:
                    req_headers = dict(request.headers)
                    g._sf_request_headers = req_headers
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] Captured request headers: {len(req_headers)} headers",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] Failed to capture request headers: {e}",
                            log=False,
                        )

            # Capture request body if enabled
            if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
                try:
                    # Quart: await request.get_data() gets raw bytes
                    body = await request.get_data()
                    if body:
                        req_body = body[:_REQUEST_LIMIT_BYTES]
                        g._sf_request_body = req_body
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Quart]] Request body capture: {len(req_body)} bytes",
                                log=False,
                            )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] Failed to capture request body: {e}", log=False
                        )

        @app.after_request
        async def _emit_network_hop(response):
            """
            OTEL-STYLE: Emit network hop AFTER response is built.
            Quart is Flask-based, so we use the same @after_request pattern.
            """
            endpoint_id = getattr(g, "_sf_endpoint_id", None)
            if endpoint_id is not None and endpoint_id >= 0:
                try:
                    _, session_id = get_or_set_sf_trace_id()

                    # Get captured request data
                    req_headers = getattr(g, "_sf_request_headers", None)
                    req_body = getattr(g, "_sf_request_body", None)

                    # Capture response headers if enabled
                    resp_headers = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                        try:
                            resp_headers = dict(response.headers)
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Quart]] Captured response headers: {len(resp_headers)} headers",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Quart]] Failed to capture response headers: {e}",
                                    log=False,
                                )

                    # Capture response body if enabled
                    resp_body = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                        try:
                            # Quart response: get_data() returns bytes (async)
                            body = await response.get_data()
                            if body:
                                resp_body = body[:_RESPONSE_LIMIT_BYTES]
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Quart]] Captured response body: {len(resp_body)} bytes",
                                        log=False,
                                    )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Quart]] Failed to capture response body: {e}",
                                    log=False,
                                )

                    # Extract raw path and query string for C to parse
                    raw_path = request.path  # e.g., "/log"
                    raw_query = request.query_string  # Already bytes (e.g., b"foo=5")

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                            f"[[Quart]] Emitted network hop: endpoint_id={endpoint_id} "
                            f"session={session_id}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(f"[[Quart]] Failed to emit network hop: {e}", log=False)

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

            return response

    # ──────────────────────────────────────────────────────────
    # OTEL-STYLE: Per-view endpoint metadata capture
    # ──────────────────────────────────────────────────────────
    def _hop_wrapper(view_fn: Callable, route: str = None):
        """
        OTEL-STYLE: Pre-register endpoint and store endpoint_id in quart.g.
        Emission happens in @after_request hook with captured body/headers.
        """
        from quart import g

        real_fn = _unwrap_user_func(view_fn)

        code = getattr(real_fn, "__code__", None)
        if not code or not _is_user_code(code.co_filename):
            return view_fn

        # Skip Strawberry GraphQL handlers
        if getattr(real_fn, "__module__", "").startswith("strawberry"):
            return view_fn

        # Check if route should be skipped
        if should_skip_route(route, _ROUTES_TO_SKIP):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Quart]] Skipping endpoint (route matches skip pattern): {route}",
                    log=False,
                )
            return view_fn  # Return original function unwrapped - no telemetry

        hop_key = (code.co_filename, code.co_firstlineno)
        fn_name = real_fn.__name__
        filename = code.co_filename
        line_no = code.co_firstlineno

        # Pre-register endpoint if user code
        endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
        if endpoint_id is None:
            endpoint_id = register_endpoint(
                line=str(line_no),
                column="0",
                name=fn_name,
                entrypoint=filename,
                route=route,
            )
            if endpoint_id >= 0:
                _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Quart]] Registered endpoint: {fn_name} @ {filename}:{line_no} (id={endpoint_id})",
                        log=False,
                    )

        @wraps(view_fn)
        async def _wrapped(*args, **kwargs):
            # OTEL-STYLE: Store endpoint_id for after_request to emit
            if not hasattr(g, "_sf_endpoint_id"):
                g._sf_endpoint_id = endpoint_id

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Quart]] Captured endpoint: {fn_name} ({filename}:{line_no}) endpoint_id={endpoint_id}",
                        log=False,
                    )

            return await view_fn(*args, **kwargs)

        return _wrapped

    def _patch_add_route(cls):
        """
        Patch add_url_rule on Quart so that the final stored endpoint function
        is wrapped after Quart has done its own bookkeeping.
        """
        original_add = cls.add_url_rule

        def patched_add(self, rule, endpoint=None, view_func=None, **options):
            # let Quart register the route first
            original_add(self, rule, endpoint=endpoint, view_func=view_func, **options)

            ep = endpoint or (view_func and view_func.__name__)
            if not ep:  # defensive
                return

            target = self.view_functions.get(ep)
            if callable(target):
                self.view_functions[ep] = _hop_wrapper(target, route=rule)

        cls.add_url_rule = patched_add

    # ──────────────────────────────────────────────────────────
    # ASGI middleware - TRUE ZERO OVERHEAD (emits AFTER response sent)
    # ──────────────────────────────────────────────────────────
    class SFZeroOverheadQuartMiddleware:
        """
        OTEL-STYLE ZERO-OVERHEAD network hop capture middleware.

        - Propagates inbound SAILFISH_TRACING_HEADER → ContextVar
        - Pre-registers endpoints at startup for ultra-fast emission
        - Captures request/response headers and body when enabled
        - Emits NetworkHop AFTER response sent (pure async, no blocking)
        - Funnels all exceptions through custom_excepthook
        """

        def __init__(self, app):
            self.app = app
            self._endpoint_cache = {}  # Cache endpoint_id by function id

        async def __call__(self, scope, receive, send):
            if scope.get("type") != "http":
                await self.app(scope, receive, send)
                return

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
                            f"[[Quart.middleware]] Set function span override from header: {funcspan_override_header}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart.middleware]] Failed to set function span override: {e}",
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
                                f"[[Quart.middleware]] Initialized outbound header base (base={base_trace[:16]}...)",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Quart.middleware]] Failed to initialize outbound header base: {e}",
                        log=False,
                    )

            # Pre-register endpoint and get endpoint_id
            endpoint_id = None
            endpoint_fn = scope.get("endpoint")

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Quart]] endpoint_fn={endpoint_fn}, type={type(endpoint_fn) if endpoint_fn else None}",
                    log=False,
                )

            if endpoint_fn:
                # Check cache first
                fn_id = id(endpoint_fn)
                if fn_id in self._endpoint_cache:
                    endpoint_id = self._endpoint_cache[fn_id]
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] Using cached endpoint_id={endpoint_id}",
                            log=False,
                        )
                else:
                    # Extract metadata and register
                    user_fn = _unwrap_user_func(endpoint_fn)
                    code = getattr(user_fn, "__code__", None)

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] user_fn={user_fn.__name__ if hasattr(user_fn, '__name__') else user_fn}, code={code}, is_user_code={_is_user_code(code.co_filename) if code else False}",
                            log=False,
                        )

                    # Skip Strawberry GraphQL handlers
                    if getattr(user_fn, "__module__", "").startswith("strawberry"):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Quart]] Skipping Strawberry GraphQL endpoint",
                                log=False,
                            )
                        # Don't register, don't cache
                    elif code and _is_user_code(code.co_filename):
                        hop_key = (code.co_filename, code.co_firstlineno)

                        # Check global registry first
                        endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
                        if endpoint_id is None:
                            endpoint_id = register_endpoint(
                                line=str(code.co_firstlineno),
                                column="0",
                                name=user_fn.__name__,
                                entrypoint=code.co_filename,
                                route=None,
                            )
                            if endpoint_id >= 0:
                                _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Quart]] Registered endpoint: {user_fn.__name__} @ {code.co_filename}:{code.co_firstlineno} (id={endpoint_id})",
                                        log=False,
                                    )
                            else:
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Quart]] Failed to register endpoint (returned {endpoint_id})",
                                        log=False,
                                    )
                        else:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Quart]] Using pre-registered endpoint_id={endpoint_id}",
                                    log=False,
                                )

                        # Cache by function id for fast lookup
                        self._endpoint_cache[fn_id] = endpoint_id

            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[Quart]] Final endpoint_id={endpoint_id}", log=False)

            # NOTE: req_headers already captured in single-pass scan above (if enabled)

            # Capture request body if enabled
            body_parts = []
            body_size = 0
            if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
                try:
                    # Save original receive before wrapping
                    original_receive = receive

                    async def receive_with_body():
                        nonlocal body_size
                        message = await original_receive()
                        if message["type"] == "http.request":
                            body_part = message.get("body", b"")
                            if body_part and body_size < _REQUEST_LIMIT_BYTES:
                                remaining = _REQUEST_LIMIT_BYTES - body_size
                                body_parts.append(body_part[:remaining])
                                body_size += len(body_part)
                        return message

                    receive = receive_with_body

                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] Failed to setup request body capture: {e}",
                            log=False,
                        )

            # Capture response headers and body
            resp_headers = None
            resp_body_parts = []
            resp_body_size = 0

            # OTEL-STYLE: Wrap send to capture response data and emit AFTER response sent
            async def wrapped_send(message):
                nonlocal resp_headers, resp_body_size

                # Capture response headers
                if (
                    message["type"] == "http.response.start"
                    and SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS
                ):
                    try:
                        headers = message.get("headers", [])
                        resp_headers = {
                            name.decode("utf-8"): val.decode("utf-8")
                            for name, val in headers
                        }
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Quart]] Captured response headers: {len(resp_headers)} headers",
                                log=False,
                            )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Quart]] Failed to capture response headers: {e}",
                                log=False,
                            )

                # Capture response body
                if (
                    message["type"] == "http.response.body"
                    and SF_NETWORKHOP_CAPTURE_RESPONSE_BODY
                ):
                    try:
                        body_part = message.get("body", b"")
                        if body_part and resp_body_size < _RESPONSE_LIMIT_BYTES:
                            remaining = _RESPONSE_LIMIT_BYTES - resp_body_size
                            resp_body_parts.append(body_part[:remaining])
                            resp_body_size += len(body_part)
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Quart]] Failed to capture response body chunk: {e}",
                                log=False,
                            )

                await send(message)

                # After final response body sent, emit network hop
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Quart]] Message type: {message.get('type')}, more_body: {message.get('more_body', False)}, endpoint_id: {endpoint_id}",
                        log=False,
                    )

                if message["type"] == "http.response.body" and not message.get(
                    "more_body", False
                ):
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Quart]] Final response body message, checking endpoint_id={endpoint_id}",
                            log=False,
                        )

                    if endpoint_id is not None and endpoint_id >= 0:
                        try:
                            _, session_id = get_or_set_sf_trace_id()

                            # Finalize request body
                            final_req_body = (
                                b"".join(body_parts) if body_parts else None
                            )
                            if final_req_body and SF_DEBUG:
                                print(
                                    f"[[Quart]] Request body capture: {len(final_req_body)} bytes",
                                    log=False,
                                )

                            # Finalize response body
                            final_resp_body = (
                                b"".join(resp_body_parts) if resp_body_parts else None
                            )
                            if final_resp_body and SF_DEBUG:
                                print(
                                    f"[[Quart]] Captured response body: {len(final_resp_body)} bytes",
                                    log=False,
                                )

                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Quart]] About to emit network hop: endpoint_id={endpoint_id}, "
                                    f"req_headers={'present' if req_headers else 'None'}, "
                                    f"req_body={len(final_req_body) if final_req_body else 0} bytes, "
                                    f"resp_headers={'present' if resp_headers else 'None'}, "
                                    f"resp_body={len(final_resp_body) if final_resp_body else 0} bytes",
                                    log=False,
                                )

                            fast_send_network_hop_fast(
                                session_id=session_id,
                                endpoint_id=endpoint_id,
                                raw_path=scope.get("path"),
                                raw_query_string=scope.get("query_string", b""),
                                request_headers=req_headers,
                                request_body=final_req_body,
                                response_headers=resp_headers,
                                response_body=final_resp_body,
                            )

                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Quart]] Emitted network hop: endpoint_id={endpoint_id} "
                                    f"session={session_id}",
                                    log=False,
                                )
                        except Exception as e:  # noqa: BLE001 S110
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Quart]] Failed to emit network hop: {e}",
                                    log=False,
                                )

            try:
                await self.app(scope, receive, wrapped_send)
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

    # ──────────────────────────────────────────────────────────
    # Main patch entry-point (Flask-style hooks for Quart)
    # ──────────────────────────────────────────────────────────
    def patch_quart(routes_to_skip: Optional[List[str]] = None):
        """
        Quart patch using Flask-style before/after request hooks:
        • Wraps view functions to capture endpoint_id
        • Uses @before_request to capture request data
        • Uses @after_request to emit AFTER response built (Flask-style)
        • Captures request/response headers and body when enabled
        • Direct C call with route/query params extracted from request object

        Note: Quart is Flask-based and doesn't expose endpoints in ASGI scope,
        so we use Flask-style hooks instead of ASGI middleware.
        """
        global _ROUTES_TO_SKIP
        _ROUTES_TO_SKIP = routes_to_skip or []

        # Guard against double-patching
        if getattr(Quart, "__sf_tracing_patched__", False):
            return

        original_init = Quart.__init__

        def patched_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)

            # Install Flask-style hooks for request/response capture
            _install_request_hooks(self)

            # Patch add_url_rule to wrap view functions
            _patch_add_route(self.__class__)

            if SF_DEBUG and app_config._interceptors_initialized:
                print("[[patch_quart]] Flask-style hooks installed", log=False)

        Quart.__init__ = patched_init
        Quart.__sf_tracing_patched__ = True

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_quart]] Flask-style patch applied (emits in @after_request)",
                log=False,
            )

    def patch_quart_cors():
        """
        Patch quart-cors to automatically inject Sailfish headers.

        SAFE: Only modifies CORS if quart-cors is installed and used.
        """
        try:
            from quart_cors import cors
        except ImportError:
            # quart-cors not installed, skip patching
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_quart_cors]] quart-cors not installed, skipping", log=False
                )
            return

        # Check if already patched
        if hasattr(cors, "_sf_cors_patched"):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("[[patch_quart_cors]] Already patched, skipping", log=False)
            return

        # Patch the cors decorator/function
        original_cors = cors

        def patched_cors(app=None, **kwargs):
            # Intercept allow_headers parameter
            if "allow_headers" in kwargs:
                original_headers = kwargs["allow_headers"]
                if should_inject_headers(original_headers):
                    kwargs["allow_headers"] = inject_sailfish_headers(original_headers)
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            "[[patch_quart_cors]] Injected Sailfish headers into quart-cors",
                            log=False,
                        )

            # Call original cors
            return original_cors(app, **kwargs)

        # Replace the cors function in the module
        import quart_cors as qc_module

        qc_module.cors = patched_cors
        cors._sf_cors_patched = True

        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_quart_cors]] Successfully patched quart-cors", log=False)

    # Call CORS patching
    patch_quart_cors()

    # Expose the patch function
    __all__ = ["patch_quart"]
