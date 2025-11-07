import inspect
import site
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
    clear_funcspan_override,
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

# Module-level variable for routes to skip (set by patch_tornado)
_ROUTES_TO_SKIP = []


def patch_tornado(routes_to_skip: Optional[List[str]] = None):
    """
    Monkey-patch tornado.web.RequestHandler so that every request:

      1. Propagates SAILFISH_TRACING_HEADER into the ContextVar.
      2. Emits ONE NetworkHop when user-land verb handler starts.
      3. Funnels *all* exceptions—including tornado.web.HTTPError—through
         custom_excepthook before Tornado's own error machinery runs.

    Safe no-op if Tornado isn't installed.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []
    try:
        import tornado.web
    except ImportError:  # Tornado not installed
        return

    # --------------------------------------------------------------- #
    # a)  Header capture + endpoint metadata (prepare)
    # --------------------------------------------------------------- #
    original_prepare = tornado.web.RequestHandler.prepare

    def patched_prepare(self, *args, **kwargs):
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(self.request.path)

        # -- 1) PERFORMANCE: Single-pass bytes-level header scan (similar to FastAPI optimization)
        # Tornado stores headers as HTTPHeaders object, iterate once to extract needed headers
        incoming_trace_header = None
        funcspan_override_header = None

        # Scan headers once
        for name, value in self.request.headers.get_all():
            name_lower = name.lower()
            if name_lower == SAILFISH_TRACING_HEADER.lower():
                incoming_trace_header = value
            elif name_lower == "x-sf3-functionspancaptureoverride":
                funcspan_override_header = value

        # -- 2) CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        if incoming_trace_header:
            # Incoming X-Sf3-Rid header provided - use it
            get_or_set_sf_trace_id(
                incoming_trace_header, is_associated_with_inbound_request=True
            )
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # -- 3) Set function span override if provided
        if funcspan_override_header:
            try:
                set_funcspan_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Tornado.prepare]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Tornado.prepare]] Failed to set function span override: {e}",
                        log=False,
                    )

        # -- 4) Initialize outbound base without list/allocs from split()
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
                            f"[[Tornado.prepare]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Tornado.prepare]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # -- 5) Capture request headers if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
            try:
                req_headers = dict(self.request.headers)
                self._sf_request_headers = req_headers
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Tornado]] Captured request headers: {len(req_headers)} headers",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Tornado]] Failed to capture request headers: {e}", log=False
                    )

        # -- 6) Capture request body if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                body = self.request.body
                if body:
                    req_body = body[:_REQUEST_LIMIT_BYTES]
                    self._sf_request_body = req_body
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Tornado]] Request body capture: {len(req_body)} bytes",
                            log=False,
                        )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Tornado]] Failed to capture request body: {e}", log=False)

        # -- 7) OTEL-STYLE: Pre-register endpoint and store endpoint_id
        method_name = self.request.method.lower()
        handler_fn = getattr(self, method_name, None)

        if callable(handler_fn):
            module = getattr(handler_fn, "__module__", "")
            if not module.startswith("strawberry"):
                real_fn = _unwrap_user_func(handler_fn)
                code_obj = getattr(real_fn, "__code__", None)
                if code_obj and _is_user_code(code_obj.co_filename):
                    hop_key = (code_obj.co_filename, code_obj.co_firstlineno)

                    # Extract route pattern from the handler's route_spec
                    route_pattern = None
                    try:
                        # Tornado stores the route pattern in the request's path_kwargs
                        # We can get the pattern from the application's handlers
                        if hasattr(self, "application") and hasattr(
                            self.application, "handlers"
                        ):
                            # Find the matching route spec
                            for host_pattern, handlers in self.application.handlers:
                                for spec in handlers:
                                    # spec is a URLSpec with regex, handler_class, kwargs, name
                                    if spec.handler_class == type(self):
                                        route_pattern = spec.regex.pattern
                                        break
                                if route_pattern:
                                    break
                    except Exception:
                        pass

                    # Check if route should be skipped
                    if should_skip_route(
                        route_pattern or self.request.path, _ROUTES_TO_SKIP
                    ):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Tornado]] Skipping endpoint (route matches skip pattern): {route_pattern or self.request.path}",
                                log=False,
                            )
                        return original_prepare(self, *args, **kwargs)

                    # Pre-register endpoint if not already registered
                    endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
                    if endpoint_id is None:
                        endpoint_id = register_endpoint(
                            line=str(code_obj.co_firstlineno),
                            column="0",
                            name=real_fn.__name__,
                            entrypoint=code_obj.co_filename,
                            route=route_pattern,
                        )
                        if endpoint_id >= 0:
                            _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Tornado]] Registered endpoint: {real_fn.__name__} @ "
                                    f"{code_obj.co_filename}:{code_obj.co_firstlineno} (id={endpoint_id})",
                                    log=False,
                                )

                    # Store endpoint_id for on_finish() to emit
                    self._sf_endpoint_id = endpoint_id

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Tornado]] Captured endpoint: {real_fn.__name__} "
                            f"({code_obj.co_filename}:{code_obj.co_firstlineno}) endpoint_id={endpoint_id}",
                            log=False,
                        )

        return original_prepare(self, *args, **kwargs)

    tornado.web.RequestHandler.prepare = patched_prepare

    # --------------------------------------------------------------- #
    # b)  Exception capture – patch _execute and write_error
    # --------------------------------------------------------------- #
    original_execute = tornado.web.RequestHandler._execute
    original_write_error = tornado.web.RequestHandler.write_error

    async def patched_execute(self, *args, **kwargs):
        try:
            return await original_execute(self, *args, **kwargs)
        except Exception as exc:  # HTTPError included
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise  # let Tornado handle 500/4xx

    def patched_write_error(self, status_code, **kwargs):
        """
        Tornado calls write_error for HTTPError and uncaught exceptions.
        Capture the exception (when provided) before rendering.
        """
        exc_info = kwargs.get("exc_info")
        if exc_info and isinstance(exc_info, tuple) and exc_info[1]:
            exc_type, exc_val, exc_tb = exc_info
            custom_excepthook(exc_type, exc_val, exc_tb)
        # Fallback: still call original renderer
        return original_write_error(self, status_code, **kwargs)

    tornado.web.RequestHandler._execute = patched_execute
    tornado.web.RequestHandler.write_error = patched_write_error

    # --------------------------------------------------------------- #
    # c)  CORS patching – inject Sailfish headers
    # --------------------------------------------------------------- #
    patch_tornado_cors()


def patch_tornado_cors():
    """
    Patch Tornado's RequestHandler to automatically inject Sailfish headers into CORS.

    SAFE: Only modifies Access-Control-Allow-Headers if the handler sets it.
    Tornado doesn't have a standard CORS library, so we patch the common patterns:
    1. set_default_headers() - called for every request
    2. options() - called for preflight requests
    """
    try:
        import tornado.web
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_tornado_cors]] Tornado not available, skipping", log=False)
        return

    # Check if already patched
    if hasattr(tornado.web.RequestHandler, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_tornado_cors]] Already patched, skipping", log=False)
        return

    # Patch set_default_headers to intercept and modify Access-Control-Allow-Headers
    original_set_header = tornado.web.RequestHandler.set_header

    def patched_set_header(self, name, value):
        # Intercept Access-Control-Allow-Headers header
        if name.lower() == "access-control-allow-headers":
            if should_inject_headers(value):
                injected = inject_sailfish_headers(value)
                # Convert list back to comma-separated string for Tornado
                # (inject_sailfish_headers returns a list, but Tornado expects a string)
                if isinstance(injected, list):
                    value = ", ".join(injected)
                else:
                    value = injected
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_tornado_cors]] Injected Sailfish headers: {value}",
                        log=False,
                    )

        # Call original set_header
        return original_set_header(self, name, value)

    tornado.web.RequestHandler.set_header = patched_set_header
    tornado.web.RequestHandler._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_tornado_cors]] Successfully patched Tornado RequestHandler.set_header",
            log=False,
        )


# Hook into on_finish for OTEL-style post-response emission
try:
    import tornado.web

    original_on_finish = tornado.web.RequestHandler.on_finish

    def patched_on_finish(self):
        """
        OTEL-STYLE: Emit network hop AFTER response is sent.
        Tornado calls on_finish() after the response is fully sent to client.
        """
        # Emit network hop if we captured endpoint_id
        endpoint_id = getattr(self, "_sf_endpoint_id", None)
        if endpoint_id is not None and endpoint_id >= 0:
            try:
                _, session_id = get_or_set_sf_trace_id()

                # Get captured request data
                req_headers = getattr(self, "_sf_request_headers", None)
                req_body = getattr(self, "_sf_request_body", None)

                # Capture response headers if enabled
                resp_headers = None
                if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                    try:
                        resp_headers = dict(self._headers)
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Tornado]] Captured response headers: {len(resp_headers)} headers",
                                log=False,
                            )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Tornado]] Failed to capture response headers: {e}",
                                log=False,
                            )

                # Capture response body if enabled
                resp_body = None
                if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                    try:
                        # Tornado stores written chunks in self._write_buffer
                        if hasattr(self, "_write_buffer") and self._write_buffer:
                            body_parts = [
                                chunk
                                for chunk in self._write_buffer
                                if isinstance(chunk, bytes)
                            ]
                            if body_parts:
                                full_body = b"".join(body_parts)
                                resp_body = full_body[:_RESPONSE_LIMIT_BYTES]
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Tornado]] Captured response body: {len(resp_body)} bytes",
                                        log=False,
                                    )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Tornado]] Failed to capture response body: {e}",
                                log=False,
                            )

                # Extract raw path and query string for C to parse
                raw_path = self.request.path  # e.g., "/log"
                # Tornado's request.query is the query string without '?'
                raw_query = (
                    self.request.query.encode("utf-8") if self.request.query else b""
                )  # e.g., b"foo=5"

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Tornado]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                        f"[[Tornado]] Emitted network hop: endpoint_id={endpoint_id} "
                        f"session={session_id}",
                        log=False,
                    )
            except Exception as e:  # noqa: BLE001 S110
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Tornado]] Failed to emit network hop: {e}", log=False)

        # Clear function span override for this request (ContextVar cleanup)
        try:
            clear_funcspan_override()
        except Exception:
            pass

        # CRITICAL: Clear C TLS to prevent stale data in thread pools
        try:
            clear_c_tls_parent_trace_id()
        except Exception:
            pass

        # CRITICAL: Clear outbound header base to prevent stale cached headers
        # ContextVar does NOT automatically clean up in thread pools - must clear explicitly
        try:
            clear_outbound_header_base()
        except Exception:
            pass

        # CRITICAL: Clear trace_id to ensure fresh generation for next request
        # Without this, get_or_set_sf_trace_id() reuses trace_id from previous request
        # causing X-Sf4-Prid to stay constant when no incoming X-Sf3-Rid header
        try:
            clear_trace_id()
        except Exception:
            pass

        # CRITICAL: Clear current request path to prevent stale data in thread pools
        try:
            clear_current_request_path()
        except Exception:
            pass

        return original_on_finish(self)

    tornado.web.RequestHandler.on_finish = patched_on_finish
except ImportError:
    pass
