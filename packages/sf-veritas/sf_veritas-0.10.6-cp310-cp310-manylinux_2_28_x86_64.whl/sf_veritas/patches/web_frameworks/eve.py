from functools import wraps
from typing import Callable, List, Optional, Set, Tuple

from ... import _sffuncspan_config, app_config
from ...constants import (
    FUNCSPAN_OVERRIDE_HEADER_BYTES,
    SAILFISH_TRACING_HEADER,
    SAILFISH_TRACING_HEADER_BYTES,
)
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
    set_outbound_header_base,
)
from .cors_utils import inject_sailfish_headers, should_inject_headers
from .utils import _is_user_code, _unwrap_user_func, should_skip_route  # shared helpers

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Routes to skip (set by patch_eve)
_ROUTES_TO_SKIP = []


# ──────────────────────────────────────────────────────────────
# OTEL-STYLE: Request hooks (before + after)
# ──────────────────────────────────────────────────────────────
def _install_request_hooks(app):
    from flask import g, request

    @app.before_request
    def _extract_sf_header():
        """OTEL-STYLE: Extract trace header and capture request data before handler."""
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(request.path)

        # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        rid = request.headers.get(SAILFISH_TRACING_HEADER)
        if rid:
            # Incoming X-Sf3-Rid header provided - use it
            get_or_set_sf_trace_id(rid, is_associated_with_inbound_request=True)
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # Check for function span capture override header (highest priority!)
        funcspan_override_header = request.headers.get(
            "X-Sf3-FunctionSpanCaptureOverride"
        )
        if funcspan_override_header:
            try:
                _sffuncspan_config.set_thread_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Eve.before_request]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Eve.before_request]] Failed to set function span override: {e}",
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
                            f"[[Eve.before_request]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Eve.before_request]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # Capture request headers if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
            try:
                req_headers = dict(request.headers)
                g._sf_request_headers = req_headers
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Eve]] Captured request headers: {len(req_headers)} headers",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Eve]] Failed to capture request headers: {e}", log=False)

        # Capture request body if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # Flask/Eve: request.data gives raw bytes
                body = request.get_data(cache=True)  # cache=True to not consume it
                if body:
                    req_body = body[:_REQUEST_LIMIT_BYTES]
                    g._sf_request_body = req_body
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Eve]] Request body capture: {len(req_body)} bytes",
                            log=False,
                        )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Eve]] Failed to capture request body: {e}", log=False)

    @app.after_request
    def _emit_network_hop(response):
        """
        OTEL-STYLE: Emit network hop AFTER response is built.
        Eve is Flask-based, so we use the same @after_request pattern.
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
                                f"[[Eve]] Captured response headers: {len(resp_headers)} headers",
                                log=False,
                            )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Eve]] Failed to capture response headers: {e}",
                                log=False,
                            )

                # Capture response body if enabled
                resp_body = None
                if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                    try:
                        # Flask/Eve response: get_data() returns bytes
                        body = response.get_data()
                        if body:
                            resp_body = body[:_RESPONSE_LIMIT_BYTES]
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Eve]] Captured response body: {len(resp_body)} bytes",
                                    log=False,
                                )
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Eve]] Failed to capture response body: {e}",
                                log=False,
                            )

                # Extract raw path and query string for C to parse
                raw_path = request.path  # e.g., "/log"
                raw_query = request.query_string  # Already bytes (e.g., b"foo=5")

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Eve]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                        f"[[Eve]] Emitted network hop: endpoint_id={endpoint_id} "
                        f"session={session_id}",
                        log=False,
                    )
            except Exception as e:  # noqa: BLE001 S110
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Eve]] Failed to emit network hop: {e}", log=False)

        # Clear function span override for this request (thread-local cleanup)
        try:
            _sffuncspan_config.clear_thread_override()
        except Exception:
            pass

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


# ──────────────────────────────────────────────────────────────
# OTEL-STYLE: Per-view endpoint metadata capture
# ──────────────────────────────────────────────────────────────
def _hop_wrapper(view_fn: Callable):
    """
    OTEL-STYLE: Pre-register endpoint and store endpoint_id in flask.g.
    Emission happens in @after_request hook with captured body/headers.
    """
    from flask import g

    real_fn = _unwrap_user_func(view_fn)

    # Skip Strawberry handlers – handled by Strawberry extension
    if real_fn.__module__.startswith("strawberry"):
        return view_fn

    code = getattr(real_fn, "__code__", None)
    if not code or not _is_user_code(code.co_filename):
        return view_fn

    hop_key = (code.co_filename, code.co_firstlineno)
    fn_name = real_fn.__name__
    filename = code.co_filename
    line_no = code.co_firstlineno

    # We'll check route at runtime in the wrapper since we need request context
    # Pre-register endpoint if user code
    endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
    if endpoint_id is None:
        # Note: route will be None here, will be passed at runtime
        endpoint_id = register_endpoint(
            line=str(line_no), column="0", name=fn_name, entrypoint=filename, route=None
        )
        if endpoint_id >= 0:
            _ENDPOINT_REGISTRY[hop_key] = endpoint_id
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Eve]] Registered endpoint: {fn_name} @ {filename}:{line_no} (id={endpoint_id})",
                    log=False,
                )

    @wraps(view_fn)
    def _wrapped(*args, **kwargs):
        from flask import request

        # Check if route should be skipped
        route_pattern = request.path
        if route_pattern and should_skip_route(route_pattern, _ROUTES_TO_SKIP):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Eve]] Skipping endpoint (route matches skip pattern): {route_pattern}",
                    log=False,
                )
            return view_fn(*args, **kwargs)

        # OTEL-STYLE: Store endpoint_id for after_request to emit
        if not hasattr(g, "_sf_endpoint_id"):
            g._sf_endpoint_id = endpoint_id

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Eve]] Captured endpoint: {fn_name} ({filename}:{line_no}) endpoint_id={endpoint_id}",
                    log=False,
                )

        return view_fn(*args, **kwargs)

    return _wrapped


def _patch_add_url_rule(cls):
    """
    Patch add_url_rule on *cls* (cls is Eve or Blueprint) so that the final
    stored endpoint function is wrapped *after* Flask has done its own
    bookkeeping.  This catches:
      • Eve resource endpoints created internally via register_resource()
      • Manual @app.route() decorators
      • Blueprints, CBVs, etc.
    """
    original_add = cls.add_url_rule

    def patched_add(
        self, rule, endpoint=None, view_func=None, **options
    ):  # noqa: ANN001
        # let Eve/Flask register the route first
        original_add(self, rule, endpoint=endpoint, view_func=view_func, **options)

        ep = endpoint or (view_func and view_func.__name__)
        if not ep:  # defensive
            return

        target = self.view_functions.get(ep)
        if callable(target):
            self.view_functions[ep] = _hop_wrapper(target)

    cls.add_url_rule = patched_add


# ──────────────────────────────────────────────────────────────
# Public entry-point
# ──────────────────────────────────────────────────────────────
def patch_eve(routes_to_skip: Optional[List[str]] = None):
    """
    • Adds ContextVar propagation middleware
    • Wraps every Eve endpoint (and Blueprint endpoints) to emit one hop
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        import eve
        from flask import Blueprint  # Eve relies on Flask blueprints
    except ImportError:
        return

    # Guard against double-patching
    if getattr(eve.Eve, "__sf_tracing_patched__", False):
        return

    # 1.  Patch Eve.add_url_rule *and* Blueprint.add_url_rule
    _patch_add_url_rule(eve.Eve)
    _patch_add_url_rule(Blueprint)

    # 2.  Patch Eve.__init__ to install request hooks
    #     Note: CORS patching is handled by patch_flask_cors() since Eve uses flask-cors
    original_init = eve.Eve.__init__

    def patched_init(self, import_name=None, settings=None, *args, **kwargs):
        # Call original init
        original_init(self, import_name, settings, *args, **kwargs)

        # Install request hooks
        _install_request_hooks(self)

    eve.Eve.__init__ = patched_init
    eve.Eve.__sf_tracing_patched__ = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_eve]] OTEL-style request hooks + hop wrapper installed (CORS patching handled by Flask)", log=False
        )
