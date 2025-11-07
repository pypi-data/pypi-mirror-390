import asyncio
import inspect
import sys
from typing import List, Optional

from ... import _sffuncspan_config
from .cors_utils import inject_sailfish_headers, should_inject_headers
from .utils import _is_user_code, _unwrap_user_func, should_skip_route

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object  # fallback for non-Django environments

import traceback

from ... import app_config
from ...constants import (
    FUNCSPAN_OVERRIDE_HEADER_BYTES,
    SAILFISH_TRACING_HEADER,
    SAILFISH_TRACING_HEADER_BYTES,
)
from ...custom_excepthook import custom_excepthook
from ...env_vars import (
    PRINT_CONFIGURATION_STATUSES,
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

# Registry mapping view function id → endpoint_id (for fast C path)
_ENDPOINT_REGISTRY = {}

# Module-level variable for routes to skip (set by patch_django_middleware)
_ROUTES_TO_SKIP = []


def find_and_modify_output_wrapper():
    """
    Monkey-patch Django's OutputWrapper to always use the current sys.stdout/stderr
    instead of storing a reference at init time. This ensures Django management
    commands (like migrate) output is captured by our UnifiedInterceptor even if
    OutputWrapper was instantiated before setup_interceptors() ran.
    """
    if PRINT_CONFIGURATION_STATUSES:
        print("find_and_modify_output_wrapper", log=False)

    try:
        from django.core.management.base import OutputWrapper
    except ImportError:
        if PRINT_CONFIGURATION_STATUSES:
            print("Django not found; skipping OutputWrapper patch", log=False)
        return

    # Check if already patched (idempotent)
    if hasattr(OutputWrapper, "_sf_patched"):
        if PRINT_CONFIGURATION_STATUSES:
            print("OutputWrapper already patched; skipping", log=False)
        return

    # Save original methods
    _original_init = OutputWrapper.__init__
    _original_write = OutputWrapper.write

    def patched_init(self, out, ending="\n"):
        """Patched __init__ that tracks if this wrapper is wrapping stdout/stderr."""
        # Call original init
        _original_init(self, out, ending)
        # Track if this wrapper is for stdout or stderr (so we can redirect to current stream)
        self._sf_is_stdout = out is sys.stdout or out is sys.__stdout__
        self._sf_is_stderr = out is sys.stderr or out is sys.__stderr__
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[Django OutputWrapper] Created: stdout={self._sf_is_stdout}, stderr={self._sf_is_stderr}",
                log=False,
            )

    def patched_write(self, msg="", style_func=None, ending=None):
        """
        Patched write that uses CURRENT sys.stdout/stderr instead of the stored reference.
        This ensures our UnifiedInterceptor captures Django output.
        """
        # If this wrapper was created for stdout, redirect to CURRENT sys.stdout
        if getattr(self, "_sf_is_stdout", False):
            original_out = self._out
            self._out = sys.stdout
            try:
                return _original_write(self, msg, style_func, ending)
            finally:
                self._out = original_out

        # If this wrapper was created for stderr, redirect to CURRENT sys.stderr
        elif getattr(self, "_sf_is_stderr", False):
            original_out = self._out
            self._out = sys.stderr
            try:
                return _original_write(self, msg, style_func, ending)
            finally:
                self._out = original_out

        # Otherwise use original behavior
        return _original_write(self, msg, style_func, ending)

    # Apply patches
    OutputWrapper.__init__ = patched_init
    OutputWrapper.write = patched_write
    OutputWrapper._sf_patched = True

    if PRINT_CONFIGURATION_STATUSES:
        print("find_and_modify_output_wrapper...DONE (monkey-patched)", log=False)


class SailfishMiddleware(MiddlewareMixin):
    """
    • process_request   – capture inbound SAILFISH_TRACING_HEADER header.
    • process_view      – emit one NetworkHop per view (skip Strawberry).
    • __call__ override – last-chance catcher for uncaught exceptions.
    • got_request_exception signal – main hook for 500-level errors.
    • process_exception – fallback for view-raised exceptions.
    """

    # ------------------------------------------------------------------ #
    # 0 | Signal registration (called once at server start-up)
    # ------------------------------------------------------------------ #
    def __init__(self, get_response):
        super().__init__(get_response)

        # Attach to Django's global exception signal so we ALWAYS
        # see real exceptions that become HTTP-500 responses.
        from django.core.signals import got_request_exception

        got_request_exception.disconnect(  # avoid dupes on reload
            self._on_exception_signal, dispatch_uid="sf_veritas_signal"
        )
        got_request_exception.connect(
            self._on_exception_signal,
            weak=False,
            dispatch_uid="sf_veritas_signal",
        )

    # ------------------------------------------------------------------ #
    # 1 | Signal handler  ← FIXED
    # ------------------------------------------------------------------ #
    def _on_exception_signal(self, sender, request, **kwargs):
        """
        Handle django.core.signals.got_request_exception.

        The signal doesn't pass the exception object; per Django's own
        implementation (and Sentry's approach) we fetch it from
        sys.exc_info().
        """

        exc_type, exc_value, exc_tb = sys.exc_info()

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[SailfishMiddleware._on_exception_signal]] "
                f"exc_value={exc_value!r}",
                log=False,
            )

        if exc_value:
            custom_excepthook(exc_type, exc_value, exc_tb)

    # ------------------------------------------------------------------ #
    # 2 | Last-chance wrapper (rarely triggered in WSGI but free)
    # ------------------------------------------------------------------ #
    def __call__(self, request):
        try:
            return super().__call__(request)
        except Exception as exc:
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise  # preserve default Django 500

    # ------------------------------------------------------------------ #
    # 3 | Header capture
    # ------------------------------------------------------------------ #
    def process_request(self, request):
        # CRITICAL: Clear trace_id FIRST at request start to ensure fresh start
        # Django reuses threads, so we must clear the ContextVar from previous request
        try:
            clear_trace_id()
            clear_outbound_header_base()
            clear_c_tls_parent_trace_id()
            clear_current_request_path()
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[SailfishMiddleware.process_request]] Cleared all context at request start",
                    log=False,
                )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[SailfishMiddleware.process_request]] Failed to clear context: {e}",
                    log=False,
                )

        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(request.path)

        # PERFORMANCE: Single-pass bytes-level header scan (convert Django META to bytes for consistent scanning)
        # Django stores headers in META with HTTP_ prefix, scan once and extract what we need
        incoming_trace_raw = None
        funcspan_override_header = None

        # Django uses string headers in META, scan for our headers
        header_key = f"HTTP_{SAILFISH_TRACING_HEADER.upper().replace('-', '_')}"
        incoming_trace_raw = request.META.get(header_key)

        funcspan_override_key = "HTTP_X_SF3_FUNCTIONSPANCAPTUREOVERRIDE"
        funcspan_override_header = request.META.get(funcspan_override_key)

        # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        if incoming_trace_raw:
            # Incoming X-Sf3-Rid header provided - use it
            get_or_set_sf_trace_id(
                incoming_trace_raw, is_associated_with_inbound_request=True
            )
            if SF_DEBUG and app_config._interceptors_initialized:
                trace_id = get_sf_trace_id()
                print(
                    f"[[SailfishMiddleware.process_request]] "
                    f"Using incoming trace: {incoming_trace_raw} → trace_id={trace_id}",
                    log=False,
                )
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            new_trace = generate_new_trace_id()
            if SF_DEBUG and app_config._interceptors_initialized:
                trace_id = get_sf_trace_id()
                print(
                    f"[[SailfishMiddleware.process_request]] "
                    f"Generated new trace_id: {new_trace} → trace_id={trace_id}",
                    log=False,
                )

        # Optional funcspan override
        if funcspan_override_header:
            try:
                _sffuncspan_config.set_thread_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[SailfishMiddleware.process_request]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[SailfishMiddleware.process_request]] Failed to set function span override: {e}",
                        log=False,
                    )

        # Initialize outbound header base with parent trace ID
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
                            f"[[SailfishMiddleware.process_request]] Initialized outbound header base (base={base_trace[:16] if len(base_trace) > 16 else base_trace}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[SailfishMiddleware.process_request]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

    # ------------------------------------------------------------------ #
    # 4 | Network-hop emission  (unchanged)
    # ------------------------------------------------------------------ #
    def process_view(self, request, view_func, view_args, view_kwargs):
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[SailfishMiddleware.process_view]] view_func={view_func.__name__ if hasattr(view_func, '__name__') else view_func}, "
                f"path={request.path}",
                log=False,
            )

        module = getattr(view_func, "__module__", "")
        if module.startswith("strawberry"):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Django.process_view]] Skipping Strawberry GraphQL view",
                    log=False,
                )
            return None

        # Unwrap decorated views to get the actual user code
        # Django decorators (csrf_exempt, require_http_methods, etc.) wrap views
        actual_view = _unwrap_user_func(view_func)

        if actual_view is not view_func and SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[Django.process_view]] Unwrapped decorator: "
                f"{view_func.__name__} → {getattr(actual_view, '__name__', 'unknown')}",
                log=False,
            )

        # Get code object and verify it's user code
        code = getattr(actual_view, "__code__", None)
        if not code:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Django.process_view]] No code object for view_func", log=False
                )
            return None

        fname, lno = code.co_filename, code.co_firstlineno

        # The unwrap function already checks for user code, but double-check
        if not _is_user_code(fname):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[Django.process_view]] Not user code: {fname}", log=False)
            return None

        # Extract route pattern from Django's resolver
        route_pattern = None
        if hasattr(request, "resolver_match") and request.resolver_match:
            route_pattern = getattr(request.resolver_match, "route", None)

        # Check if route should be skipped
        if should_skip_route(route_pattern, _ROUTES_TO_SKIP):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Django.process_view]] Skipping view (route matches skip pattern): {route_pattern}",
                    log=False,
                )
            return None

        # Get or register endpoint_id (use actual_view for consistent tracking)
        view_id = id(actual_view)
        endpoint_id = _ENDPOINT_REGISTRY.get(view_id)

        if endpoint_id is None:
            # First time seeing this view - register it
            view_name = getattr(actual_view, "__name__", "unknown")
            endpoint_id = register_endpoint(
                line=str(lno),
                column="0",
                name=view_name,
                entrypoint=fname,
                route=route_pattern,
            )

            if endpoint_id >= 0:
                _ENDPOINT_REGISTRY[view_id] = endpoint_id
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Django]] Registered endpoint: {view_name} "
                        f"({fname}:{lno}) → id={endpoint_id}",
                        log=False,
                    )
            else:
                # Failed to register, don't track
                return None

        # Store endpoint_id for process_response()
        request._sf_endpoint_id = endpoint_id

        # Capture request headers if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
            try:
                # Django stores headers in request.META with HTTP_ prefix
                headers = {}
                for key, value in request.META.items():
                    if key.startswith("HTTP_"):
                        # Remove HTTP_ prefix and convert to standard format
                        header_name = key[5:].replace("_", "-")
                        headers[header_name] = str(value)
                    elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                        headers[key.replace("_", "-")] = str(value)
                request._sf_request_headers = headers
            except Exception:
                request._sf_request_headers = None

        # Capture request body if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # Read body (Django caches it, so this is safe)
                limit = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
                body = request.body if hasattr(request, "body") else b""
                if body and len(body) > limit:
                    body = body[:limit]
                request._sf_request_body = body if body else None
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Django]] Failed to capture request body: {e}", log=False)
                request._sf_request_body = None

        return None

    # ------------------------------------------------------------------ #
    # 5 | View-level exception hook (unchanged)
    # ------------------------------------------------------------------ #
    def process_response(self, request, response):
        """
        Emit network hop AFTER response is built (OTEL-style zero-overhead).
        Uses pre-registered endpoint_id for ultra-fast C path.
        Captures response headers/body if enabled.
        """
        endpoint_id = getattr(request, "_sf_endpoint_id", None)

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[SailfishMiddleware.process_response]] endpoint_id={endpoint_id}, "
                f"has_endpoint_attr={hasattr(request, '_sf_endpoint_id')}",
                log=False,
            )

        if endpoint_id is not None and endpoint_id >= 0:
            try:
                _, session_id = get_or_set_sf_trace_id()

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[SailfishMiddleware.process_response]] session_id={session_id}, "
                        f"endpoint_id={endpoint_id}, path={request.path}",
                        log=False,
                    )

                # Capture response headers if enabled
                resp_headers = None
                if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                    try:
                        resp_headers = dict(response.items())
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Django]] Failed to capture response headers: {e}",
                                log=False,
                            )

                # Capture response body if enabled
                resp_body = None
                if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                    try:
                        limit = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024
                        if hasattr(response, "content"):
                            resp_body = response.content[:limit]
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Django]] Failed to capture response body: {e}",
                                log=False,
                            )

                # Get request data if captured
                req_headers = getattr(request, "_sf_request_headers", None)
                req_body = getattr(request, "_sf_request_body", None)

                # Extract raw path and query string for C to parse
                raw_path = request.path  # e.g., "/log"
                raw_query = request.META.get("QUERY_STRING", "").encode(
                    "utf-8"
                )  # e.g., b"foo=5"

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Django]] About to emit network hop: endpoint_id={endpoint_id}, "
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
                        f"[[Django]] Emitted network hop: endpoint_id={endpoint_id} "
                        f"session={session_id}",
                        log=False,
                    )
            except Exception as e:  # noqa: BLE001 S110
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Django]] Failed to emit network hop: {e}", log=False)

                    traceback.print_exc()

        # Clear function span override for this request (thread-local cleanup)
        try:
            _sffuncspan_config.clear_thread_override()
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

        return response

    # ------------------------------------------------------------------ #
    # 6 | View-level exception hook (unchanged)
    # ------------------------------------------------------------------ #
    def process_exception(self, request, exception):
        print("[[SailfishMiddleware.process_exception]]", log=False)
        custom_excepthook(type(exception), exception, exception.__traceback__)


# --------------------------------------------------------------------------- #
# Helper – patch django.core.wsgi.get_wsgi_application once
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Helper – patch django.core.asgi.get_asgi_application once
# --------------------------------------------------------------------------- #
def _patch_get_asgi_application() -> None:
    """
    Replace ``django.core.asgi.get_asgi_application`` with a wrapper that:

    1. Runs ``django.setup()`` (as the original does),
    2. **Then** injects ``SailfishMiddleware`` into *settings.MIDDLEWARE*
       *after* settings are configured but *before* the first ``ASGIHandler``
       is built,
    3. Returns the handler (ASGI handlers handle exceptions internally).

    This mirrors the WSGI patching approach.
    """
    try:
        from django.core import asgi as _asgi_mod
    except ImportError:  # pragma: no cover
        return

    if getattr(_asgi_mod, "_sf_patched", False):
        return  # idempotent

    _orig_get_asgi = _asgi_mod.get_asgi_application
    _MW_PATH = "sf_veritas.patches.web_frameworks.django.SailfishMiddleware"

    def _sf_get_asgi_application(*args, **kwargs):
        # --- Step 1: exactly replicate original behaviour -----------------
        import django

        django.setup(set_prefix=False)  # configures settings & apps

        # --- Step 2: inject middleware *now* (settings are configured) ----
        from django.conf import settings

        if (
            hasattr(settings, "MIDDLEWARE")
            and isinstance(settings.MIDDLEWARE, list)
            and _MW_PATH not in settings.MIDDLEWARE
        ):
            settings.MIDDLEWARE.insert(0, _MW_PATH)
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[_patch_get_asgi_application]] Injected {_MW_PATH}", log=False)

        # --- Step 2.5: inject CORS headers if configured ----
        if hasattr(settings, 'CORS_ALLOW_HEADERS'):
            original_headers = settings.CORS_ALLOW_HEADERS

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_patch_get_asgi_application]] Found CORS_ALLOW_HEADERS: {original_headers}",
                    log=False,
                )

            if should_inject_headers(original_headers):
                patched_headers = inject_sailfish_headers(original_headers)
                settings.CORS_ALLOW_HEADERS = patched_headers

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[_patch_get_asgi_application]] Injected Sailfish headers into CORS_ALLOW_HEADERS: {patched_headers}",
                        log=False,
                    )

        # --- Step 3: build and return ASGI handler ----
        return _orig_get_asgi(*args, **kwargs)

    _asgi_mod.get_asgi_application = _sf_get_asgi_application
    _asgi_mod._sf_patched = True


# --------------------------------------------------------------------------- #
# Helper – patch django.core.wsgi.get_wsgi_application once
# --------------------------------------------------------------------------- #
def _patch_get_wsgi_application() -> None:
    """
    Replace ``django.core.wsgi.get_wsgi_application`` with a wrapper that:

    1. Runs ``django.setup()`` (as the original does),
    2. **Then** injects ``SailfishMiddleware`` into *settings.MIDDLEWARE*
       *after* settings are configured but *before* the first ``WSGIHandler``
       is built,
    3. Wraps the returned handler in our ``CustomExceptionMiddleware`` so we
       still have a last-chance catcher outside Django's stack.

    This mirrors the flow used by Sentry's Django integration.
    """
    try:
        from django.core import wsgi as _wsgi_mod
    except ImportError:  # pragma: no cover
        return

    if getattr(_wsgi_mod, "_sf_patched", False):
        return  # idempotent

    _orig_get_wsgi = _wsgi_mod.get_wsgi_application
    _MW_PATH = "sf_veritas.patches.web_frameworks.django.SailfishMiddleware"

    def _sf_get_wsgi_application(*args, **kwargs):
        # --- Step 1: exactly replicate original behaviour -----------------
        import django

        django.setup(set_prefix=False)  # configures settings & apps

        # --- Step 2: inject middleware *now* (settings are configured) ----
        from django.conf import settings

        if (
            hasattr(settings, "MIDDLEWARE")
            and isinstance(settings.MIDDLEWARE, list)
            and _MW_PATH not in settings.MIDDLEWARE
        ):
            settings.MIDDLEWARE.insert(0, _MW_PATH)

        # --- Step 2.5: inject CORS headers if configured ----
        if hasattr(settings, 'CORS_ALLOW_HEADERS'):
            original_headers = settings.CORS_ALLOW_HEADERS

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[_patch_get_wsgi_application]] Found CORS_ALLOW_HEADERS: {original_headers}",
                    log=False,
                )

            if should_inject_headers(original_headers):
                patched_headers = inject_sailfish_headers(original_headers)
                settings.CORS_ALLOW_HEADERS = patched_headers

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[_patch_get_wsgi_application]] Injected Sailfish headers into CORS_ALLOW_HEADERS: {patched_headers}",
                        log=False,
                    )

        # --- Step 3: build handler and wrap for last-chance exceptions ----
        from django.core.handlers.wsgi import WSGIHandler
        from sf_veritas.patches.web_frameworks.django import CustomExceptionMiddleware

        handler = WSGIHandler()
        return CustomExceptionMiddleware(handler)

    _wsgi_mod.get_wsgi_application = _sf_get_wsgi_application
    _wsgi_mod._sf_patched = True


def patch_django_middleware(routes_to_skip: Optional[List[str]] = None) -> None:
    """
    Public entry-point called by ``setup_interceptors``.

    • Inserts ``SailfishMiddleware`` for *already-configured* settings
      (run-server or ASGI).
    • Patches ``get_wsgi_application`` so *future* WSGI handlers created
      by third-party code inherit the middleware without relying on a
      configured settings object at import time.
    """
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured
    except ImportError:  # Django not installed
        return

    _MW_PATH = "sf_veritas.patches.web_frameworks.django.SailfishMiddleware"

    # ---------- If settings are *already* configured, patch immediately ---
    try:
        if settings.configured and isinstance(
            getattr(settings, "MIDDLEWARE", None), list
        ):
            if _MW_PATH not in settings.MIDDLEWARE:
                settings.MIDDLEWARE.insert(0, _MW_PATH)
    except ImproperlyConfigured:
        # Settings not yet configured – safe to ignore; the WSGI patch below
        # will handle insertion once ``django.setup()`` runs.
        pass

    # ---------- Always patch get_wsgi/asgi_application (idempotent) ------------
    _patch_get_wsgi_application()
    _patch_get_asgi_application()

    # ---------- Patch CORS to inject Sailfish headers (idempotent) ------------
    patch_django_cors()

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_django_middleware]] Sailfish Django integration ready", log=False
        )


class CustomExceptionMiddleware:
    """
    A universal last-chance exception wrapper that works for either
    • ASGI call signature:   (scope, receive, send)  → coroutine
    • WSGI call signature:   (environ, start_response) → iterable
    Every un-handled exception is funneled through ``custom_excepthook`` once.
    """

    def __init__(self, app):
        self.app = app

    # ------------------------------------------------------------------ #
    # Dispatcher – routes ASGI vs WSGI based on arity / argument shape
    # ------------------------------------------------------------------ #
    def __call__(self, *args, **kwargs):
        if len(args) == 3:
            # Heuristic: (scope, receive, send) for ASGI
            return self._asgi_call(*args)  # returns coroutine
        # Else assume classic WSGI: (environ, start_response)
        return self._wsgi_call(*args)  # returns iterable

    # ------------------------------------------------------------------ #
    # ASGI branch
    # ------------------------------------------------------------------ #
    async def _asgi_call(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception as exc:  # noqa: BLE001
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise
        finally:
            # CRITICAL: Clear C TLS to prevent stale data in thread pools
            try:
                clear_c_tls_parent_trace_id()
            except Exception:
                pass

            # CRITICAL: Clear outbound header base to prevent stale cached headers
            try:
                clear_outbound_header_base()
            except Exception:
                pass

            # CRITICAL: Clear trace_id to ensure fresh generation for next request
            try:
                clear_trace_id()
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    # WSGI branch
    # ------------------------------------------------------------------ #
    def _wsgi_call(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception as exc:  # noqa: BLE001
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise
        finally:
            # CRITICAL: Clear C TLS to prevent stale data in thread pools
            try:
                clear_c_tls_parent_trace_id()
            except Exception:
                pass

            # CRITICAL: Clear outbound header base to prevent stale cached headers
            try:
                clear_outbound_header_base()
            except Exception:
                pass

            # CRITICAL: Clear trace_id to ensure fresh generation for next request
            try:
                clear_trace_id()
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    # Delegate attribute access so the wrapped app still behaves normally
    # ------------------------------------------------------------------ #
    def __getattr__(self, attr):
        return getattr(self.app, attr)


# --------------------------------------------------------------------------- #
# CORS Header Injection – django-cors-headers
# --------------------------------------------------------------------------- #
def patch_django_cors():
    """
    Patch django-cors-headers to automatically inject Sailfish headers.

    Two-pronged approach:
    1. Directly modify Django settings.CORS_ALLOW_HEADERS if already configured
    2. Patch corsheaders.conf property to inject headers dynamically

    SAFE: Only modifies CORS if django-cors-headers is installed and configured.
    """
    try:
        from django.conf import settings
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_django_cors]] Django not available, skipping",
                log=False,
            )
        return

    try:
        from corsheaders import conf as cors_conf
    except ImportError:
        # django-cors-headers not installed, skip patching
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[patch_django_cors]] django-cors-headers not installed, skipping",
                log=False,
            )
        return

    # Check if already patched
    if hasattr(cors_conf, "_sf_cors_patched"):
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[patch_django_cors]] Already patched, skipping", log=False)
        return

    # APPROACH 1: Directly modify Django settings if CORS is configured
    try:
        if hasattr(settings, 'CORS_ALLOW_HEADERS'):
            original_headers = settings.CORS_ALLOW_HEADERS

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[patch_django_cors]] Found CORS_ALLOW_HEADERS in settings: {original_headers}",
                    log=False,
                )

            if should_inject_headers(original_headers):
                patched_headers = inject_sailfish_headers(original_headers)
                settings.CORS_ALLOW_HEADERS = patched_headers

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[patch_django_cors]] Modified settings.CORS_ALLOW_HEADERS to: {patched_headers}",
                        log=False,
                    )
    except Exception as e:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(f"[[patch_django_cors]] Failed to modify settings: {e}", log=False)

    # APPROACH 2: Patch the Conf class property for dynamic access
    try:
        conf_class = type(cors_conf)

        if hasattr(conf_class, 'CORS_ALLOW_HEADERS'):
            original_property = getattr(conf_class, 'CORS_ALLOW_HEADERS')

            if isinstance(original_property, property):
                original_fget = original_property.fget

                def patched_fget(self):
                    original_headers = original_fget(self)

                    if should_inject_headers(original_headers):
                        patched_headers = inject_sailfish_headers(original_headers)

                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[patch_django_cors]] Property access: injected headers -> {patched_headers}",
                                log=False,
                            )

                        return patched_headers

                    return original_headers

                setattr(
                    conf_class,
                    'CORS_ALLOW_HEADERS',
                    property(patched_fget, original_property.fset, original_property.fdel)
                )

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[patch_django_cors]] Successfully patched CORS_ALLOW_HEADERS property",
                        log=False,
                    )
    except Exception as e:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(f"[[patch_django_cors]] Failed to patch property: {e}", log=False)

    cors_conf._sf_cors_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[patch_django_cors]] Successfully patched django-cors-headers", log=False
        )
