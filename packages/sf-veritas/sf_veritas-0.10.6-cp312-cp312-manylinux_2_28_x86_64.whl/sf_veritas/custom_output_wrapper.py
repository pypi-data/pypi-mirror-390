# sf_veritas/custom_output_wrapper.py
import os
import sys

from . import app_config
from .env_vars import PRINT_CONFIGURATION_STATUSES
from .interceptors import PrintInterceptor
from .thread_local import _thread_locals, get_or_set_sf_trace_id

# ---- optional native fast path (C extension) ----
try:
    from . import _sffastlog  # compiled extension with ring + libcurl sender

    _FAST_OK = True
except Exception:  # pragma: no cover
    _sffastlog = None
    _FAST_OK = False

_FAST_PRINT_READY = False  # one-time init guard


def _ensure_fast_print_initialized() -> bool:
    """Idempotent, cheap check to init native print path once."""
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
        return False  # not configured yet

    # GraphQL mutation for print statements (must match server)
    query = (
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

    try:
        ok = _sffastlog.init_print(
            url=endpoint,
            query=query,
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


class CustomOutputWrapper:
    """
    Ultra-thin sys.stdout wrapper:
      - Writes straight to the real stream to preserve console output.
      - If native fast path is ready, send to C ring immediately.
      - Otherwise, fall back to PrintInterceptor (Python path).
      - No locks, no regex, no unconditional flush.
    """

    __slots__ = ("original", "print_interceptor")

    def __init__(self, original):
        self.original = original
        self.print_interceptor = PrintInterceptor()

    def write(self, msg):
        # Respect your reentrancy guard quickly
        if getattr(_thread_locals, "reentrancy_guard_logging_active", False):
            self.original.write(msg)
            return

        # Always write to the real stream first (don’t flush unless caller asks)
        self.original.write(msg)

        # Cheap ignore cases (optional): skip totally empty or pure newline
        if not msg or msg == "\n":
            return

        # Build once
        message = msg
        _, trace_id = get_or_set_sf_trace_id()

        # Native fast path (C) — lowest overhead
        if _ensure_fast_print_initialized():
            try:
                _sffastlog.print_(
                    contents=message, session_id=str(trace_id), preactive=0
                )
                return
            except Exception:
                pass  # fall through to Python fallback

        # Python fallback path
        self.print_interceptor.do_send((message, trace_id), trace_id)

    def flush(self):
        # Only flush when caller flushes (keeps latency down)
        self.original.flush()

    def __getattr__(self, attr):
        return getattr(self.original, attr)


def setup_custom_output_wrappers():
    # Import here to avoid circular dependency
    from .print_override import override_print

    if PRINT_CONFIGURATION_STATUSES:
        sys.__stdout__.write("setup_custom_output_wrappers\n")

    # First override print to support log=True/False parameter
    override_print()

    # Then wrap stdout for interception
    sys.stdout = CustomOutputWrapper(sys.stdout)

    if PRINT_CONFIGURATION_STATUSES:
        sys.__stdout__.write("setup_custom_output_wrappers...DONE\n")


def get_custom_output_wrapper_django():
    """Django-specific wrapper setup function called by Django patch."""
    setup_custom_output_wrappers()
