"""
Litestar ASGI framework patch for OTEL-style network hop capture.
Captures request/response headers and bodies when enabled via env vars.
Uses sys.setprofile tracer to reliably capture endpoint metadata.
"""

import sys
from functools import lru_cache
from typing import Any, Callable, List, Optional, Set

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
from .utils import _is_user_code, should_skip_route

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Routes to skip (set by patch_litestar)
_ROUTES_TO_SKIP = []


def _sf_tracing_factory(app: Callable) -> Callable:
    """
    OTEL-STYLE ASGI middleware that:
      • propagates the inbound SAILFISH_TRACING_HEADER header
      • captures request headers/body if enabled
      • uses sys.setprofile tracer to capture first user code frame
      • emits NetworkHop AFTER response sent (zero overhead)
      • captures response headers/body if enabled
      • reports any unhandled exception via `custom_excepthook`
    """

    async def _middleware(scope, receive, send):
        if scope.get("type") != "http":
            await app(scope, receive, send)
            return

        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        request_path = scope.get("path", "")
        set_current_request_path(request_path)

        # Always print to verify middleware is being called
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[Litestar._middleware]] HTTP request to {request_path}, type={scope.get('type')}",
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
                        f"[[Litestar._middleware]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Litestar._middleware]] Failed to set function span override: {e}",
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
                            f"[[Litestar._middleware]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Litestar._middleware]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # OPTIMIZATION: Skip ALL capture infrastructure if not capturing network hops
        # We still needed to set up trace_id and outbound header base above (for outbound call tracing)
        # but we can skip all request/response capture overhead
        if not SF_NETWORKHOP_CAPTURE_ENABLED:
            try:
                await app(scope, receive, send)
            except Exception as exc:  # noqa: BLE001
                custom_excepthook(type(exc), exc, exc.__traceback__)
                raise
            finally:
                # CRITICAL: Clear C TLS to prevent stale data in thread pools
                clear_c_tls_parent_trace_id()

                # CRITICAL: Clear outbound header base to prevent stale cached headers
                clear_outbound_header_base()

                # CRITICAL: Clear trace_id to ensure fresh generation for next request
                clear_trace_id()

                # CRITICAL: Clear current request path to prevent stale data in thread pools
                clear_current_request_path()
            return

        # NOTE: req_headers already captured in single-pass scan above (if enabled)

        # 2. Capture request body if enabled (must intercept receive)
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

        # 3. Use sys.setprofile to capture first user code frame
        endpoint_info = {}
        previous_profiler = sys.getprofile()

        def _tracer(frame, event, arg):
            # Chain to previous profiler first
            if previous_profiler is not None:
                try:
                    previous_profiler(frame, event, arg)
                except Exception:  # noqa: BLE001 S110
                    pass

            # Capture first user code frame (skip Strawberry GraphQL handlers)
            if event == "call" and _is_user_code(frame.f_code.co_filename):
                if not endpoint_info:  # Only capture once
                    # Skip Strawberry GraphQL handlers - they're handled by separate Strawberry extension
                    module_name = frame.f_globals.get("__name__", "")
                    if module_name.startswith("strawberry"):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Litestar]] Skipping Strawberry GraphQL handler: {frame.f_code.co_name}",
                                log=False,
                            )
                        sys.setprofile(previous_profiler)
                        return _tracer

                    endpoint_info["filename"] = frame.f_code.co_filename
                    endpoint_info["line"] = frame.f_lineno
                    endpoint_info["name"] = frame.f_code.co_name

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Litestar]] Tracer captured endpoint: {frame.f_code.co_name} "
                            f"({frame.f_code.co_filename}:{frame.f_lineno})",
                            log=False,
                        )
                    # Restore previous profiler
                    sys.setprofile(previous_profiler)
            return _tracer

        sys.setprofile(_tracer)

        # 4. Capture response headers and body if enabled
        resp_headers = None
        resp_body_chunks = []

        # OPTIMIZATION: Cache debug flag check (avoid repeated lookups)
        _debug_enabled = SF_DEBUG and app_config._interceptors_initialized

        # OPTIMIZATION: Cache capture flags (avoid repeated global lookups in hot path)
        _capture_resp_headers = SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS
        _capture_resp_body = SF_NETWORKHOP_CAPTURE_RESPONSE_BODY

        async def wrapped_send(message):
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

            # 5. OTEL-STYLE: Emit network hop AFTER final response body sent
            # Ensure profiler is restored
            sys.setprofile(previous_profiler)

            if endpoint_info:
                try:
                    filename = endpoint_info["filename"]
                    line_no = endpoint_info["line"]
                    fn_name = endpoint_info["name"]
                    hop_key = (filename, line_no)

                    # Get route pattern if available
                    route_pattern = scope["path"]

                    # Check if route should be skipped
                    if route_pattern and should_skip_route(
                        route_pattern, _ROUTES_TO_SKIP
                    ):
                        if _debug_enabled:
                            print(
                                f"[[Litestar]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                                log=False,
                            )
                        return

                    # Get or register endpoint
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
                            if _debug_enabled:
                                print(
                                    f"[[Litestar]] Registered endpoint: {fn_name} @ {filename}:{line_no} (id={endpoint_id})",
                                    log=False,
                                )

                    if endpoint_id is not None and endpoint_id >= 0:
                        # OPTIMIZATION: Use get_sf_trace_id() directly instead of get_or_set_sf_trace_id()
                        # Trace ID is GUARANTEED to be set at request start (lines 105-112)
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
                                f"[[Litestar]] Emitted NetworkHop for endpoint_id={endpoint_id}",
                                log=False,
                            )
                except Exception as e:  # noqa: BLE001 S110
                    if _debug_enabled:
                        print(
                            f"[[Litestar]] Failed to emit NetworkHop: {e}",
                            log=False,
                        )

        # Exception capture
        try:
            await app(scope, wrapped_receive, wrapped_send)
        except Exception as exc:  # noqa: BLE001
            # Ensure profiler is restored even on exception
            sys.setprofile(previous_profiler)
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise
        finally:
            # Ensure profiler is always restored
            sys.setprofile(previous_profiler)

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

    return _middleware


def patch_litestar(routes_to_skip: Optional[List[str]] = None) -> None:
    """
    OTEL-STYLE Litestar patch:
    • Uses sys.setprofile tracer to capture endpoint metadata
    • Captures request headers/body if enabled
    • Emits network hop AFTER handler completes (zero-overhead)
    • Captures response headers/body if enabled
    • Universal exception handler for all exceptions
    Safe no-op if Litestar is not installed.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        import litestar
        from litestar import Litestar
        from litestar.middleware import DefineMiddleware
    except ImportError:
        return

    original_init = Litestar.__init__

    def patched_init(self, *args, **kwargs):
        """
        Injects Sailfish into every Litestar app instance by:
        1. Pre-pending ASGI middleware for header propagation + network hop capture
        2. Adding a generic exception handler for all exceptions
        """

        # 1. Middleware injection
        mw = list(kwargs.get("middleware") or [])
        mw.insert(0, DefineMiddleware(_sf_tracing_factory))
        kwargs["middleware"] = mw

        # 2. Universal exception handler
        def _sf_exception_handler(request, exc):  # type: ignore[valid-type]
            """
            Litestar calls this for any Exception once routing/dep-resolution is done.
            Forward to custom_excepthook and re-raise so builtin handler produces response.
            """
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise exc  # let Litestar fall back to its default logic

        # Merge with user-supplied handlers
        existing_handlers = kwargs.get("exception_handlers") or {}
        if isinstance(existing_handlers, dict):
            existing_handlers.setdefault(Exception, _sf_exception_handler)
        else:  # Litestar also accepts list[tuple[Exception, Handler]]
            existing_handlers = list(existing_handlers)  # type: ignore[arg-type]
            existing_handlers.append((Exception, _sf_exception_handler))
        kwargs["exception_handlers"] = existing_handlers

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_litestar]] OTEL-style middleware + exception handler installed",
                log=False,
            )

        return original_init(self, *args, **kwargs)

    Litestar.__init__ = patched_init

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_litestar]] OTEL-style patch applied", log=False)

    # ── CORS patching ──────────────────────────────────────────────────
    patch_litestar_cors()


def patch_litestar_cors():
    """
    Patch Litestar's CORSConfig to automatically inject Sailfish headers.

    SAFE: Only modifies allow_headers if CORS is already configured.
    Litestar uses CORSConfig dataclass for CORS configuration.
    """
    try:
        from litestar.config.cors import CORSConfig
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_litestar_cors]] Litestar CORSConfig not available, skipping",
                log=False,
            )
        return

    # Check if already patched
    if hasattr(CORSConfig, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_litestar_cors]] Already patched, skipping", log=False)
        return

    # Patch CORSConfig.__init__ to intercept and modify allow_headers
    original_init = CORSConfig.__init__

    def patched_init(
        self,
        allow_origins=("*",),
        allow_methods=("*",),
        allow_headers=("*",),
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
                    "[[patch_litestar_cors]] Injected Sailfish headers into CORSConfig",
                    log=False,
                )

        # Call original init with potentially modified headers
        original_init(
            self,
            allow_origins=allow_origins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
            allow_origin_regex=allow_origin_regex,
            expose_headers=expose_headers,
            max_age=max_age,
        )

    CORSConfig.__init__ = patched_init
    CORSConfig._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_litestar_cors]] Successfully patched Litestar CORSConfig",
            log=False,
        )
