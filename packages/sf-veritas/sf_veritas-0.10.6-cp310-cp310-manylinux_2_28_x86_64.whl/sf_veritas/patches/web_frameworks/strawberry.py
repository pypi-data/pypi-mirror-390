import inspect
import logging
import sys
import traceback
from importlib.util import find_spec
from typing import Any, Callable, Set, Tuple

from ... import app_config
from ...custom_excepthook import custom_excepthook
from ...env_vars import (
    CAPTURE_STRAWBERRY_ERRORS_WITH_DATA,
    PRINT_CONFIGURATION_STATUSES,
    SF_DEBUG,
    SF_NETWORKHOP_CAPTURE_REQUEST_BODY,
    SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS,
    SF_NETWORKHOP_CAPTURE_RESPONSE_BODY,
    SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS,
    SF_NETWORKHOP_REQUEST_LIMIT_MB,
    SF_NETWORKHOP_RESPONSE_LIMIT_MB,
    STRAWBERRY_DEBUG,
)
from ...fast_network_hop import (
    fast_send_network_hop,
    fast_send_network_hop_fast,
    register_endpoint,
)
from ...thread_local import get_or_set_sf_trace_id
from ...transmit_exception_to_sailfish import transmit_exception_to_sailfish
from .utils import _is_user_code, _unwrap_user_func

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json


logger = logging.getLogger(__name__)

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Track if Strawberry has already been patched to prevent multiple patches
_is_strawberry_patched = False


# Cache for function definition line numbers (keyed by code object id)
_FUNCTION_DEF_LINE_CACHE: dict[int, int] = {}


def _get_function_def_line(frame):
    """
    Get the line number of the 'def' statement, skipping decorators.

    Python's co_firstlineno includes decorators, so we need to scan the source
    to find the actual function definition line.

    PERFORMANCE: Results are cached by code object ID, so the file I/O only
    happens once per function (first request). Subsequent requests are instant.
    """
    code_id = id(frame.f_code)

    # Check cache first - this is the fast path for all requests after the first
    if code_id in _FUNCTION_DEF_LINE_CACHE:
        return _FUNCTION_DEF_LINE_CACHE[code_id]

    # Cache miss - do the expensive source file lookup
    try:
        # Get source lines for this code object (SLOW: reads file from disk)
        source_lines, start_line = inspect.getsourcelines(frame.f_code)

        # Find the first line that starts with 'def' or 'async def'
        for i, line in enumerate(source_lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("async def "):
                def_line = start_line + i
                # Cache the result for next time
                _FUNCTION_DEF_LINE_CACHE[code_id] = def_line
                return def_line

        # Fallback: return co_firstlineno if we can't find def
        result = frame.f_code.co_firstlineno
        _FUNCTION_DEF_LINE_CACHE[code_id] = result
        return result
    except Exception:
        # If anything fails, fallback to co_firstlineno
        result = frame.f_code.co_firstlineno
        _FUNCTION_DEF_LINE_CACHE[code_id] = result
        return result


def get_extension():
    from strawberry.extensions import SchemaExtension

    class CustomErrorHandlingExtension(SchemaExtension):
        def __init__(self, *, execution_context):
            self.execution_context = execution_context

        def on_request_start(self):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("Starting GraphQL request", log=False)

        def on_request_end(self):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("Ending GraphQL request", log=False)
            if not self.execution_context.errors:
                return
            for error in self.execution_context.errors:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"Handling GraphQL error: {error}", log=False)
                custom_excepthook(type(error), error, error.__traceback__)

        def on_validation_start(self):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("Starting validation of GraphQL request", log=False)

        def on_validation_end(self):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("Ending validation of GraphQL request", log=False)

        def on_execution_start(self):
            if SF_DEBUG and app_config._interceptors_initialized:
                print("Starting execution of GraphQL request", log=False)

        def on_resolver_start(self, resolver, obj, info, **kwargs):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"Starting resolver {resolver.__name__}", log=False)

        def on_resolver_end(self, resolver, obj, info, **kwargs):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"Ending resolver {resolver.__name__}", log=False)

        def on_error(self, error: Exception):
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"Handling error in resolver: {error}", log=False)
            custom_excepthook(type(error), error, error.__traceback__)

    return CustomErrorHandlingExtension


def get_network_hop_extension() -> "type[SchemaExtension]":
    """
    Strawberry SchemaExtension that emits a collectNetworkHops mutation for the
    *first* user-land frame executed inside every resolver (sync or async).
    """

    from strawberry.extensions import SchemaExtension

    # --------------------------------------------------------------------- #
    # Helper predicates
    # --------------------------------------------------------------------- #
    # Extended dig:  __wrapped__, closure cells *and* common attribute names
    # --------------------------------------------------------------------- #
    # Extension class
    # --------------------------------------------------------------------- #
    class NetworkHopExtension(SchemaExtension):
        supports_sync = supports_async = True
        _sent: Set[Tuple[str, int]] = set()  # class-level: de-dupe per request

        def __init__(self, *, execution_context):
            super().__init__(execution_context=execution_context)
            self._captured_endpoints = (
                []
            )  # Store endpoint info for post-response emission
            self._request_data = {}  # Store request headers/body
            self._response_data = {}  # Store response headers/body

        # ---------------- internal capture helper ---------------- #
        def _capture(self, frame, info):
            """OTEL-STYLE: Capture endpoint metadata and pre-register."""
            filename = frame.f_code.co_filename
            func_name = frame.f_code.co_name

            # Get the actual function definition line (skipping decorators)
            line_no = _get_function_def_line(frame)

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Strawberry]] _capture: {func_name} @ {filename} "
                    f"co_firstlineno={frame.f_code.co_firstlineno} -> def_line={line_no}",
                    log=False,
                )
            if (filename, line_no) in NetworkHopExtension._sent:
                return

            hop_key = (filename, line_no)

            # Pre-register endpoint if not already registered
            endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
            if endpoint_id is None:
                endpoint_id = register_endpoint(
                    line=str(line_no),
                    column="0",
                    name=func_name,
                    entrypoint=filename,
                    route=None,
                )
                if endpoint_id >= 0:
                    _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Strawberry]] Registered resolver: {func_name} @ "
                            f"{filename}:{line_no} (id={endpoint_id})",
                            log=False,
                        )

            # Store for on_request_end to emit
            self._captured_endpoints.append(
                {
                    "filename": filename,
                    "line": line_no,
                    "name": func_name,
                    "endpoint_id": endpoint_id,
                }
            )
            NetworkHopExtension._sent.add((filename, line_no))

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Strawberry]] Captured resolver: {func_name} "
                    f"({filename}:{line_no}) endpoint_id={endpoint_id}",
                    log=False,
                )

        # ---------------- tracer factory ---------------- #
        def _make_tracer(self, info):
            def tracer(frame, event, arg):
                if event.startswith("c_"):
                    return
                if event == "call":
                    if _is_user_code(frame.f_code.co_filename):
                        self._capture(frame, info)
                        sys.setprofile(None)
                        return
                    return tracer  # keep tracing until we hit user code

            return tracer

        # ---------------- request/response capture ---------------- #
        def on_request_start(self):
            """Capture GraphQL request data when request starts."""
            # IMPORTANT: Clear captured endpoints from previous requests
            # SchemaExtension instances may be reused across requests
            self._captured_endpoints = []
            self._request_data = {}
            self._response_data = {}

            if (
                SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS
                or SF_NETWORKHOP_CAPTURE_REQUEST_BODY
            ):
                try:
                    # Access the GraphQL query from execution context
                    if (
                        SF_NETWORKHOP_CAPTURE_REQUEST_BODY
                        and self.execution_context.query
                    ):

                        query_data = {
                            "query": self.execution_context.query,
                            "variables": self.execution_context.variables or {},
                            "operation_name": self.execution_context.operation_name,
                        }
                        # Convert to JSON string and limit size
                        if HAS_ORJSON:
                            query_str = orjson.dumps(query_data)[:_REQUEST_LIMIT_BYTES]
                        else:
                            query_str = json.dumps(query_data)[:_REQUEST_LIMIT_BYTES]
                        self._request_data["body"] = query_str.encode("utf-8")
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Strawberry]] Captured GraphQL query: {len(query_str)} chars",
                                log=False,
                            )

                    # Try to capture HTTP headers if available (depends on integration)
                    if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
                        # For Django/Flask integrations, headers might be in context
                        if hasattr(self.execution_context, "context"):
                            ctx = self.execution_context.context
                            if hasattr(ctx, "request") and hasattr(
                                ctx.request, "headers"
                            ):
                                self._request_data["headers"] = dict(
                                    ctx.request.headers
                                )
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Strawberry]] Captured {len(self._request_data['headers'])} request headers",
                                        log=False,
                                    )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Strawberry]] Failed to capture request data: {e}",
                            log=False,
                        )

        # ---------------- wrappers ---------------- #
        def resolve(self, _next, root, info, *args, **kwargs):
            user_fn = _unwrap_user_func(_next)
            tracer = self._make_tracer(info)
            sys.setprofile(tracer)
            try:
                return _next(root, info, *args, **kwargs)
            finally:
                sys.setprofile(None)  # safety-net

        async def resolve_async(self, _next, root, info, *args, **kwargs):
            user_fn = _unwrap_user_func(_next)
            tracer = self._make_tracer(info)
            sys.setprofile(tracer)
            try:
                return await _next(root, info, *args, **kwargs)
            finally:
                sys.setprofile(None)

        # ---------------- OTEL-STYLE: Emit after request completes ---------------- #
        def on_request_end(self):
            """Capture response data and emit network hops AFTER GraphQL response is built."""
            # Capture response data first
            if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY and self.execution_context.result:
                try:
                    # GraphQL result includes data and errors
                    result_data = {
                        "data": (
                            self.execution_context.result.data
                            if self.execution_context.result.data
                            else None
                        ),
                        "errors": (
                            [str(e) for e in self.execution_context.result.errors]
                            if self.execution_context.result.errors
                            else None
                        ),
                    }
                    if HAS_ORJSON:
                        result_str = orjson.dumps(result_data, default=str)[
                            :_RESPONSE_LIMIT_BYTES
                        ]
                    else:
                        result_str = json.dumps(result_data, default=str)[
                            :_RESPONSE_LIMIT_BYTES
                        ]
                    self._response_data["body"] = result_str.encode("utf-8")
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Strawberry]] Captured GraphQL result: {len(result_str)} chars",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Strawberry]] Failed to capture response data: {e}",
                            log=False,
                        )

            # Get captured data
            req_headers = self._request_data.get("headers")
            req_body = self._request_data.get("body")
            resp_headers = self._response_data.get(
                "headers"
            )  # Not typically available in GraphQL
            resp_body = self._response_data.get("body")

            # Emit network hops for all captured resolvers
            for endpoint_info in self._captured_endpoints:
                endpoint_id = endpoint_info.get("endpoint_id")

                try:
                    _, session_id = get_or_set_sf_trace_id()

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Strawberry]] Emitting hop for {endpoint_info['name']}: "
                            f"req_headers={'present' if req_headers else 'None'}, "
                            f"req_body={len(req_body) if req_body else 0} bytes, "
                            f"resp_body={len(resp_body) if resp_body else 0} bytes",
                            log=False,
                        )

                    # Extract raw path and query string for C to parse (if available from context)
                    raw_path = None
                    raw_query = b""
                    try:
                        if hasattr(self.execution_context, "context"):
                            ctx = self.execution_context.context
                            if hasattr(ctx, "request"):
                                req = ctx.request
                                # Try to get path - different frameworks have different attributes
                                if hasattr(req, "path"):
                                    raw_path = str(req.path)
                                elif hasattr(req, "url") and hasattr(req.url, "path"):
                                    raw_path = str(req.url.path)

                                # Try to get query string
                                if hasattr(req, "query_string"):
                                    raw_query = (
                                        req.query_string
                                        if isinstance(req.query_string, bytes)
                                        else req.query_string.encode("utf-8")
                                    )
                                elif (
                                    hasattr(req, "META") and "QUERY_STRING" in req.META
                                ):
                                    raw_query = req.META["QUERY_STRING"].encode("utf-8")
                    except Exception as e:
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Strawberry]] Failed to extract path/query: {e}",
                                log=False,
                            )

                    # Use fast path if C extension available
                    if endpoint_id is not None and endpoint_id >= 0:
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
                                f"[[Strawberry]] Emitted network hop (fast path): {endpoint_info['name']} "
                                f"endpoint_id={endpoint_id} session={session_id}",
                                log=False,
                            )
                    else:
                        # Fallback to old Python API (doesn't support body/header capture)
                        fast_send_network_hop(
                            session_id=session_id,
                            line=str(endpoint_info["line"]),
                            column="0",
                            name=endpoint_info["name"],
                            entrypoint=endpoint_info["filename"],
                        )
                        if SF_DEBUG and app_config._interceptors_initialized:
                            print(
                                f"[[Strawberry]] Emitted network hop (fallback): {endpoint_info['name']} "
                                f"session={session_id}",
                                log=False,
                            )
                except Exception as e:  # noqa: BLE001 S110
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Strawberry]] Failed to emit network hop: {e}", log=False
                        )

    return NetworkHopExtension


def patch_strawberry_module(strawberry):
    """Patch Strawberry to ensure exceptions go through the custom excepthook."""
    global _is_strawberry_patched
    if _is_strawberry_patched:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[DEBUG]] Strawberry has already been patched, skipping. [[/DEBUG]]",
                log=False,
            )
        return

    try:
        # Backup the original execute method from Strawberry
        original_execute = strawberry.execution.execute.execute

        async def custom_execute(*args, **kwargs):
            try:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[DEBUG]] Executing patched Strawberry execute function. [[/DEBUG]]",
                        log=False,
                    )
                return await original_execute(*args, **kwargs)
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        "[[DEBUG]] Intercepted exception in Strawberry execute. [[/DEBUG]]",
                        log=False,
                    )
                # Invoke custom excepthook globally
                sys.excepthook(type(e), e, e.__traceback__)
                raise

        # Replace Strawberry's execute function with the patched version
        strawberry.execution.execute.execute = custom_execute
        _is_strawberry_patched = True
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[DEBUG]] Successfully patched Strawberry execute function. [[/DEBUG]]",
                log=False,
            )
    except Exception as error:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[DEBUG]] Failed to patch Strawberry: {error}. [[/DEBUG]]", log=False
            )


class CustomImportHook:
    """Import hook to intercept the import of 'strawberry' modules."""

    def find_spec(self, fullname, path, target=None):
        global _is_strawberry_patched
        if fullname == "strawberry" and not _is_strawberry_patched:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[DEBUG]] Intercepting import of {fullname}. [[/DEBUG]]",
                    log=False,
                )
            return find_spec(fullname)
        if fullname.startswith("strawberry_django"):
            return None  # Let default import handle strawberry_django

    def exec_module(self, module):
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[DEBUG]] Executing module: {module.__name__}. [[/DEBUG]]", log=False
            )
        # Execute the module normally
        module_spec = module.__spec__
        if module_spec and module_spec.loader:
            module_spec.loader.exec_module(module)
        # Once strawberry is loaded, patch it
        if module.__name__ == "strawberry" and not _is_strawberry_patched:
            patch_strawberry_module(module)


def patch_schema():
    """Patch strawberry.Schema to include both Sailfish and NetworkHop extensions by default."""
    try:
        import strawberry

        original_schema_init = strawberry.Schema.__init__

        def patched_schema_init(self, *args, extensions=None, **kwargs):
            if extensions is None:
                extensions = []

            # Add the custom error handling extension
            sailfish_ext = get_extension()
            if sailfish_ext not in extensions:
                extensions.append(sailfish_ext)

            # Add the network hop extension
            hop_ext = get_network_hop_extension()
            if hop_ext not in extensions:
                extensions.append(hop_ext)

            # Call the original constructor
            original_schema_init(self, *args, extensions=extensions, **kwargs)

            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[DEBUG]] Patched strawberry.Schema to include Sailfish & NetworkHop extensions. [[/DEBUG]]",
                    log=False,
                )

        # Apply the patch
        strawberry.Schema.__init__ = patched_schema_init

        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[DEBUG]] Successfully patched strawberry.Schema. [[/DEBUG]]",
                log=False,
            )
    except ImportError:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[DEBUG]] Strawberry is not installed. Skipping schema patching. [[/DEBUG]]",
                log=False,
            )


def patch_views():
    """
    Patch Strawberry view classes to capture and print request data on errors.
    This helps debug malformed requests when STRAWBERRY_DEBUG is enabled.
    Also transmits exceptions with full stack traces when CAPTURE_STRAWBERRY_ERRORS_WITH_DATA is enabled.
    """
    if not STRAWBERRY_DEBUG and not CAPTURE_STRAWBERRY_ERRORS_WITH_DATA:
        return  # Skip patching if neither debug mode nor capture mode is enabled

    try:
        # Try to import Strawberry Django view
        try:
            from strawberry.django.views import GraphQLView as DjangoGraphQLView

            _patch_view_class(DjangoGraphQLView, "Django")
        except ImportError:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[DEBUG]] Strawberry Django view not found. [[/DEBUG]]", log=False
                )

        # Try to import base async view (used by other integrations)
        try:
            from strawberry.http.async_base_view import AsyncBaseHTTPView

            _patch_async_base_view(AsyncBaseHTTPView)
        except ImportError:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[DEBUG]] Strawberry AsyncBaseHTTPView not found. [[/DEBUG]]",
                    log=False,
                )

    except Exception as e:
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[DEBUG]] Failed to patch Strawberry views: {e}. [[/DEBUG]]",
                log=False,
            )


def _patch_view_class(view_class, integration_name):
    """Patch a Strawberry view class to capture request data on errors."""
    if hasattr(view_class, "_sf_patched"):
        return  # Already patched

    original_dispatch = view_class.dispatch

    async def patched_dispatch(self, request, *args, **kwargs):
        # Capture raw request body before processing
        raw_body = None
        if STRAWBERRY_DEBUG or CAPTURE_STRAWBERRY_ERRORS_WITH_DATA:
            try:
                raw_body = request.body if hasattr(request, "body") else None
            except Exception:
                pass

        try:
            return await original_dispatch(self, request, *args, **kwargs)
        except Exception as e:
            if (
                STRAWBERRY_DEBUG or CAPTURE_STRAWBERRY_ERRORS_WITH_DATA
            ) and raw_body is not None:
                _print_request_debug_info(raw_body, e, integration_name)
            raise

    view_class.dispatch = patched_dispatch
    view_class._sf_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            f"[[DEBUG]] Patched Strawberry {integration_name} view for error debugging. [[/DEBUG]]",
            log=False,
        )


def _patch_async_base_view(view_class):
    """Patch AsyncBaseHTTPView to capture request data on parse errors."""
    if hasattr(view_class, "_sf_parse_patched"):
        return  # Already patched

    original_parse = view_class.parse_http_body

    async def patched_parse_http_body(self, request_adapter):
        # Capture raw body before parsing (but avoid consuming the stream twice)
        raw_body = None
        if STRAWBERRY_DEBUG or CAPTURE_STRAWBERRY_ERRORS_WITH_DATA:
            try:
                # Read the body once
                raw_body = await request_adapter.get_body()

                # Patch request_adapter.get_body to return cached body
                # (body streams can only be read once)
                async def cached_get_body():
                    return raw_body

                request_adapter.get_body = cached_get_body
            except Exception:
                pass

        try:
            return await original_parse(self, request_adapter)
        except Exception as e:
            logger.info("=" * 20 + " <STRAWBERRY> " + "=" * 20)
            logger.error(e)
            logger.info("=" * 20 + " </STRAWBERRY> " + "=" * 20)
            if (
                STRAWBERRY_DEBUG or CAPTURE_STRAWBERRY_ERRORS_WITH_DATA
            ) and raw_body is not None:
                _print_request_debug_info(raw_body, e, "AsyncBaseHTTPView")
            raise

    view_class.parse_http_body = patched_parse_http_body
    view_class._sf_parse_patched = True

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            "[[DEBUG]] Patched Strawberry AsyncBaseHTTPView.parse_http_body for error debugging. [[/DEBUG]]",
            log=False,
        )


def _count_traceback_frames(tb):
    """Count the number of frames in a traceback."""
    count = 0
    while tb is not None:
        count += 1
        tb = tb.tb_next
    return count


def _print_request_debug_info(raw_body, exception, source):
    """Print debug information about the request that caused an error."""

    # Transmit exception to Sailfish with full stack trace if enabled
    if CAPTURE_STRAWBERRY_ERRORS_WITH_DATA:
        try:
            # Verify that the exception has a traceback attached
            if (
                not hasattr(exception, "__traceback__")
                or exception.__traceback__ is None
            ):
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[STRAWBERRY_DEBUG]] WARNING: Exception {type(exception).__name__} has no __traceback__ attribute!",
                        log=False,
                    )
            else:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[STRAWBERRY_DEBUG]] Exception has traceback with {_count_traceback_frames(exception.__traceback__)} frames",
                        log=False,
                    )

            transmit_exception_to_sailfish(exception, force_transmit=False)
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[STRAWBERRY_DEBUG]] Transmitted exception to Sailfish: {type(exception).__name__}",
                    log=False,
                )
        except Exception as transmit_err:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[STRAWBERRY_DEBUG]] Failed to transmit exception: {transmit_err}",
                    log=False,
                )

                print(
                    f"[[STRAWBERRY_DEBUG]] Transmission error traceback:\n{traceback.format_exc()}",
                    log=False,
                )

    # Print debug info if STRAWBERRY_DEBUG is enabled
    if not STRAWBERRY_DEBUG:
        return  # Skip printing if debug mode is disabled

    print("\n" + "=" * 80, log=False)
    print(f"[[STRAWBERRY_DEBUG]] Error in {source}", log=False)
    print("=" * 80, log=False)

    # Print the exception
    print(f"\nException: {type(exception).__name__}: {exception}", log=False)
    print("\nTraceback:", log=False)
    print(traceback.format_exc(), log=False)

    # Print raw body
    print("\n" + "-" * 80, log=False)
    print("Raw HTTP Body (bytes):", log=False)
    print("-" * 80, log=False)
    if isinstance(raw_body, bytes):
        print(f"Length: {len(raw_body)} bytes", log=False)
        print(f"Raw: {raw_body!r}", log=False)

        # Try to decode and pretty-print as JSON
        try:
            decoded = raw_body.decode("utf-8")
            print(f"\nDecoded (UTF-8): {decoded}", log=False)

            # Try to parse as JSON
            try:
                if HAS_ORJSON:
                    parsed = orjson.loads(decoded)
                else:
                    parsed = json.loads(decoded)
                print(f"\nParsed JSON (type: {type(parsed).__name__}):", log=False)
                if HAS_ORJSON:
                    parsed = print(orjson.dumps(parsed, indent=2), log=False)
                else:
                    parsed = print(json.dumps(parsed, indent=2), log=False)
            except json.JSONDecodeError as json_err:
                print(f"\nFailed to parse as JSON: {json_err}", log=False)
        except UnicodeDecodeError as decode_err:
            print(f"\nFailed to decode as UTF-8: {decode_err}", log=False)
    else:
        print(f"Body type: {type(raw_body).__name__}", log=False)
        print(f"Body: {raw_body!r}", log=False)

    print("\n" + "=" * 80, log=False)
    print("[[/STRAWBERRY_DEBUG]]", log=False)
    print("=" * 80 + "\n", log=False)


def patch_strawberry():
    """
    Main entry point for patching Strawberry GraphQL.
    Applies both schema extensions and error debugging patches.
    """
    patch_schema()
    patch_views()
