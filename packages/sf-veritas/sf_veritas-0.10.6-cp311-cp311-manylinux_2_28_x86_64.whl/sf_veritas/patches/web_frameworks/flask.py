"""
Adds:
• before_request hook → ContextVar propagation (unchanged).
• global add_url_rule / Blueprint.add_url_rule patch →
  wraps every endpoint in a hop-emitting closure.
"""

from functools import wraps
from types import MethodType
from typing import Callable, List, Optional, Set, Tuple

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
from .utils import should_skip_route

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs (filename:line -> endpoint_id)
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Module-level variable for routes to skip (set by patch_flask)
_ROUTES_TO_SKIP = []

# ────────────────────────────────────────────────────────────────
#   shared helpers
# ────────────────────────────────────────────────────────────────
from .utils import _is_user_code, _unwrap_user_func  # cached helpers


def _make_hop_wrapper(
    fn: Callable,
    hop_key: Tuple[str, int],
    fn_name: str,
    filename: str,
    route: str = None,
):
    """
    OTEL-STYLE: Store endpoint metadata in flask.g during request.
    Emission happens in @after_request hook for zero-overhead.
    Pre-register endpoint on first wrap.
    """
    from flask import g

    # Check if route should be skipped
    if should_skip_route(route, _ROUTES_TO_SKIP):
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[Flask]] Skipping endpoint (route matches skip pattern): {route}",
                log=False,
            )
        # Return original function unwrapped - no telemetry
        return fn

    # Pre-register endpoint if not already registered
    endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
    if endpoint_id is None:
        endpoint_id = register_endpoint(
            line=str(hop_key[1]),
            column="0",
            name=fn_name,
            entrypoint=filename,
            route=route,
        )
        if endpoint_id >= 0:
            _ENDPOINT_REGISTRY[hop_key] = endpoint_id
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Flask]] Registered endpoint: {fn_name} @ {filename}:{hop_key[1]} (id={endpoint_id})",
                    log=False,
                )

    @wraps(fn)
    def _wrapped(*args, **kwargs):  # noqa: ANN001
        # OTEL-STYLE: Store endpoint_id for after_request to emit
        if not hasattr(g, "_sf_endpoint_id"):
            g._sf_endpoint_id = endpoint_id

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Flask]] Captured endpoint: {fn_name} ({filename}:{hop_key[1]}) endpoint_id={endpoint_id}",
                    log=False,
                )

        return fn(*args, **kwargs)

    return _wrapped


def _wrap_if_user_view(endpoint_fn: Callable, route: str = None):
    """
    Decide whether to wrap `endpoint_fn`. Returns the (possibly wrapped)
    callable.  Suppress wrapping for library code or Strawberry handlers.
    """
    real_fn = _unwrap_user_func(endpoint_fn)

    # Skip Strawberry GraphQL views – Strawberry extension owns them
    if real_fn.__module__.startswith("strawberry"):
        return endpoint_fn

    code = getattr(real_fn, "__code__", None)
    if not code or not _is_user_code(code.co_filename):
        return endpoint_fn

    hop_key = (code.co_filename, code.co_firstlineno)
    return _make_hop_wrapper(
        endpoint_fn, hop_key, real_fn.__name__, code.co_filename, route=route
    )


# ────────────────────────────────────────────────────────────────
#   Request hooks: before (header capture) + after (OTEL-style emission)
# ────────────────────────────────────────────────────────────────
def _install_request_hooks(app):
    from flask import g, request

    @app.before_request
    def _extract_sf_trace():
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(request.path)

        # 1. CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        hdr = request.headers.get(SAILFISH_TRACING_HEADER)
        if hdr:
            get_or_set_sf_trace_id(hdr, is_associated_with_inbound_request=True)
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # Optional funcspan override (highest priority!)
        funcspan_override_header = request.headers.get(
            "X-Sf3-FunctionSpanCaptureOverride"
        )
        if funcspan_override_header:
            try:
                set_funcspan_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Flask.before_request]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Flask.before_request]] Failed to set function span override: {e}",
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
                            f"[[Flask.before_request]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Flask.before_request]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

    @app.after_request
    def _emit_network_hop(response):
        """
        OTEL-STYLE: Emit network hop AFTER response is built.
        This ensures telemetry doesn't impact response time to client.
        Captures request/response headers and bodies if enabled.
        """
        endpoint_id = getattr(g, "_sf_endpoint_id", None)
        if endpoint_id is not None and endpoint_id >= 0:
            try:
                _, session_id = get_or_set_sf_trace_id()

                # Capture request headers if enabled
                req_headers = None
                if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
                    try:
                        req_headers = dict(request.headers)
                    except Exception:
                        pass

                # Capture request body if enabled
                req_body = None
                if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
                    try:
                        # Flask caches request.data, so this is safe
                        body = request.get_data()
                        if body and len(body) > 0:
                            req_body = body[:_REQUEST_LIMIT_BYTES]
                    except Exception:
                        pass

                # Capture response headers if enabled
                resp_headers = None
                if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                    try:
                        resp_headers = dict(response.headers)
                    except Exception:
                        pass

                # Capture response body if enabled
                resp_body = None
                if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                    try:
                        if hasattr(response, "get_data"):
                            body = response.get_data()
                            if body and len(body) > 0:
                                resp_body = body[:_RESPONSE_LIMIT_BYTES]
                    except Exception:
                        pass

                # Extract raw path and query string for C to parse
                raw_path = request.path  # e.g., "/log"
                raw_query = request.query_string  # e.g., b"foo=5"

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
                        f"[[Flask]] Emitted network hop: endpoint_id={endpoint_id} "
                        f"session={session_id}",
                        log=False,
                    )
            except Exception as e:  # noqa: BLE001 S110
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Flask]] Failed to emit network hop: {e}", log=False)

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

        # Clear function span override for this request (thread-local cleanup)
        try:
            _sffuncspan_config.clear_thread_override()
        except Exception:
            pass

        return response


# ────────────────────────────────────────────────────────────────
#   Monkey-patch Flask & Blueprint
# ────────────────────────────────────────────────────────────────
try:
    import flask
    from flask import Blueprint

    def _patch_add_url_rule(cls):
        """
        Patch *cls*.add_url_rule (cls is Flask or Blueprint) so the final
        stored view function is wrapped after Flask registers it.  Works for:
            • view_func positional
            • endpoint string lookup
            • CBV's as_view()
        """
        original_add = cls.add_url_rule

        def patched_add(
            self, rule, endpoint=None, view_func=None, **options
        ):  # noqa: ANN001
            # Resolve endpoint name
            ep_name = endpoint or (view_func and view_func.__name__)

            # Check if endpoint already registered
            already_registered = ep_name and ep_name in self.view_functions

            # If already registered, use existing function to avoid Flask's
            # "overwriting endpoint" assertion when same function is used for multiple routes
            if already_registered:
                view_func = self.view_functions[ep_name]

            # 1. Let Flask register the route
            original_add(self, rule, endpoint=endpoint, view_func=view_func, **options)

            # 2. Wrap only if this is a new endpoint registration
            if already_registered:
                return  # Already wrapped during first registration

            # This is a new endpoint, wrap it
            if not ep_name:
                return

            target = self.view_functions.get(ep_name)
            if not callable(target):
                return

            # 3. Wrap if user code (pass route pattern)
            wrapped = _wrap_if_user_view(target, route=rule)
            self.view_functions[ep_name] = wrapped

        cls.add_url_rule = patched_add

    def patch_flask(routes_to_skip: Optional[List[str]] = None):
        """
        OTEL-STYLE PURE ASYNC:
        • Installs before_request header propagation
        • Installs after_request for OTEL-style network hop emission
        • Wraps every endpoint to capture metadata (not emit)
        • Patches exception handlers for custom_excepthook
        """
        global _ROUTES_TO_SKIP
        _ROUTES_TO_SKIP = routes_to_skip or []

        if getattr(flask.Flask, "__sf_tracing_patched__", False):
            return  # idempotent

        # --- 1. Patch Flask.__init__ to add request hooks -----------
        original_flask_init = flask.Flask.__init__

        def patched_init(self, *args, **kwargs):
            original_flask_init(self, *args, **kwargs)
            _install_request_hooks(self)

        flask.Flask.__init__ = patched_init

        # --- 2. Patch add_url_rule for both Flask and Blueprint -----------------
        _patch_add_url_rule(flask.Flask)
        _patch_add_url_rule(Blueprint)

        # --- 3. Patch exception handlers once on the class ----------------------
        _mw_path = "sf_veritas_exception_patch_applied"
        if not getattr(flask.Flask, _mw_path, False):
            orig_handle_exc = flask.Flask.handle_exception
            orig_handle_user_exc = flask.Flask.handle_user_exception

            def _patched_handle_exception(self, e):
                custom_excepthook(type(e), e, e.__traceback__)
                return orig_handle_exc(self, e)

            def _patched_handle_user_exception(self, e):
                custom_excepthook(type(e), e, e.__traceback__)
                return orig_handle_user_exc(self, e)

            flask.Flask.handle_exception = _patched_handle_exception  # 500 errors
            flask.Flask.handle_user_exception = (
                _patched_handle_user_exception  # HTTPExc.
            )

            setattr(flask.Flask, _mw_path, True)

        flask.Flask.__sf_tracing_patched__ = True

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_flask]] tracing hooks + exception capture installed", log=False
            )

    def patch_flask_cors():
        """
        Patch flask-cors to automatically inject Sailfish headers into CORS allow_headers.

        Patches:
        1. CORS class __init__ method to intercept allow_headers parameter
        2. CORS class init_app method for factory pattern support
        3. cross_origin decorator for route-specific CORS

        SAFE: Only modifies CORS if flask-cors is installed and used.
        Reference: https://corydolphin.com/flask-cors/extension/
        """
        # Import guard: only patch if flask-cors is installed
        try:
            from flask_cors import CORS, cross_origin
        except ImportError:
            # flask-cors not installed, skip patching
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[patch_flask_cors]] flask-cors not installed, skipping", log=False
                )
            return

        # Check if already patched to avoid double-patching
        if hasattr(CORS, "_sf_cors_patched"):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("[[patch_flask_cors]] Already patched, skipping", log=False)
            return

        # Save original methods
        original_cors_init = CORS.__init__
        original_init_app = getattr(CORS, 'init_app', None)

        # Patch CORS.__init__ (handles: CORS(app, allow_headers=["foo"]))
        def patched_cors_init(self, app=None, **kwargs):
            # Intercept and inject Sailfish headers into allow_headers
            if "allow_headers" in kwargs:
                original_headers = kwargs["allow_headers"]
                if should_inject_headers(original_headers):
                    injected_headers = inject_sailfish_headers(original_headers)
                    kwargs["allow_headers"] = injected_headers
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[patch_flask_cors]] Injected Sailfish headers into CORS.__init__: {injected_headers}",
                            log=False,
                        )

            # Call original init
            original_cors_init(self, app, **kwargs)

        # Patch CORS.init_app (handles factory pattern: cors = CORS(); cors.init_app(app, allow_headers=["foo"]))
        def patched_init_app(self, app, **kwargs):
            # Intercept and inject Sailfish headers into allow_headers
            if "allow_headers" in kwargs:
                original_headers = kwargs["allow_headers"]
                if should_inject_headers(original_headers):
                    injected_headers = inject_sailfish_headers(original_headers)
                    kwargs["allow_headers"] = injected_headers
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[patch_flask_cors]] Injected Sailfish headers into CORS.init_app: {injected_headers}",
                            log=False,
                        )

            # Call original init_app
            if original_init_app:
                original_init_app(self, app, **kwargs)

        # Apply patches to CORS class
        CORS.__init__ = patched_cors_init
        if original_init_app:
            CORS.init_app = patched_init_app
        CORS._sf_cors_patched = True

        # Patch cross_origin decorator (handles: @cross_origin(allow_headers=["foo"]))
        original_cross_origin = cross_origin

        def patched_cross_origin(*args, **kwargs):
            # Intercept and inject Sailfish headers into allow_headers
            if "allow_headers" in kwargs:
                original_headers = kwargs["allow_headers"]
                if should_inject_headers(original_headers):
                    injected_headers = inject_sailfish_headers(original_headers)
                    kwargs["allow_headers"] = injected_headers
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[patch_flask_cors]] Injected Sailfish headers into @cross_origin: {injected_headers}",
                            log=False,
                        )

            # Call original decorator
            return original_cross_origin(*args, **kwargs)

        # Replace the cross_origin function in the flask_cors module
        import flask_cors

        flask_cors.cross_origin = patched_cross_origin

        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_flask_cors]] Successfully patched flask-cors (CORS, init_app, cross_origin)", log=False)

    # Apply CORS patching when module is loaded
    patch_flask_cors()

except ImportError:  # Flask not installed

    def patch_flask(routes_to_skip: Optional[List[str]] = None):  # noqa: D401
        """No-op when Flask is absent."""
        return
