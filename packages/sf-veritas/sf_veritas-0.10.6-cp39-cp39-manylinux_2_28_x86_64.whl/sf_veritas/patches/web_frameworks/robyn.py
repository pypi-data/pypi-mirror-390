"""
Robyn web framework patch for OTEL-style network hop capture.
Captures request/response headers and bodies when enabled via env vars.
"""

import functools
import inspect
import sys
import sysconfig
from functools import lru_cache
from threading import local
from typing import Any, Callable, Optional, Set

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
    clear_outbound_header_base,
    clear_trace_id,
    generate_new_trace_id,
    get_or_set_sf_trace_id,
    get_sf_trace_id,
    set_funcspan_override,
    set_outbound_header_base,
)
from ..constants import supported_network_verbs as HTTP_METHODS
from .cors_utils import inject_sailfish_headers, should_inject_headers
from .utils import _is_user_code, _unwrap_user_func, should_skip_route

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json


_stdlib = sysconfig.get_paths()["stdlib"]

_SKIP_TRACING_ATTR = "_sf_skip_tracing"

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Thread-local storage for request data (since we can't set attributes on Request object)
_request_data = local()


@lru_cache(maxsize=512)
def _is_user_code(path: Optional[str]) -> bool:
    """
    True only for “application” files (not stdlib or site-packages).
    """
    if not path or path.startswith("<"):
        return False
    if path.startswith(_stdlib):
        return False
    if "site-packages" in path or "dist-packages" in path:
        return False
    return True


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


def patch_robyn(routes_to_skip: Optional[list] = None):
    """
    OTEL-STYLE Robyn patch using lightweight wrappers + hooks.
    - Wrappers: Pre-register endpoints and store endpoint_id (minimal overhead)
    - Hooks: Capture request/response data and emit network hops
    Safe no-op if Robyn isn't installed.

    Args:
        routes_to_skip: Optional list of route patterns to skip (supports wildcards)
    """
    routes_to_skip = routes_to_skip or []

    try:
        import robyn
    except ImportError:
        return

    # Patch route decorators to wrap handlers
    for method_name in HTTP_METHODS:
        if not hasattr(robyn.Robyn, method_name):
            continue

        original_method = getattr(robyn.Robyn, method_name)

        def make_patched(orig):
            @functools.wraps(orig)
            def patched(self, path: str, *args, **kwargs):
                # Get original decorator
                decorator = orig(self, path, *args, **kwargs)

                def wrapper(fn):
                    # Check for @skip_network_tracing on the wrapped function BEFORE unwrapping
                    if getattr(fn, _SKIP_TRACING_ATTR, False):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn]] Skipping endpoint (marked with @skip_network_tracing): {fn.__name__ if hasattr(fn, '__name__') else fn}",
                                log=False,
                            )
                        return decorator(fn)

                    real_fn = _unwrap_user_func(fn)

                    # Check if endpoint should be traced
                    if not _should_trace_endpoint(real_fn):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn]] Skipping endpoint (not user code or Strawberry): {real_fn.__name__ if hasattr(real_fn, '__name__') else real_fn}",
                                log=False,
                            )
                        return decorator(fn)

                    # Check if route should be skipped based on wildcard patterns
                    if should_skip_route(path, routes_to_skip):
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn]] Skipping endpoint (route matches skip pattern): {path}",
                                log=False,
                            )
                        return decorator(fn)

                    # Pre-register endpoint if user code
                    endpoint_id = None
                    filename = real_fn.__code__.co_filename
                    if _is_user_code(filename):
                        line_no = real_fn.__code__.co_firstlineno
                        hop_key = (filename, line_no)

                        endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
                        if endpoint_id is None:
                            # Extract route pattern (Robyn uses the path parameter directly)
                            route_pattern = path

                            endpoint_id = register_endpoint(
                                line=str(line_no),
                                column="0",
                                name=real_fn.__name__,
                                entrypoint=filename,
                                route=route_pattern,
                            )
                            if endpoint_id >= 0:
                                _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Robyn]] Registered endpoint: {real_fn.__name__} @ {filename}:{line_no} route={route_pattern} (id={endpoint_id})",
                                        log=False,
                                    )

                    # Minimal wrapper: just store endpoint_id
                    @functools.wraps(fn)
                    async def minimal_wrapper(*a, **kw):
                        # Store endpoint_id in thread-local for after_request hook
                        if endpoint_id is not None:
                            _request_data.endpoint_id = endpoint_id
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Robyn]] Wrapper storing endpoint_id={endpoint_id} for {real_fn.__name__}",
                                    log=False,
                                )
                        # Call original handler
                        return await fn(*a, **kw)

                    return decorator(minimal_wrapper)

                return wrapper

            return patched

        setattr(robyn.Robyn, method_name, make_patched(original_method))

    original_init = robyn.Robyn.__init__

    def patched_init(self, *args, **kwargs):
        # Let Robyn initialize normally
        original_init(self, *args, **kwargs)

        # Install before_request hook for header propagation and request capture
        @self.before_request()
        async def _sf_before_request(request):
            """Capture trace header and request data before handler runs."""
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[Robyn]] Request object: {request}", log=False)
                print(f"[[Robyn]] Request type: {type(request)}", log=False)
                print("[[Robyn]] Request attributes and values:", log=False)
                for attr in dir(request):
                    if not attr.startswith("_"):
                        try:
                            value = getattr(request, attr)
                            print(f"  {attr} = {value}", log=False)
                        except Exception as e:
                            print(f"  {attr} = <error: {e}>", log=False)

            try:
                # 0. Capture path and query string for later use
                try:
                    if hasattr(request, "url"):
                        url = request.url
                        _request_data.path = getattr(url, "path", None)
                        query = getattr(url, "queries", None)
                        # queries might be a dict, convert to query string
                        if query:
                            _request_data.query = "&".join(
                                f"{k}={v}" for k, v in query.items()
                            ).encode("utf-8")
                        else:
                            _request_data.query = b""
                    else:
                        _request_data.path = None
                        _request_data.query = b""
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(f"[[Robyn]] Failed to capture path/query: {e}", log=False)

                headers = getattr(request, "headers", {})

                # PERFORMANCE: Single-pass bytes-level header scan (similar to FastAPI)
                # Scan headers once on bytes, only decode what we need
                incoming_trace_raw = None  # bytes
                funcspan_raw = None  # bytes
                req_headers = None  # dict[str,str] only if capture enabled

                capture_req_headers = (
                    SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache
                )

                # 1. Header propagation and capture
                if hasattr(headers, "get_headers"):
                    try:
                        raw_headers = headers.get_headers()

                        if capture_req_headers:
                            # Build dict while scanning for special headers
                            tmp = {}
                            for k, v in raw_headers.items():
                                k_lower = k.lower() if isinstance(k, str) else k
                                v_val = (
                                    v[0] if isinstance(v, list) and len(v) > 0 else v
                                )

                                if k_lower == SAILFISH_TRACING_HEADER.lower():
                                    incoming_trace_raw = (
                                        v_val
                                        if isinstance(v_val, bytes)
                                        else v_val.encode("latin-1")
                                    )
                                elif k_lower == "x-sf3-functionspancaptureoverride":
                                    funcspan_raw = (
                                        v_val
                                        if isinstance(v_val, bytes)
                                        else v_val.encode("latin-1")
                                    )

                                tmp[k] = v_val
                            req_headers = tmp
                        else:
                            # Just scan for special headers
                            for k, v in raw_headers.items():
                                k_lower = k.lower() if isinstance(k, str) else k
                                v_val = (
                                    v[0] if isinstance(v, list) and len(v) > 0 else v
                                )

                                if k_lower == SAILFISH_TRACING_HEADER.lower():
                                    incoming_trace_raw = (
                                        v_val
                                        if isinstance(v_val, bytes)
                                        else v_val.encode("latin-1")
                                    )
                                elif k_lower == "x-sf3-functionspancaptureoverride":
                                    funcspan_raw = (
                                        v_val
                                        if isinstance(v_val, bytes)
                                        else v_val.encode("latin-1")
                                    )

                        # Store headers for later
                        if req_headers:
                            _request_data.headers = req_headers
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Robyn]] Captured request headers: {len(req_headers)} headers",
                                    log=False,
                                )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn]] Failed to capture request headers: {e}",
                                log=False,
                            )
                elif hasattr(headers, "get"):
                    # Fallback to dict-like interface
                    try:
                        hdr = headers.get(SAILFISH_TRACING_HEADER)
                        if hdr:
                            incoming_trace_raw = (
                                hdr if isinstance(hdr, bytes) else hdr.encode("latin-1")
                            )

                        funcspan_hdr = headers.get("X-Sf3-FunctionSpanCaptureOverride")
                        if funcspan_hdr:
                            funcspan_raw = (
                                funcspan_hdr
                                if isinstance(funcspan_hdr, bytes)
                                else funcspan_hdr.encode("latin-1")
                            )
                    except (KeyError, TypeError):
                        pass

                # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
                if incoming_trace_raw:
                    # Incoming X-Sf3-Rid header provided - use it
                    incoming_trace = (
                        incoming_trace_raw.decode("latin-1")
                        if isinstance(incoming_trace_raw, bytes)
                        else incoming_trace_raw
                    )
                    get_or_set_sf_trace_id(
                        incoming_trace, is_associated_with_inbound_request=True
                    )
                else:
                    # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
                    generate_new_trace_id()

                # Optional funcspan override (decode only if present)
                funcspan_override_header = (
                    (
                        funcspan_raw.decode("latin-1")
                        if isinstance(funcspan_raw, bytes)
                        else funcspan_raw
                    )
                    if funcspan_raw
                    else None
                )

                if funcspan_override_header:
                    try:
                        set_funcspan_override(funcspan_override_header)
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn.before_request]] Set function span override from header: {funcspan_override_header}",
                                log=False,
                            )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn.before_request]] Failed to set function span override: {e}",
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
                                    f"[[Robyn.before_request]] Initialized outbound header base (base={base_trace[:16]}...)",
                                    log=False,
                                )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Robyn.before_request]] Failed to initialize outbound header base: {e}",
                            log=False,
                        )

                # 2. Capture request body if enabled (only if capturing network hops)
                if SF_NETWORKHOP_CAPTURE_ENABLED and SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
                    try:
                        body = getattr(request, "body", None)
                        if body:
                            if isinstance(body, bytes):
                                req_body = body[:_REQUEST_LIMIT_BYTES]
                            elif isinstance(body, str):
                                req_body = body.encode("utf-8")[:_REQUEST_LIMIT_BYTES]
                            else:
                                req_body = None
                            _request_data.body = req_body
                            if SF_DEBUG and req_body:
                                print(
                                    f"[[Robyn]] Request body capture: {len(req_body)} bytes",
                                    log=False,
                                )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn]] Failed to capture request body: {e}",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Robyn]] before_request error: {e}", log=False)

            return request

        # Install after_request hook for OTEL-style emission
        @self.after_request()
        async def _sf_after_request(response):
            """OTEL-STYLE: Emit network hop AFTER response is built."""
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[Robyn]] Response object: {response}", log=False)
                print(f"[[Robyn]] Response type: {type(response)}", log=False)
                print("[[Robyn]] Response attributes and values:", log=False)
                for attr in dir(response):
                    if not attr.startswith("_"):
                        try:
                            value = getattr(response, attr)
                            print(f"  {attr} = {value}", log=False)
                        except Exception as e:
                            print(f"  {attr} = <error: {e}>", log=False)

            try:
                # OPTIMIZATION: Skip ALL capture infrastructure if not capturing network hops
                # We still needed to set up trace_id and outbound header base in before_request
                # (for outbound call tracing), but we can skip all request/response capture overhead
                if SF_NETWORKHOP_CAPTURE_ENABLED:
                    # Get endpoint_id from thread-local storage (set by wrapper)
                    endpoint_id = getattr(_request_data, "endpoint_id", None)

                    if endpoint_id is not None and endpoint_id >= 0:
                        # OPTIMIZATION: Use get_sf_trace_id() directly instead of get_or_set_sf_trace_id()
                        # Trace ID is GUARANTEED to be set at request start
                        # This saves time by avoiding tuple unpacking and conditional logic
                        session_id = get_sf_trace_id()

                        # Get captured request data from thread-local storage
                        req_headers = getattr(_request_data, "headers", None)
                        req_body = getattr(_request_data, "body", None)

                        # Capture response headers if enabled (from Response object)
                        resp_headers = None
                        if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                            try:
                                if hasattr(response, "headers"):
                                    resp_hdrs = response.headers
                                    if hasattr(resp_hdrs, "get_headers"):
                                        raw_resp_headers = resp_hdrs.get_headers()
                                        resp_headers = (
                                            {
                                                k: (
                                                    v[0]
                                                    if isinstance(v, list)
                                                    and len(v) > 0
                                                    else v
                                                )
                                                for k, v in raw_resp_headers.items()
                                            }
                                            if raw_resp_headers
                                            else None
                                        )
                                    elif isinstance(resp_hdrs, dict):
                                        resp_headers = dict(resp_hdrs)
                                    if SF_DEBUG and resp_headers:
                                        print(
                                            f"[[Robyn]] Captured response headers: {len(resp_headers)} headers",
                                            log=False,
                                        )
                            except Exception as e:
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Robyn]] Failed to capture response headers: {e}",
                                        log=False,
                                    )

                        # Capture response body if enabled
                        resp_body = None
                        if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                            try:
                                # Response object should have body or description
                                if hasattr(response, "body"):
                                    body = response.body
                                elif hasattr(response, "description"):
                                    body = response.description
                                else:
                                    body = None

                                if body:
                                    if isinstance(body, bytes):
                                        resp_body = body[:_RESPONSE_LIMIT_BYTES]
                                    elif isinstance(body, str):
                                        resp_body = body.encode("utf-8")[
                                            :_RESPONSE_LIMIT_BYTES
                                        ]
                                    elif isinstance(body, dict):
                                        if HAS_ORJSON:
                                            resp_body = orjson.dumps(body).encode(
                                                "utf-8"
                                            )[:_RESPONSE_LIMIT_BYTES]
                                        else:
                                            resp_body = json.dumps(body).encode(
                                                "utf-8"
                                            )[:_RESPONSE_LIMIT_BYTES]
                                    if SF_DEBUG and resp_body:
                                        print(
                                            f"[[Robyn]] Captured response body: {len(resp_body)} bytes",
                                            log=False,
                                        )
                            except Exception as e:
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Robyn]] Failed to capture response body: {e}",
                                        log=False,
                                    )

                        # Extract raw path and query string for C to parse (from thread-local request data)
                        raw_path = getattr(_request_data, "path", None)
                        raw_query = getattr(_request_data, "query", b"")

                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Robyn]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                                f"[[Robyn]] Emitted network hop: endpoint_id={endpoint_id} "
                                f"session={session_id}",
                                log=False,
                            )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Robyn]] after_request error: {e}", log=False)
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

            return response

        # Install exception handler
        @self.exception
        async def _sf_exception_handler(error):
            """Capture all exceptions and forward to custom_excepthook."""
            try:
                custom_excepthook(type(error), error, error.__traceback__)
            except Exception:
                pass
            # Re-raise so Robyn's default error handler processes it
            raise error

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_robyn]] OTEL-style hooks installed (no handler wrapping)",
                log=False,
            )

    robyn.Robyn.__init__ = patched_init

    # Apply CORS patching
    patch_robyn_cors()

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_robyn]] OTEL-style patch applied", log=False)


def patch_robyn_cors():
    """
    Patch Robyn's ALLOW_CORS function to automatically inject Sailfish headers.

    SAFE: Only modifies CORS if ALLOW_CORS is used by the application.
    This ensures Sailfish tracing headers are included in CORS allow-headers.
    """
    try:
        import robyn
    except ImportError:
        # Robyn or cors_utils not available, skip patching
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_robyn_cors]] Robyn or cors_utils not found, skipping",
                log=False,
            )
        return

    # Check if ALLOW_CORS exists
    if not hasattr(robyn, "ALLOW_CORS"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_robyn_cors]] ALLOW_CORS not found in Robyn, skipping",
                log=False,
            )
        return

    # Check if already patched
    if hasattr(robyn.ALLOW_CORS, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_robyn_cors]] Already patched, skipping", log=False)
        return

    original_allow_cors = robyn.ALLOW_CORS

    def patched_allow_cors(app, origins=None, **kwargs):
        """
        Patched ALLOW_CORS that injects Sailfish headers into allowed headers.

        Robyn's ALLOW_CORS signature varies by version, but typically:
        - ALLOW_CORS(app, origins) or
        - ALLOW_CORS(app, origins=..., allow_headers=..., ...)
        """
        # Try to intercept allow_headers parameter if present
        allow_headers = kwargs.get("allow_headers", None)

        if should_inject_headers(allow_headers):
            kwargs["allow_headers"] = inject_sailfish_headers(allow_headers)
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_robyn_cors]] Injected Sailfish headers into Robyn CORS",
                    log=False,
                )

        # Call original ALLOW_CORS with potentially modified headers
        return original_allow_cors(app, origins, **kwargs)

    # Replace ALLOW_CORS with patched version
    robyn.ALLOW_CORS = patched_allow_cors
    robyn.ALLOW_CORS._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_robyn_cors]] Successfully patched Robyn ALLOW_CORS",
            log=False,
        )
