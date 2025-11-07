"""
Klein (Twisted web framework) patch for OTEL-style network hop capture.
Captures request/response headers and bodies when enabled via env vars.
"""

import functools
import inspect
from typing import List, Optional

from ... import _sffuncspan_config, app_config
from ...constants import SAILFISH_TRACING_HEADER
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
from ...thread_local import get_or_set_sf_trace_id
from .utils import _is_user_code, _unwrap_user_func, should_skip_route

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Routes to skip (set by patch_klein)
_ROUTES_TO_SKIP = []


def patch_klein(routes_to_skip: Optional[List[str]] = None):
    """
    OTEL-STYLE Klein patch:
    • Pre-registers endpoints on first route decoration
    • Captures request headers/body if enabled
    • Emits network hop AFTER handler completes (zero-overhead)
    • Captures response headers/body if enabled
    • Funnels exceptions through custom_excepthook
    No-op if Klein isn't installed.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        import klein
    except ImportError:
        return

    original_route = klein.Klein.route

    def patched_route(self, *args, **kwargs):
        # Grab Klein's decorator for this pattern
        original_decorator = original_route(self, *args, **kwargs)

        def new_decorator(fn):
            real_fn = _unwrap_user_func(fn)

            # Skip non-user code
            code = getattr(real_fn, "__code__", None)
            if not code or not _is_user_code(code.co_filename):
                return original_decorator(fn)

            filename = code.co_filename
            line_no = code.co_firstlineno
            fn_name = real_fn.__name__
            hop_key = (filename, line_no)

            # Get route pattern from args (first arg after self is usually the path)
            route_pattern = args[0] if args else None

            # Check if route should be skipped
            if route_pattern and should_skip_route(route_pattern, _ROUTES_TO_SKIP):
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Klein]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                        log=False,
                    )
                return original_decorator(fn)

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
                            f"[[Klein]] Registered endpoint: {fn_name} @ {filename}:{line_no} (id={endpoint_id})",
                            log=False,
                        )

            # Check if async or sync
            is_async = inspect.iscoroutinefunction(real_fn)

            if is_async:

                @functools.wraps(fn)
                async def wrapped_async(request, *f_args, **f_kwargs):
                    # 1. Trace-id propagation
                    header = request.getHeader(SAILFISH_TRACING_HEADER)
                    if header:
                        get_or_set_sf_trace_id(
                            header, is_associated_with_inbound_request=True
                        )

                    # Check for function span capture override header (highest priority!)
                    funcspan_override_header = request.getHeader(
                        "X-Sf3-FunctionSpanCaptureOverride"
                    )
                    if funcspan_override_header:
                        try:
                            _sffuncspan_config.set_thread_override(
                                funcspan_override_header
                            )
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein.async]] Set function span override from header: {funcspan_override_header}",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein.async]] Failed to set function span override: {e}",
                                    log=False,
                                )

                    # 2. Capture request headers if enabled
                    req_headers = None
                    if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
                        try:
                            # Klein/Twisted request.requestHeaders is a Headers object
                            req_headers = dict(
                                request.requestHeaders.getAllRawHeaders()
                            )
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Captured request headers: {len(req_headers)} headers",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture request headers: {e}",
                                    log=False,
                                )

                    # 3. Capture request body if enabled
                    req_body = None
                    if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
                        try:
                            # Klein/Twisted request.content is a file-like object
                            body = request.content.read(_REQUEST_LIMIT_BYTES)
                            request.content.seek(0)  # Reset for handler
                            req_body = body if body else None
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Request body capture: {len(body) if body else 0} bytes (method={request.method})",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture request body: {e}",
                                    log=False,
                                )

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Klein]] Captured endpoint: {fn_name} ({filename}:{line_no}) endpoint_id={endpoint_id}",
                            log=False,
                        )

                    # 4. Call handler and capture exceptions
                    response = None
                    try:
                        response = await fn(request, *f_args, **f_kwargs)
                    except Exception as exc:
                        custom_excepthook(type(exc), exc, exc.__traceback__)
                        raise

                    # 5. Capture response headers if enabled
                    resp_headers = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                        try:
                            # Klein/Twisted request.responseHeaders is a Headers object
                            resp_headers = dict(
                                request.responseHeaders.getAllRawHeaders()
                            )
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Captured response headers: {len(resp_headers)} headers",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture response headers: {e}",
                                    log=False,
                                )

                    # 6. Capture response body if enabled
                    resp_body = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                        try:
                            # Klein handlers return bytes directly
                            if isinstance(response, bytes):
                                resp_body = response[:_RESPONSE_LIMIT_BYTES]
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Klein]] Captured response body: {len(resp_body)} bytes",
                                        log=False,
                                    )
                            elif isinstance(response, str):
                                resp_body = response.encode("utf-8")[
                                    :_RESPONSE_LIMIT_BYTES
                                ]
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Klein]] Captured response body (str): {len(resp_body)} bytes",
                                        log=False,
                                    )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture response body: {e}",
                                    log=False,
                                )

                    # 7. OTEL-STYLE: Emit network hop AFTER handler completes
                    if endpoint_id is not None and endpoint_id >= 0:
                        try:
                            _, session_id = get_or_set_sf_trace_id()

                            # Extract raw path and query string for C to parse
                            raw_path = (
                                request.path
                                if isinstance(request.path, str)
                                else request.path.decode("utf-8")
                            )
                            # Twisted request.uri includes full URI with query string (bytes)
                            uri_parts = request.uri.split(b"?", 1)
                            raw_query = uri_parts[1] if len(uri_parts) > 1 else b""

                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                                    f"[[Klein]] Emitted network hop: endpoint_id={endpoint_id} "
                                    f"session={session_id}",
                                    log=False,
                                )
                        except Exception as e:  # noqa: BLE001 S110
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to emit network hop: {e}",
                                    log=False,
                                )

                    # Clear function span override for this request (thread-local cleanup)
                    try:
                        _sffuncspan_config.clear_thread_override()
                    except Exception:
                        pass

                    return response

                return original_decorator(wrapped_async)
            else:

                @functools.wraps(fn)
                def wrapped_sync(request, *f_args, **f_kwargs):
                    # 1. Trace-id propagation
                    header = request.getHeader(SAILFISH_TRACING_HEADER)
                    if header:
                        get_or_set_sf_trace_id(
                            header, is_associated_with_inbound_request=True
                        )

                    # Check for function span capture override header (highest priority!)
                    funcspan_override_header = request.getHeader(
                        "X-Sf3-FunctionSpanCaptureOverride"
                    )
                    if funcspan_override_header:
                        try:
                            _sffuncspan_config.set_thread_override(
                                funcspan_override_header
                            )
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein.sync]] Set function span override from header: {funcspan_override_header}",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein.sync]] Failed to set function span override: {e}",
                                    log=False,
                                )

                    # 2. Capture request headers if enabled
                    req_headers = None
                    if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
                        try:
                            # Klein/Twisted request.requestHeaders is a Headers object
                            req_headers = dict(
                                request.requestHeaders.getAllRawHeaders()
                            )
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Captured request headers: {len(req_headers)} headers",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture request headers: {e}",
                                    log=False,
                                )

                    # 3. Capture request body if enabled
                    req_body = None
                    if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
                        try:
                            # Klein/Twisted request.content is a file-like object
                            body = request.content.read(_REQUEST_LIMIT_BYTES)
                            request.content.seek(0)  # Reset for handler
                            req_body = body if body else None
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Request body capture: {len(body) if body else 0} bytes (method={request.method})",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture request body: {e}",
                                    log=False,
                                )

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Klein]] Captured endpoint: {fn_name} ({filename}:{line_no}) endpoint_id={endpoint_id}",
                            log=False,
                        )

                    # 4. Call handler and capture exceptions
                    response = None
                    try:
                        response = fn(request, *f_args, **f_kwargs)
                    except Exception as exc:
                        custom_excepthook(type(exc), exc, exc.__traceback__)
                        raise

                    # 5. Capture response headers if enabled
                    resp_headers = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                        try:
                            # Klein/Twisted request.responseHeaders is a Headers object
                            resp_headers = dict(
                                request.responseHeaders.getAllRawHeaders()
                            )
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Captured response headers: {len(resp_headers)} headers",
                                    log=False,
                                )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture response headers: {e}",
                                    log=False,
                                )

                    # 6. Capture response body if enabled
                    resp_body = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                        try:
                            # Klein handlers return bytes directly
                            if isinstance(response, bytes):
                                resp_body = response[:_RESPONSE_LIMIT_BYTES]
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Klein]] Captured response body: {len(resp_body)} bytes",
                                        log=False,
                                    )
                            elif isinstance(response, str):
                                resp_body = response.encode("utf-8")[
                                    :_RESPONSE_LIMIT_BYTES
                                ]
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Klein]] Captured response body (str): {len(resp_body)} bytes",
                                        log=False,
                                    )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to capture response body: {e}",
                                    log=False,
                                )

                    # 7. OTEL-STYLE: Emit network hop AFTER handler completes
                    if endpoint_id is not None and endpoint_id >= 0:
                        try:
                            _, session_id = get_or_set_sf_trace_id()

                            # Extract raw path and query string for C to parse
                            raw_path = (
                                request.path
                                if isinstance(request.path, str)
                                else request.path.decode("utf-8")
                            )
                            # Twisted request.uri includes full URI with query string (bytes)
                            uri_parts = request.uri.split(b"?", 1)
                            raw_query = uri_parts[1] if len(uri_parts) > 1 else b""

                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                                    f"[[Klein]] Emitted network hop: endpoint_id={endpoint_id} "
                                    f"session={session_id}",
                                    log=False,
                                )
                        except Exception as e:  # noqa: BLE001 S110
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Klein]] Failed to emit network hop: {e}",
                                    log=False,
                                )

                    # Clear function span override for this request (thread-local cleanup)
                    try:
                        _sffuncspan_config.clear_thread_override()
                    except Exception:
                        pass

                    return response

                return original_decorator(wrapped_sync)

        return new_decorator

    klein.Klein.route = patched_route

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_klein]] OTEL-style route patch applied", log=False)
