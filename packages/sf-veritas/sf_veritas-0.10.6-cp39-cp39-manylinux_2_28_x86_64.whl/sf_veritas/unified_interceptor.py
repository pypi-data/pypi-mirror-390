import atexit
import builtins
import functools
import inspect
import logging
import os
import signal
import sys
import threading
from types import ModuleType
from typing import Dict, List, Optional, Union

from pydantic import validate_call

from . import app_config
from .custom_excepthook import (
    custom_excepthook,
    custom_thread_excepthook,
    start_profiling,
)
from .custom_log_handler import CustomLogHandler
from .env_vars import (
    LOG_LEVEL,
    PRINT_CONFIGURATION_STATUSES,
    SF_DEBUG,
    SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES,
    SF_DISABLE_PARENT_DEATH_SIGNAL,
    SF_PARENT_MONITOR_INTERVAL_MS,
)
from .exception_metaclass import PatchedException
from .interceptors import PrintInterceptor
from .local_env_detect import set_sf_is_local_flag
from .patches.network_libraries import patch_all_http_clients
from .patches.threading import patch_threading
from .patches.web_frameworks import patch_web_frameworks
from .shutdown_flag import set_shutdown_flag
from .thread_local import (
    _thread_locals,
    get_or_set_sf_trace_id,
    get_reentrancy_guard_sys_stdout_active,
)
from .timeutil import TimeSync

# Optional native fast path for prints (C extension)
try:
    from . import _sffastlog  # provides init_print() and print_()

    _FAST_OK = True
except Exception:
    _sffastlog = None
    _FAST_OK = False

_FAST_PRINT_READY = False  # one-time guard for native print init

# Optional native fast path for service operations (C extension)
try:
    from . import _sfservice  # provides service_identifier(), collect_metadata(), etc.

    _SFSERVICE_OK = True
except Exception:
    _sfservice = None
    _SFSERVICE_OK = False

_SFSERVICE_READY = False  # one-time guard for native service init

# Optional native fast path for function spans (C extension)
try:
    import sf_veritas._sffuncspan as _sffuncspan

    from .function_span_profiler import init_function_span_profiler

    _FUNCSPAN_OK = True
except Exception as import_error:
    _sffuncspan = None
    _FUNCSPAN_OK = False
    if os.getenv("SF_DEBUG", "false").lower() == "true":
        import traceback

        print(
            f"[[DEBUG]] Failed to import _sffuncspan C extension: {import_error}",
            file=sys.stderr,
        )
        traceback.print_exc(file=sys.stderr)

_FUNCSPAN_READY = False  # one-time guard for native funcspan init
_FUNCSPAN_PROFILER = None  # global profiler instance

# GraphQL mutation string for prints — keep schema identical to server
_COLLECT_PRINT_MUTATION = (
    "mutation CollectPrintStatements("
    "$apiKey: String!,"
    "$serviceUuid: String!,"
    "$sessionId: String!,"
    "$contents: String!,"
    "$reentrancyGuardPreactive: Boolean!,"
    "$library: String!,"
    "$timestampMs: String!,"
    "$version: String!"
    "){collectPrintStatements("
    "apiKey:$apiKey,serviceUuid:$serviceUuid,sessionId:$sessionId,"
    "contents:$contents,reentrancyGuardPreactive:$reentrancyGuardPreactive,"
    "library:$library,timestampMs:$timestampMs,version:$version)}"
)

# GraphQL mutation string for function spans
_COLLECT_FUNCTION_SPAN_MUTATION = (
    "mutation CollectFunctionSpan("
    "$apiKey: String!,"
    "$serviceUuid: String!,"
    "$library: String!,"
    "$version: String!,"
    "$sessionId: String!,"
    "$spanId: String!,"
    "$parentSpanId: String,"
    "$filePath: String!,"
    "$lineNumber: Int!,"
    "$columnNumber: Int!,"
    "$functionName: String!,"
    "$arguments: String!,"
    "$returnValue: String,"
    "$startTimeNs: String!,"
    "$durationNs: String!,"
    "$timestampMs: String!"
    "){collectFunctionSpan("
    "apiKey:$apiKey,serviceUuid:$serviceUuid,library:$library,version:$version,"
    "sessionId:$sessionId,spanId:$spanId,parentSpanId:$parentSpanId,"
    "filePath:$filePath,lineNumber:$lineNumber,columnNumber:$columnNumber,"
    "functionName:$functionName,arguments:$arguments,returnValue:$returnValue,"
    "startTimeNs:$startTimeNs,durationNs:$durationNs,timestampMs:$timestampMs)}"
)

# GraphQL mutation string for service identification
_IDENTIFY_SERVICE_DETAILS_MUTATION = (
    "mutation IdentifyServiceDetails("
    "$apiKey: String!,"
    "$serviceUuid: String!,"
    "$library: String!,"
    "$version: String!,"
    "$serviceIdentifier: String!,"
    "$serviceVersion: String!,"
    "$serviceDisplayName: String,"
    "$serviceAdditionalMetadata: JSON,"
    "$gitSha: String!,"
    "$infrastructureType: String!,"
    "$infrastructureDetails: JSON,"
    "$setupInterceptorsFilePath: String!,"
    "$setupInterceptorsLineNumber: Int!,"
    "$timestampMs: String!"
    "){identifyServiceDetails("
    "apiKey:$apiKey,serviceUuid:$serviceUuid,library:$library,version:$version,"
    "serviceIdentifier:$serviceIdentifier,serviceVersion:$serviceVersion,"
    "serviceDisplayName:$serviceDisplayName,"
    "serviceAdditionalMetadata:$serviceAdditionalMetadata,gitSha:$gitSha,"
    "infrastructureType:$infrastructureType,infrastructureDetails:$infrastructureDetails,"
    "setupInterceptorsFilePath:$setupInterceptorsFilePath,"
    "setupInterceptorsLineNumber:$setupInterceptorsLineNumber,timestampMs:$timestampMs)}"
)

# GraphQL mutation string for update service details
_UPDATE_SERVICE_DETAILS_MUTATION = (
    "mutation UpdateServiceDetails("
    "$apiKey: String!,"
    "$serviceUuid: String!,"
    "$timestampMs: String!,"
    "$serviceIdentifier: String,"
    "$serviceVersion: String,"
    "$serviceAdditionalMetadata: JSON,"
    "$gitSha: String"
    "){updateServiceDetails("
    "apiKey:$apiKey,serviceUuid:$serviceUuid,timestampMs:$timestampMs,"
    "serviceIdentifier:$serviceIdentifier,serviceVersion:$serviceVersion,"
    "serviceAdditionalMetadata:$serviceAdditionalMetadata,gitSha:$gitSha)}"
)

# GraphQL mutation string for collect metadata
_COLLECT_METADATA_MUTATION = (
    "mutation CollectMetadata("
    "$apiKey: String!,"
    "$serviceUuid: String!,"
    "$library: String!,"
    "$version: String!,"
    "$sessionId: String!,"
    "$userId: String!,"
    "$traitsJson: String!,"
    "$excludedFields: [String!]!,"
    "$override: Boolean!,"
    "$timestampMs: String!"
    "){collectMetadata("
    "apiKey:$apiKey,serviceUuid:$serviceUuid,library:$library,version:$version,"
    "sessionId:$sessionId,userId:$userId,traitsJson:$traitsJson,"
    "excludedFields:$excludedFields,override:$override,timestampMs:$timestampMs)}"
)

# GraphQL mutation string for domains to not pass header to
_DOMAINS_TO_NOT_PASS_HEADER_TO_MUTATION = (
    "mutation DomainsToNotPassHeaderTo("
    "$apiKey: String!,"
    "$serviceUuid: String!,"
    "$library: String!,"
    "$version: String!,"
    "$domains: [String!]!,"
    "$timestampMs: String!"
    "){domainsToNotPassHeaderTo("
    "apiKey:$apiKey,serviceUuid:$serviceUuid,library:$library,version:$version,"
    "domains:$domains,timestampMs:$timestampMs)}"
)

STRINGS_NOT_FOUND_IN_CALLER_LOCATIONS = {
    "site-packages",
    "dist-packages",
    "venv",
    "/lib/python",
    "\\lib\\python",
    "sf-veritas",
}


def _ensure_fast_print_initialized() -> bool:
    """
    Lazily init the native print path; becomes a cheap bool check after first success.
    """
    global _FAST_PRINT_READY
    if not _FAST_OK or _FAST_PRINT_READY:
        return _FAST_PRINT_READY

    endpoint = getattr(app_config, "_sailfish_graphql_endpoint", None)
    api_key = getattr(app_config, "_sailfish_api_key", None)
    service_uuid = getattr(app_config, "_service_uuid", None)
    library = getattr(app_config, "library", "sailfish-python")
    version = getattr(app_config, "version", "0.0.0")
    http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0

    if not (endpoint and api_key and service_uuid):
        return False

    try:
        ok = _sffastlog.init_print(
            url=endpoint,
            query=_COLLECT_PRINT_MUTATION,
            api_key=str(api_key),
            service_uuid=str(service_uuid),
            library=str(library),
            version=str(version),
            http2=http2,
        )
        _FAST_PRINT_READY = bool(ok)
    except Exception:
        _FAST_PRINT_READY = False

    return _FAST_PRINT_READY


def _ensure_funcspan_initialized() -> bool:
    """
    Lazily init the native function span path; becomes a cheap bool check after first success.
    """
    global _FUNCSPAN_READY, _FUNCSPAN_PROFILER

    # PERFORMANCE: Skip function span profiler when testing network library only
    if os.getenv("TESTING_NETWORK_LIBRARY_ONLY", "0") == "1":
        if SF_DEBUG:
            print(
                "[[DEBUG]] Function span profiler: Disabled (TESTING_NETWORK_LIBRARY_ONLY=1)",
                log=False,
            )
        return False

    if not _FUNCSPAN_OK:
        if SF_DEBUG:
            print(
                "[[DEBUG]] Function span profiler: C extension not available (_FUNCSPAN_OK=False)",
                log=False,
            )
        return False

    if _FUNCSPAN_READY:
        return _FUNCSPAN_READY

    endpoint = getattr(app_config, "_sailfish_graphql_endpoint", None)
    api_key = getattr(app_config, "_sailfish_api_key", None)
    service_uuid = getattr(app_config, "_service_uuid", None)
    library = getattr(app_config, "library", "sailfish-python")
    version = getattr(app_config, "version", "0.0.0")
    http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0

    # Get function span config from env vars
    enable_profiler = os.getenv("SF_ENABLE_PROFILER", "false").lower() == "true"
    if SF_DEBUG:
        print(
            f"[[DEBUG]] Function span profiler: SF_ENABLE_PROFILER={os.getenv('SF_ENABLE_PROFILER')} -> enable_profiler={enable_profiler}",
            log=False,
        )

    if not enable_profiler:
        if SF_DEBUG:
            print(
                "[[DEBUG]] Function span profiler: Disabled (SF_ENABLE_PROFILER not 'true')",
                log=False,
            )
        return False

    if not (endpoint and api_key and service_uuid):
        if SF_DEBUG:
            print(
                f"[[DEBUG]] Function span profiler: Missing config (endpoint={bool(endpoint)}, api_key={bool(api_key)}, service_uuid={bool(service_uuid)})",
                log=False,
            )
        return False

    # Configuration options
    variable_capture_size_limit_mb = int(os.getenv("SF_FUNCSPAN_VAR_LIMIT_MB", "1"))
    capture_from_installed_libraries = (
        os.getenv("SF_FUNCSPAN_CAPTURE_LIBRARIES", "").split(",")
        if os.getenv("SF_FUNCSPAN_CAPTURE_LIBRARIES")
        else []
    )
    sample_rate = float(os.getenv("SF_FUNCSPAN_SAMPLE_RATE", "1.0"))
    enable_sampling = (
        os.getenv("SF_FUNCSPAN_ENABLE_SAMPLING", "false").lower() == "true"
    )
    include_django_view_functions = (
        os.getenv("SF_FUNCSPAN_INCLUDE_DJANGO_VIEW_FUNCTIONS", "false").lower()
        == "true"
    )

    try:
        _FUNCSPAN_PROFILER = init_function_span_profiler(
            url=endpoint,
            query=_COLLECT_FUNCTION_SPAN_MUTATION,
            api_key=str(api_key),
            service_uuid=str(service_uuid),
            library=str(library),
            version=str(version),
            http2=(http2 == 1),
            variable_capture_size_limit_mb=variable_capture_size_limit_mb,
            capture_from_installed_libraries=capture_from_installed_libraries,
            sample_rate=sample_rate,
            enable_sampling=enable_sampling,
            include_django_view_functions=include_django_view_functions,
            auto_start=True,
        )

        # Load .sailfish configuration files (directory/file/function-level configs)
        try:
            from .funcspan_config_loader import FunctionSpanConfigLoader

            # Get the directory where setup_interceptors() was called from
            setup_dir = getattr(app_config, "_setup_interceptors_call_filename", None)
            root_paths = []

            if setup_dir:
                # Use the directory containing the file that called setup_interceptors()
                root_paths.append(os.path.dirname(os.path.abspath(setup_dir)))

            # Also add current working directory
            root_paths.append(os.getcwd())

            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Loading .sailfish configs from: {root_paths}",
                    log=False,
                )

            config_loader = FunctionSpanConfigLoader(root_paths)
            config_loader.load_all_configs()

            if SF_DEBUG:
                print(
                    "[[DEBUG]] Function span config loader initialized successfully",
                    log=False,
                )
        except Exception as config_error:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Failed to load .sailfish configs (non-fatal): {config_error}",
                    log=False,
                )
            # Config loading is optional - don't fail if it doesn't work

        _FUNCSPAN_READY = True

        # Set master kill switch from SF_ENABLE_FUNCTION_SPANS (defaults to "true")
        enable_function_spans = (
            os.getenv("SF_ENABLE_FUNCTION_SPANS", "true").lower() == "true"
        )
        _sffuncspan.set_function_spans_enabled(enable_function_spans)

        if SF_DEBUG:
            print(
                f"[[DEBUG]] Function span capture: SF_ENABLE_FUNCTION_SPANS={os.getenv('SF_ENABLE_FUNCTION_SPANS', 'true')} -> enabled={enable_function_spans}",
                log=False,
            )

    except Exception as e:
        if SF_DEBUG:
            print(
                f"[[DEBUG]] Failed to initialize function span profiler: {e}", log=False
            )
        _FUNCSPAN_READY = False

    return _FUNCSPAN_READY


def _ensure_service_initialized() -> bool:
    """
    Lazily init the native service operations path (service_identifier, collect_metadata);
    becomes a cheap bool check after first success.
    """
    global _SFSERVICE_READY
    if not _SFSERVICE_OK or _SFSERVICE_READY:
        return _SFSERVICE_READY

    endpoint = getattr(app_config, "_sailfish_graphql_endpoint", None)
    api_key = getattr(app_config, "_sailfish_api_key", None)
    service_uuid = getattr(app_config, "_service_uuid", None)
    library = getattr(app_config, "library", "sailfish-python")
    version = getattr(app_config, "version", "0.0.0")
    http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0

    if not (endpoint and api_key and service_uuid):
        return False

    try:
        # Initialize the main service module (starts sender thread)
        ok = _sfservice.init(
            url=endpoint,
            query="",  # Not used for init, only for channel-specific inits
            api_key=str(api_key),
            service_uuid=str(service_uuid),
            library=str(library),
            version=str(version),
            http2=http2,
        )
        if not ok:
            _SFSERVICE_READY = False
            return False

        # Initialize service identifier channel
        ok = _sfservice.init_service_identifier(
            url=endpoint,
            query=_IDENTIFY_SERVICE_DETAILS_MUTATION,
            api_key=str(api_key),
            service_uuid=str(service_uuid),
            library=str(library),
            version=str(version),
            http2=http2,
        )
        if not ok:
            _SFSERVICE_READY = False
            return False

        # Initialize collect metadata channel
        ok = _sfservice.init_collect_metadata(
            url=endpoint,
            query=_COLLECT_METADATA_MUTATION,
            api_key=str(api_key),
            service_uuid=str(service_uuid),
            library=str(library),
            version=str(version),
            http2=http2,
        )
        if not ok:
            _SFSERVICE_READY = False
            return False

        # Initialize domains channel
        ok = _sfservice.init_domains(
            url=endpoint,
            query=_DOMAINS_TO_NOT_PASS_HEADER_TO_MUTATION,
            api_key=str(api_key),
            service_uuid=str(service_uuid),
            library=str(library),
            version=str(version),
            http2=http2,
        )
        if not ok:
            _SFSERVICE_READY = False
            return False

        # NOTE: update_service channel is NOT initialized here because the C implementation
        # is currently incompatible with the GraphQL schema. It will use Python fallback.
        # The C extension has py_update_service() which takes domains[], but the actual
        # GraphQL mutation expects service_identifier, service_version, etc.
        # TODO: Reimplement build_body_update_service() in C to match the schema.

        _SFSERVICE_READY = True
    except Exception as e:
        if SF_DEBUG:
            print(f"[[DEBUG]] Failed to initialize _sfservice: {e}", log=False)
        _SFSERVICE_READY = False

    return _SFSERVICE_READY


def _shutdown_all_c_extensions():
    """
    Shutdown all C extensions in the correct order.
    This function is called on application exit to ensure clean shutdown
    of background threads and prevent exit code 137 (SIGKILL).

    Order matters: shutdown dependencies first, then core extensions.
    """
    # Use sys.stderr.write() for debugging because print() might not work during shutdown
    import sys

    # Check if shutdown was already called (by signal handler)
    global _shutdown_handler_called
    if _shutdown_handler_called:
        return

    _shutdown_handler_called = True

    # First, set the global shutdown flag (for any Python code that checks it)
    set_shutdown_flag()

    # Shutdown function span profiler first (depends on funcspan C extension)
    global _FUNCSPAN_PROFILER
    if _FUNCSPAN_PROFILER is not None:
        try:
            _FUNCSPAN_PROFILER.stop()
            _FUNCSPAN_PROFILER = None
        except Exception as e:
            pass

    # Shutdown function span config C extension
    try:
        from . import _sffuncspan_config

        _sffuncspan_config.shutdown()
    except Exception as e:
        if SF_DEBUG:
            sys.stderr.write(f"[SHUTDOWN] _sffuncspan_config.shutdown() failed: {e}\n")
            sys.stderr.flush()

    # Shutdown function span C extension
    try:
        if _FUNCSPAN_OK and _sffuncspan:
            _sffuncspan.shutdown()
    except Exception as e:
        if SF_DEBUG:
            sys.stderr.write(f"[SHUTDOWN] _sffuncspan.shutdown() failed: {e}\n")
            sys.stderr.flush()

    # Shutdown network hop C extension
    try:
        from . import fast_network_hop

        if fast_network_hop._NETWORKHOP_FAST_OK and fast_network_hop._sfnetworkhop:
            fast_network_hop._sfnetworkhop.shutdown()
    except Exception as e:
        if SF_DEBUG:
            sys.stderr.write(f"[SHUTDOWN] _sfnetworkhop.shutdown() failed: {e}\n")
            sys.stderr.flush()

    # Shutdown network request C extension
    try:
        from .patches.network_libraries import utils as net_utils

        if net_utils._FAST_NETWORKREQUEST_AVAILABLE and net_utils._sffastnetworkrequest:
            net_utils._sffastnetworkrequest.shutdown()
    except Exception as e:
        if SF_DEBUG:
            sys.stderr.write(
                f"[SHUTDOWN] _sffastnetworkrequest.shutdown() failed: {e}\n"
            )
            sys.stderr.flush()

    # Shutdown service operations C extension
    try:
        if _SFSERVICE_OK and _sfservice:
            _sfservice.shutdown()
    except Exception as e:
        if SF_DEBUG:
            sys.stderr.write(f"[SHUTDOWN] _sfservice.shutdown() failed: {e}\n")
            sys.stderr.flush()

    # Shutdown fast log C extension (core - shutdown last)
    try:
        if _FAST_OK and _sffastlog:
            _sffastlog.shutdown()
    except Exception as e:
        if SF_DEBUG:
            sys.stderr.write(f"[SHUTDOWN] _sffastlog.shutdown() failed: {e}\n")
            sys.stderr.flush()

    if SF_DEBUG:
        sys.stderr.write(
            f"[SHUTDOWN] _shutdown_all_c_extensions() completed in PID {os.getpid()}\n"
        )
    sys.stderr.flush()


# Global flag to prevent calling shutdown handler multiple times
_shutdown_handler_called = False

# Store the original signal.signal function for monkey-patching
_original_signal_signal = None

# Track handlers that have already been wrapped to avoid double-wrapping
_wrapped_handlers = {}  # {signum: wrapped_handler}

# Track if we've already run shutdown for this signal
_shutdown_by_signal = {}  # {signum: bool}


def _patched_signal_signal(signum, handler):
    """
    Monkey-patched version of signal.signal() that intercepts SIGTERM/SIGINT
    registrations and chains our C extension cleanup before the application's handler.

    This ensures our cleanup runs first, regardless of when frameworks
    (Django, Celery, Uvicorn, etc.) install their signal handlers.
    """
    global _wrapped_handlers, _shutdown_by_signal

    # Only intercept SIGTERM and SIGINT
    if signum not in (signal.SIGTERM, signal.SIGINT):
        return _original_signal_signal(signum, handler)

    # ALWAYS log interception (not just SF_DEBUG) for debugging 137 issues
    sys.stderr.write(
        f"[SIGNAL_PATCH] Intercepted signal.signal({signum}, {handler}) in PID {os.getpid()}\n"
    )
    sys.stderr.flush()

    # Check if this handler is already one we wrapped (avoid double-wrapping)
    if handler in _wrapped_handlers.values():
        if SF_DEBUG:
            sys.stderr.write(
                f"[SIGNAL_PATCH] Handler already wrapped, passing through\n"
            )
            sys.stderr.flush()
        return _original_signal_signal(signum, handler)

    # Handle special cases
    if handler == signal.SIG_IGN:
        # They want to ignore the signal - respect that but still cleanup
        def wrapped_ignore(sig, frame):
            if not _shutdown_by_signal.get(sig, False):
                _shutdown_by_signal[sig] = True
                sys.stderr.write(
                    f"[SIGNAL] Received signal {sig} (SIG_IGN), running cleanup\n"
                )
                sys.stderr.flush()
                _shutdown_all_c_extensions()

        wrapped_handler = wrapped_ignore

    elif handler == signal.SIG_DFL:
        # They want default behavior - cleanup then re-raise
        def wrapped_default(sig, frame):
            if not _shutdown_by_signal.get(sig, False):
                _shutdown_by_signal[sig] = True
                sys.stderr.write(
                    f"[SIGNAL] Received signal {sig} (SIG_DFL), running cleanup\n"
                )
                sys.stderr.flush()
                _shutdown_all_c_extensions()
            # Restore default and re-raise
            _original_signal_signal(sig, signal.SIG_DFL)
            os.kill(os.getpid(), sig)

        wrapped_handler = wrapped_default

    elif callable(handler):
        # They provided a custom handler - chain ours before theirs
        def wrapped_custom(sig, frame):
            if not _shutdown_by_signal.get(sig, False):
                _shutdown_by_signal[sig] = True
                sys.stderr.write(
                    f"[SIGNAL] Received signal {sig} in PID {os.getpid()}\n"
                )
                sys.stderr.flush()
                _shutdown_all_c_extensions()

                # Print all remaining threads for debugging
                import threading

                sys.stderr.write(
                    f"[SIGNAL] Active threads after shutdown: {threading.active_count()}\n"
                )
                for thread in threading.enumerate():
                    sys.stderr.write(
                        f"[SIGNAL]   - {thread.name} (daemon={thread.daemon}, alive={thread.is_alive()})\n"
                    )
                sys.stderr.flush()

            sys.stderr.write(f"[SIGNAL] Calling application handler: {handler}\n")
            sys.stderr.flush()
            handler(sig, frame)

        wrapped_handler = wrapped_custom
    else:
        # Unknown handler type - pass through
        if SF_DEBUG:
            sys.stderr.write(f"[SIGNAL_PATCH] Unknown handler type, passing through\n")
            sys.stderr.flush()
        return _original_signal_signal(signum, handler)

    # Track this wrapped handler
    _wrapped_handlers[signum] = wrapped_handler

    # Install the wrapped handler
    if SF_DEBUG:
        sys.stderr.write(
            f"[SIGNAL_PATCH] Installing wrapped handler for signal {signum}\n"
        )
        sys.stderr.flush()

    return _original_signal_signal(signum, wrapped_handler)


def _monitor_parent_process():
    """
    Background daemon thread that monitors parent process for death.

    This is a cross-platform solution that works on Linux, macOS, and Windows.
    It detects when the parent process dies by checking if we've been reparented
    (parent PID changes, typically to init/PID 1).

    How it works:
    - Records the initial parent PID at startup
    - Periodically checks if current parent PID != initial parent PID
    - When parent dies, we get reparented (usually to PID 1)
    - Triggers clean shutdown of C extensions immediately

    This handles all cases where parent dies without forwarding signals:
    - Shell wrappers (sh -c) that don't forward SIGTERM
    - Process supervisors that exit unexpectedly
    - Container runtimes that kill parent process

    Check interval configured via: SF_PARENT_MONITOR_INTERVAL_MS (default: 100ms)
    Set to 0 to disable monitoring.
    """
    import time

    # Record initial parent PID
    initial_parent_pid = os.getppid()

    sys.stderr.write(
        f"[SAILFISH_INIT] Parent monitor thread started (parent PID: {initial_parent_pid}, check interval: {SF_PARENT_MONITOR_INTERVAL_MS}ms)\n"
    )
    sys.stderr.flush()

    # Convert milliseconds to seconds for time.sleep()
    check_interval_seconds = SF_PARENT_MONITOR_INTERVAL_MS / 1000.0

    try:
        while True:
            time.sleep(check_interval_seconds)

            current_parent_pid = os.getppid()

            # Check if parent has changed (we've been reparented)
            if current_parent_pid != initial_parent_pid:
                sys.stderr.write(
                    f"[PARENT_MONITOR] Parent process died! Initial parent PID: {initial_parent_pid}, current parent PID: {current_parent_pid}\n"
                )
                sys.stderr.write(
                    f"[PARENT_MONITOR] Triggering clean shutdown of C extensions...\n"
                )
                sys.stderr.flush()

                # Trigger shutdown
                _shutdown_all_c_extensions()

                sys.stderr.write(
                    f"[PARENT_MONITOR] Clean shutdown complete, exiting with code 0\n"
                )
                sys.stderr.flush()

                # Exit cleanly
                os._exit(0)

    except Exception as e:
        # If monitoring fails, log but don't crash the application
        if SF_DEBUG:
            sys.stderr.write(
                f"[PARENT_MONITOR] Monitoring thread error (non-fatal): {e}\n"
            )
            sys.stderr.flush()


def _setup_parent_death_signal():
    """
    On Linux, register to receive SIGTERM when parent process dies.
    This handles cases where shell wrappers (sh -c) or process supervisors
    don't forward signals properly in Docker/Kubernetes environments.

    This is a best-effort enhancement that works transparently without
    requiring customers to modify Dockerfiles, entrypoints, or K8s configs.

    How it works:
    - Uses Linux prctl(PR_SET_PDEATHSIG, SIGTERM)
    - When parent process dies, kernel sends SIGTERM to this process
    - Our monkey-patched signal handlers run
    - C extensions shut down cleanly

    Platform support:
    - Linux: Uses prctl(PR_SET_PDEATHSIG)
    - macOS: Skipped (no prctl)
    - Windows: Skipped (no prctl)

    Can be disabled via: SF_DISABLE_PARENT_DEATH_SIGNAL=true
    """
    # Check if disabled via environment variable
    if SF_DISABLE_PARENT_DEATH_SIGNAL:
        if SF_DEBUG:
            sys.stderr.write(
                "[SAILFISH_INIT] Parent death signal disabled via SF_DISABLE_PARENT_DEATH_SIGNAL\n"
            )
            sys.stderr.flush()
        return

    # Only supported on Linux
    if sys.platform != "linux":
        if SF_DEBUG:
            sys.stderr.write(
                f"[SAILFISH_INIT] Parent death signal not supported on {sys.platform}, skipping\n"
            )
            sys.stderr.flush()
        return

    try:
        import ctypes

        # Load libc
        try:
            libc = ctypes.CDLL("libc.so.6")
        except OSError:
            # Try alternative libc names
            try:
                libc = ctypes.CDLL("libc.so")
            except OSError:
                if SF_DEBUG:
                    sys.stderr.write(
                        "[SAILFISH_INIT] Could not load libc, parent death signal unavailable\n"
                    )
                    sys.stderr.flush()
                return

        # prctl constants
        PR_SET_PDEATHSIG = 1  # Set parent death signal

        # Register to receive SIGTERM when parent dies
        result = libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM)

        if result == 0:
            sys.stderr.write(
                "[SAILFISH_INIT] Registered parent death signal (SIGTERM on parent exit)\n"
            )
            sys.stderr.flush()
        else:
            if SF_DEBUG:
                sys.stderr.write(
                    f"[SAILFISH_INIT] prctl returned {result}, parent death signal may not be active\n"
                )
                sys.stderr.flush()

    except AttributeError:
        # prctl function not available in libc
        if SF_DEBUG:
            sys.stderr.write(
                "[SAILFISH_INIT] prctl not available in libc, parent death signal unavailable\n"
            )
            sys.stderr.flush()
    except Exception as e:
        # Any other error - log but don't crash
        if SF_DEBUG:
            sys.stderr.write(
                f"[SAILFISH_INIT] Unexpected error setting up parent death signal: {e}\n"
            )
            sys.stderr.flush()


class UnifiedInterceptor:
    """
    Replaces sys.stdout and builtins.print with ultra-thin shims:
      - direct write to real stdout (no recursion, no lock, no regex)
      - native fast path to _sffastlog.print_() when available
      - fallback to PrintInterceptor otherwise
    """

    __slots__ = (
        "print_interceptor",
        "_original_stdout",
        "_original_stderr",
    )

    def __init__(self):
        # Note: CustomLogHandler is created in setup_interceptors() and added to loggers there
        # We don't need a separate instance here
        self.print_interceptor = PrintInterceptor()
        # Use sys.__stdout__ and sys.__stderr__ to get the ORIGINAL streams
        # before any monkey-patching. This prevents recursion issues when
        # log=False tries to bypass interceptors.
        self._original_stdout = sys.__stdout__
        self._original_stderr = sys.__stderr__

    # -------- sys.stdout replacement --------
    def write(self, message):
        """
        Ultra-thin write path: write to real stdout, then ship via C fast path or fallback.
        """
        # Debug logging for Django output capture
        if SF_DEBUG and message and message.strip():
            sys.__stderr__.write(
                f"[DEBUG UnifiedInterceptor.write] {repr(message[:80])}\n"
            )
            sys.__stderr__.flush()

        # Respect guards
        if get_reentrancy_guard_sys_stdout_active() or getattr(
            _thread_locals, "reentrancy_guard_logging_active", False
        ):
            self._original_stdout.write(message)
            return

        # Always write to the real stdout first; no unconditional flush.
        self._original_stdout.write(message)

        # Skip empty / newline-only
        if not message or message == "\n":
            if SF_DEBUG:
                sys.__stderr__.write(f"[DEBUG] Skipping empty/newline message\n")
                sys.__stderr__.flush()
            return

        # Build/send once
        _, trace_id = get_or_set_sf_trace_id()

        # Native fast path (ring + libcurl sender)
        fast_ok = _ensure_fast_print_initialized()
        if SF_DEBUG:
            sys.__stderr__.write(f"[DEBUG] Fast print initialized: {fast_ok}\n")
            sys.__stderr__.flush()

        if fast_ok:
            try:
                if SF_DEBUG:
                    sys.__stderr__.write(
                        f"[DEBUG] Calling _sffastlog.print_() with message: {repr(message[:50])}\n"
                    )
                    sys.__stderr__.flush()
                _sffastlog.print_(
                    contents=message, session_id=str(trace_id), preactive=0
                )
                if SF_DEBUG:
                    sys.__stderr__.write(f"[DEBUG] _sffastlog.print_() succeeded\n")
                    sys.__stderr__.flush()
                return
            except Exception as e:
                if SF_DEBUG:
                    sys.__stderr__.write(f"[DEBUG] _sffastlog.print_() failed: {e}\n")
                    sys.__stderr__.flush()
                pass  # fall back below

        # Fallback to Python interceptor path
        if SF_DEBUG:
            sys.__stderr__.write(f"[DEBUG] Using fallback Python interceptor\n")
            sys.__stderr__.flush()
        self.print_interceptor.do_send((message, trace_id), trace_id)

    def flush(self):
        self._original_stdout.flush()

    # -------- print() override --------
    def create_custom_print(self):
        """
        Provide a print function compatible with the builtins.print signature,
        but as lean as possible.
        """
        _orig = self._original_stdout
        _pi = self.print_interceptor

        def custom_print(*args, sep=" ", end="\n", file=None, flush=False, log=True):
            # Perform the minimal formatting work once.
            out = sep.join(map(str, args)) + end

            # Always write to real stdout.
            # (Ignore 'file' param to avoid recursion into our own wrappers.)
            _orig.write(out)
            if flush:
                _orig.flush()

            if not log:
                return
            msg = out
            if not msg.strip():
                return

            # Trace id once
            _, trace_id = get_or_set_sf_trace_id()

            # Native fast path
            fast_init = _ensure_fast_print_initialized()
            if SF_DEBUG:
                _orig.write(f"[[DEBUG custom_print]] fast_init={fast_init}, msg={msg[:50]!r}\n")
                _orig.flush()

            if fast_init:
                try:
                    _sffastlog.print_(
                        contents=msg, session_id=str(trace_id), preactive=0
                    )
                    if SF_DEBUG:
                        _orig.write(f"[[DEBUG custom_print]] C fast path succeeded\n")
                        _orig.flush()
                    return
                except Exception as e:
                    if SF_DEBUG:
                        _orig.write(f"[[DEBUG custom_print]] C fast path failed: {e}\n")
                        _orig.flush()
                    pass

            # Fallback
            if SF_DEBUG:
                _orig.write(f"[[DEBUG custom_print]] Using Python fallback, _pi={_pi}\n")
                _orig.flush()
            try:
                _pi.do_send((msg, trace_id), trace_id)
                if SF_DEBUG:
                    _orig.write(f"[[DEBUG custom_print]] Python fallback succeeded\n")
                    _orig.flush()
            except Exception as e:
                if SF_DEBUG:
                    _orig.write(f"[[DEBUG custom_print]] Python fallback failed: {e}\n")
                    _orig.flush()

        return custom_print

    def __getattr__(self, attr):
        """
        Delegate attribute access to original stdout or stderr when needed.
        """
        if hasattr(self._original_stdout, attr):
            return getattr(self._original_stdout, attr)
        # TODO: If you later intercept stderr, mirror the same behavior
        # elif hasattr(self._original_stderr, attr):
        #     return getattr(self._original_stderr, attr)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )

    def intercept_stdout(self):
        """
        Replace sys.stdout and builtins.print to intercept all output.
        """
        if PRINT_CONFIGURATION_STATUSES:
            self._original_stdout.write("Intercepting stdout and print...\n")
            self._original_stdout.flush()

        # Replace stdout
        sys.stdout = self
        # NOTE: stderr interception left as-is; uncomment if you want parity:
        # sys.stderr = self

        # Save original print if not already saved
        if not hasattr(builtins, "_original_print"):
            builtins._original_print = builtins.print

        # Override builtins.print with our ultra-thin implementation
        custom_print_function = self.create_custom_print()
        builtins.print = functools.partial(custom_print_function)

        # Update __builtins__ reference if needed
        if isinstance(__builtins__, dict):
            __builtins__["print"] = custom_print_function
        elif isinstance(__builtins__, ModuleType):
            setattr(__builtins__, "print", custom_print_function)

        # Also ensure __main__.print and builtins module reference are updated
        if "__main__" in sys.modules:
            sys.modules["__main__"].__dict__["print"] = custom_print_function
        sys.modules["builtins"].print = custom_print_function

        if PRINT_CONFIGURATION_STATUSES:
            self._original_stdout.write("Intercepting stdout and print...DONE\n")
            self._original_stdout.flush()

    # -------- exceptions --------
    def intercept_exceptions(self):
        start_profiling()
        if PRINT_CONFIGURATION_STATUSES:
            self._original_stdout.write("Intercepting uncaught exceptions...\n")
            self._original_stdout.flush()

        sys.excepthook = custom_excepthook
        if hasattr(threading, "excepthook"):
            threading.excepthook = custom_thread_excepthook

        if PRINT_CONFIGURATION_STATUSES:
            self._original_stdout.write("Intercepting uncaught exceptions...DONE\n")
            self._original_stdout.flush()

    # TODO - Figure out how to make this work universally
    def patch_exception_class(self):
        import builtins as _b

        if hasattr(_b.Exception, "transmit_to_sailfish"):
            return
        try:
            if PRINT_CONFIGURATION_STATUSES:
                self._original_stdout.write("Monkey-patching Exceptions class...\n")
                self._original_stdout.flush()
            _ = _b.Exception
            _b.Exception = PatchedException
            if PRINT_CONFIGURATION_STATUSES:
                self._original_stdout.write("Monkey-patching Exceptions class...DONE\n")
                self._original_stdout.flush()
        except Exception as e:
            print(f"[Warning] Failed to patch `builtins.Exception`: {e}")


# ----------------- setup entrypoint -----------------


@validate_call
def setup_interceptors(
    api_key: str,
    graphql_endpoint: str = None,
    service_identifier: Optional[str] = None,
    service_version: Optional[str] = None,
    service_display_name: Optional[str] = None,
    git_sha: Optional[str] = None,
    service_additional_metadata: Optional[
        Dict[str, Union[str, int, float, None]]
    ] = None,
    profiling_mode_enabled: bool = False,
    profiling_max_depth: int = 5,
    domains_to_not_propagate_headers_to: Optional[List[str]] = None,
    routes_to_skip_network_hops: Optional[List[str]] = None,
    site_and_dist_packages_to_collect_local_variables_on: Optional[List[str]] = None,
    setup_global_time_at_app_spinup: bool = True,
):
    if service_identifier is None:
        service_identifier = os.getenv("SERVICE_VERSION", os.getenv("GIT_SHA"))
    if git_sha is None:
        git_sha = os.getenv("GIT_SHA")
    app_config._service_identifier = service_identifier
    app_config._service_version = service_version
    app_config._service_display_name = service_display_name
    app_config._git_sha = git_sha
    app_config._service_additional_metadata = service_additional_metadata
    app_config._profiling_mode_enabled = profiling_mode_enabled
    app_config._profiling_max_depth = profiling_max_depth
    app_config._set_site_and_dist_packages_to_collect_local_variables_on = (
        site_and_dist_packages_to_collect_local_variables_on
    )

    # Use parameter if provided, otherwise fall back to environment variable
    if routes_to_skip_network_hops is not None:
        app_config._routes_to_skip_network_hops = routes_to_skip_network_hops
    else:
        # Parse env var as comma-separated list
        if SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES:
            app_config._routes_to_skip_network_hops = [
                p.strip()
                for p in SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES.split(",")
                if p.strip()
            ]
        else:
            app_config._routes_to_skip_network_hops = []

    # Capture caller file/line (avoid site-packages etc)
    for frame in inspect.stack():
        if any(s in frame.filename for s in STRINGS_NOT_FOUND_IN_CALLER_LOCATIONS):
            continue
        app_config._setup_interceptors_call_filename = frame.filename
        app_config._setup_interceptors_call_lineno = frame.lineno
        break

    # Configure core endpoints/keys
    app_config._sailfish_api_key = api_key
    app_config._sailfish_graphql_endpoint = (
        graphql_endpoint or app_config._sailfish_graphql_endpoint
    )

    # Idempotent setup
    if app_config._interceptors_initialized:
        if SF_DEBUG:
            print("[[DEBUG]] Interceptors already set up. Skipping setup.")
        return

    if not app_config._sailfish_api_key:
        raise RuntimeError(
            "The 'api_key' parameter is missing. Please provide a valid value."
        )

    if PRINT_CONFIGURATION_STATUSES:
        print("Setting up interceptors")

    # Register shutdown handlers to cleanly stop C extensions and prevent exit code 137
    # atexit: handles normal Python exit (sys.exit(), end of script, etc.)
    atexit.register(_shutdown_all_c_extensions)

    # Monkey-patch signal.signal() to intercept ALL signal handler registrations
    # This ensures our C extension cleanup runs first, regardless of when
    # frameworks (Django, Celery, Uvicorn, etc.) install their handlers
    global _original_signal_signal
    if _original_signal_signal is None:  # Only patch once
        _original_signal_signal = signal.signal
        signal.signal = _patched_signal_signal

        # ALWAYS log this (not just SF_DEBUG) so we can debug 137 issues
        sys.stderr.write(
            f"[SAILFISH_INIT] Monkey-patched signal.signal() in PID {os.getpid()}\n"
        )
        sys.stderr.flush()

    # Check if handlers are already registered and wrap them
    for sig in (signal.SIGTERM, signal.SIGINT):
        current_handler = signal.getsignal(sig)
        if current_handler not in (signal.SIG_DFL, signal.SIG_IGN, None):
            # A handler is already registered - wrap it
            sys.stderr.write(
                f"[SAILFISH_INIT] Found existing {sig} handler: {current_handler}, wrapping it\n"
            )
            sys.stderr.flush()

            # Use our patched signal.signal to wrap it
            signal.signal(sig, current_handler)
        else:
            sys.stderr.write(
                f"[SAILFISH_INIT] No existing handler for signal {sig} (current: {current_handler})\n"
            )
            sys.stderr.flush()

    # Setup parent death signal (Linux only, best-effort)
    # This ensures Python receives SIGTERM even when shell wrappers don't forward signals
    # Critical for Docker/Kubernetes environments where customers can't modify infrastructure
    _setup_parent_death_signal()

    # Start parent process monitor thread (cross-platform)
    # This actively detects when parent process dies by checking for reparenting
    # More reliable than signals, works on all platforms
    if SF_PARENT_MONITOR_INTERVAL_MS > 0:
        parent_monitor_thread = threading.Thread(
            target=_monitor_parent_process,
            name="sailfish-parent-monitor",
            daemon=True,  # Daemon thread won't prevent process exit
        )
        parent_monitor_thread.start()
    else:
        if SF_DEBUG:
            sys.stderr.write(
                "[SAILFISH_INIT] Parent monitoring disabled (SF_PARENT_MONITOR_INTERVAL_MS=0)\n"
            )
            sys.stderr.flush()

    # Global time sync
    if setup_global_time_at_app_spinup:
        TimeSync.get_instance()

    # Local env detect
    set_sf_is_local_flag()

    # Install hooks
    unified_interceptor = UnifiedInterceptor()
    unified_interceptor.intercept_exceptions()

    # Configure logging to capture ALL logs (including those with propagate=False like Uvicorn)
    logging.basicConfig(level=LOG_LEVEL)
    custom_handler = CustomLogHandler()

    # Add to root logger (captures all logs with propagate=True)
    root_logger = logging.getLogger()
    root_logger.addHandler(custom_handler)

    # OPTIMIZATION: Cache loggers we've already processed to avoid repeated checks
    # Use dict instead of set for faster lookups (dicts have slightly better cache locality)
    # This cache tracks which loggers we've seen and don't need to check again
    _processed_loggers = {}

    # Store reference to check if handler is already added
    # OPTIMIZATION: Cache the CustomLogHandler class to avoid repeated lookups
    _handler_class = CustomLogHandler

    def _needs_handler(logger_instance):
        """Check if logger needs our handler added.

        OPTIMIZED: Use direct iteration instead of generator expression to avoid overhead.
        """
        # Fast path: If no handlers, definitely needs one
        if not logger_instance.handlers:
            return True

        # Check if our handler is already present (avoid generator overhead)
        for h in logger_instance.handlers:
            if isinstance(h, _handler_class):
                return False
        return True

    # Monkey-patch logging.Logger.__setattr__ to detect when propagate is set to False
    # This catches cases where logger is created before our patch, but propagate set later
    _original_Logger_setattr = logging.Logger.__setattr__

    def _patched_Logger_setattr(self, name, value):
        _original_Logger_setattr(self, name, value)
        # If propagate was just set to False, add our handler
        if name == "propagate" and value is False and self.name:
            if _needs_handler(self):
                self.addHandler(custom_handler)
                _processed_loggers[self.name] = (
                    self  # Mark as processed (cache logger instance)
                )
                if SF_DEBUG:
                    print(
                        f"[[DEBUG]] Auto-added handler to {self.name} (propagate set to False)",
                    )

    logging.Logger.__setattr__ = _patched_Logger_setattr

    # Monkey-patch logging.getLogger() to auto-add handler to propagate=False loggers
    # This catches loggers retrieved/accessed after setup
    _original_getLogger = logging.getLogger

    def _patched_getLogger(name=None):
        # ULTRA-FAST PATH: Early exit for root logger (most common case)
        # Check BEFORE calling original getLogger to save a function call
        if name is None or name == "root":
            return _original_getLogger(name)

        # ULTRA-FAST PATH: Check cache BEFORE calling original getLogger
        # Dict lookup is ~50ns, saves us from redundant processing
        # OPTIMIZATION: Use get() with sentinel for faster cache hits (avoids exception overhead)
        cached = _processed_loggers.get(name, None)
        if cached is not None:
            return cached

        # Get logger (only called on first access for this logger name)
        logger = _original_getLogger(name)

        # OPTIMIZATION: Mark as processed IMMEDIATELY by caching the logger instance
        # This avoids set operations and gives us O(1) lookup next time
        _processed_loggers[name] = logger

        # FAST PATH: Only check propagate if it's actually False
        # Most loggers have propagate=True, so this avoids _needs_handler call
        # REMOVED: isinstance check - getLogger() always returns a Logger
        if not logger.propagate:
            # OPTIMIZATION: Inline _needs_handler check for hot path performance
            # Fast path: no handlers means we definitely need to add one
            needs_handler = not logger.handlers
            if not needs_handler:
                # Check if our handler is already present (manual loop for early exit)
                needs_handler = True
                for h in logger.handlers:
                    if isinstance(h, _handler_class):
                        needs_handler = False
                        break

            if needs_handler:
                logger.addHandler(custom_handler)
                if SF_DEBUG:
                    print(
                        f"[[DEBUG]] Auto-added handler to {name} (has propagate=False)",
                        log=False,
                    )

        return logger

    logging.getLogger = _patched_getLogger

    # Also handle any existing loggers with propagate=False
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        logger = _original_getLogger(logger_name)
        if isinstance(logger, logging.Logger) and not logger.propagate:
            if _needs_handler(logger):
                logger.addHandler(custom_handler)
                if SF_DEBUG:
                    print(
                        f"[[DEBUG]] Added handler to existing logger {logger_name} (has propagate=False)",
                    )
        # Mark all existing loggers as processed to avoid checking them again
        _processed_loggers[logger_name] = logger

    if SF_DEBUG:
        print(
            f"[[DEBUG]] Configured logging: root handler + auto-patching getLogger() and Logger.__setattr__",
        )

    # stdout + print override (this is the hot path)
    unified_interceptor.intercept_stdout()

    # Framework wrappers / network patches
    if SF_DEBUG:
        print(
            f"[[DEBUG]] Before patch_web_frameworks, sys.getprofile() = {sys.getprofile()}",
            log=False,
        )
    # Initialize service operations C extension FIRST (before patching)
    # This ensures the C extension is ready when DomainsToNotPassHeaderToTransmitter
    # is called during patch_all_http_clients()
    if _ensure_service_initialized():
        try:
            import json

            # Prepare parameters for service_identifier()
            service_identifier_val = app_config._service_identifier or ""
            service_version_val = app_config._service_version or ""
            service_display_name_val = app_config._service_display_name or ""
            git_sha_val = app_config._git_sha or ""

            # Serialize additional metadata dict to JSON string
            service_additional_metadata_json = ""
            if app_config._service_additional_metadata:
                try:
                    service_additional_metadata_json = json.dumps(
                        app_config._service_additional_metadata
                    )
                except Exception as e:
                    if SF_DEBUG:
                        print(
                            f"[[DEBUG]] Failed to serialize service_additional_metadata: {e}",
                            log=False,
                        )

            # Get infrastructure details
            infrastructure_type_val = ""
            infrastructure_details_json = ""
            try:
                infrastructure_type_val = app_config._infra_details.system.value
                infrastructure_details_json = json.dumps(
                    app_config._infra_details.details
                )
            except Exception as e:
                if SF_DEBUG:
                    print(
                        f"[[DEBUG]] Failed to get infrastructure details: {e}",
                        log=False,
                    )

            # Get setup_interceptors call location
            setup_file_path = app_config._setup_interceptors_call_filename or ""
            setup_line_number = app_config._setup_interceptors_call_lineno or 0

            # Call the C extension to send service identification
            _sfservice.service_identifier(
                service_identifier=service_identifier_val,
                service_version=service_version_val,
                service_display_name=service_display_name_val,
                service_additional_metadata=service_additional_metadata_json,
                git_sha=git_sha_val,
                infrastructure_type=infrastructure_type_val,
                infrastructure_details=infrastructure_details_json,
                setup_interceptors_file_path=setup_file_path,
                setup_interceptors_line_number=setup_line_number,
            )

            if SF_DEBUG:
                print(
                    "[[DEBUG]] Service identification sent via _sfservice C extension",
                    log=False,
                )
        except Exception as e:
            if SF_DEBUG:
                print(
                    f"[[DEBUG]] Failed to send service identification: {e}", log=False
                )

    # Now that C extension is initialized, apply framework/network patches
    # The DomainsToNotPassHeaderToTransmitter will use the C extension now
    patch_web_frameworks(routes_to_skip_network_hops)
    if SF_DEBUG:
        print(
            f"[[DEBUG]] After patch_web_frameworks, sys.getprofile() = {sys.getprofile()}",
            log=False,
        )
    patch_all_http_clients(domains_to_not_propagate_headers_to)

    # Patch ThreadPoolExecutor to copy ContextVars (eliminates lock contention!)
    patch_threading()
    if SF_DEBUG:
        print(
            f"[[DEBUG]] After patch_threading, ThreadPoolExecutor will copy ContextVars",
            log=False,
        )

    # Initialize function span profiler if enabled
    if _ensure_funcspan_initialized():
        if PRINT_CONFIGURATION_STATUSES:
            print("Function span profiler initialized and started.", log=False)
        if SF_DEBUG:
            print(
                f"[[DEBUG]] After funcspan init, sys.getprofile() = {sys.getprofile()}",
                log=False,
            )

    app_config._interceptors_initialized = True

    # CRITICAL: Mark interceptors as ready - this enables profiling
    # The profiler skips all events until interceptors are fully initialized to prevent
    # crashes from profiling code in an inconsistent state during initialization.
    if _FUNCSPAN_OK and _sffuncspan:
        _sffuncspan.set_interceptors_ready()
        if SF_DEBUG:
            print("[[DEBUG]] Profiling enabled (interceptors ready)", log=False)

    if PRINT_CONFIGURATION_STATUSES:
        print("Interceptors setup completed.", log=False)


def reinitialize_after_fork():
    """
    Reinitialize only the C extensions after a fork (for multiprocessing frameworks like Robyn).
    Does NOT re-apply patches - those are inherited from the parent process.
    Only resets initialization flags and reinitializes C extension background threads/libcurl.
    """
    global _FAST_PRINT_READY, _FUNCSPAN_READY, _FUNCSPAN_PROFILER

    if SF_DEBUG:
        print(
            f"[[DEBUG]] reinitialize_after_fork() called in PID {os.getpid()}",
            log=False,
        )

    # Shutdown C extensions first (resets g_running flag and cleans up state)
    # Note: We don't call _shutdown_all_c_extensions() here because we're reinitializing,
    # not shutting down permanently, so we don't want to set the shutdown flag.

    # Shutdown function span config C extension
    try:
        from . import _sffuncspan_config

        if SF_DEBUG:
            print("[[DEBUG]] Shutting down _sffuncspan_config before reinit", log=False)
        _sffuncspan_config.shutdown()
    except Exception as e:
        if SF_DEBUG:
            print(
                f"[[DEBUG]] _sffuncspan_config.shutdown() failed (non-fatal): {e}",
                log=False,
            )

    # Shutdown function span C extension
    try:
        if _FUNCSPAN_OK and _sffuncspan:
            if SF_DEBUG:
                print("[[DEBUG]] Shutting down _sffuncspan before reinit", log=False)
            _sffuncspan.shutdown()
    except Exception as e:
        if SF_DEBUG:
            print(f"[[DEBUG]] _sffuncspan.shutdown() failed: {e}", log=False)

    # Shutdown network hop C extension
    try:
        from . import fast_network_hop

        if fast_network_hop._NETWORKHOP_FAST_OK and fast_network_hop._sfnetworkhop:
            if SF_DEBUG:
                print("[[DEBUG]] Shutting down _sfnetworkhop before reinit", log=False)
            fast_network_hop._sfnetworkhop.shutdown()
    except Exception as e:
        if SF_DEBUG:
            print(f"[[DEBUG]] _sfnetworkhop.shutdown() failed: {e}", log=False)

    # Shutdown network request C extension (http.client body/header capture)
    try:
        from .patches.network_libraries import utils as net_utils

        if net_utils._FAST_NETWORKREQUEST_AVAILABLE and net_utils._sffastnetworkrequest:
            if SF_DEBUG:
                print(
                    "[[DEBUG]] Shutting down _sffastnetworkrequest before reinit",
                    log=False,
                )
            net_utils._sffastnetworkrequest.shutdown()
    except Exception as e:
        if SF_DEBUG:
            print(f"[[DEBUG]] _sffastnetworkrequest.shutdown() failed: {e}", log=False)

    # Shutdown fast log C extension (core - shutdown last)
    try:
        if _FAST_OK and _sffastlog:
            if SF_DEBUG:
                print("[[DEBUG]] Shutting down _sffastlog before reinit", log=False)
            _sffastlog.shutdown()
    except Exception as e:
        if SF_DEBUG:
            print(f"[[DEBUG]] _sffastlog.shutdown() failed: {e}", log=False)

    # Reset initialization flags to force reinitialization
    _FAST_PRINT_READY = False
    _FUNCSPAN_READY = False
    _FUNCSPAN_PROFILER = None

    # Reset network hop flag
    from . import fast_network_hop

    fast_network_hop._FAST_NETWORKHOP_READY = False

    # Reset network request flag
    from .patches.network_libraries import utils as net_utils

    net_utils._FAST_NETWORKREQUEST_INITIALIZED = False

    # Reinitialize C extensions (but not patches)
    _ensure_fast_print_initialized()
    _ensure_funcspan_initialized()
    fast_network_hop._ensure_fast_networkhop_initialized()
    net_utils.init_fast_networkrequest_tracking()

    if SF_DEBUG:
        print(
            f"[[DEBUG]] reinitialize_after_fork() completed in PID {os.getpid()}",
            log=False,
        )
