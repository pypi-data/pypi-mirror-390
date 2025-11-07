# sf_veritas/custom_print.py
import builtins
import logging
import os
import sys

from . import app_config, transmit_exception_to_sailfish
from .env_vars import SF_DEBUG
from .thread_local import activate_reentrancy_guards_sys_stdout, get_or_set_sf_trace_id

logger = logging.getLogger(__name__)

# --- Optional native fast path (C extension) ---
try:
    from . import _sffastlog  # compiled extension

    _FAST_OK = True
except Exception:  # pragma: no cover
    _sffastlog = None
    _FAST_OK = False

# Keep an internal one-time init guard for the print fast path
_FAST_PRINT_READY = False

# GraphQL mutation for print statements (must match your server exactly)
# Mirrors interceptors.PrintInterceptor._QUERY variables/shape.
_COLLECT_PRINT_MUTATION = """
mutation CollectPrintStatements(
  $apiKey: String!,
  $serviceUuid: String!,
  $sessionId: String!,
  $contents: String!,
  $reentrancyGuardPreactive: Boolean!,
  $library: String!,
  $timestampMs: String!,
  $version: String!
) {
  collectPrintStatements(
    apiKey: $apiKey,
    serviceUuid: $serviceUuid,
    sessionId: $sessionId,
    contents: $contents,
    reentrancyGuardPreactive: $reentrancyGuardPreactive,
    library: $library,
    timestampMs: $timestampMs,
    version: $version
  )
}
""".strip()


def _ensure_fast_print_initialized() -> bool:
    """
    Lazily initialize the native print path. Safe to call every print; it becomes a no-op after the first success.
    """
    global _FAST_PRINT_READY

    if not _FAST_OK or _FAST_PRINT_READY:
        return _FAST_PRINT_READY

    # We require the same config used elsewhere in the package
    endpoint = getattr(app_config, "_sailfish_graphql_endpoint", None)
    api_key = getattr(app_config, "_sailfish_api_key", None)
    service_uuid = getattr(app_config, "_service_uuid", None)
    library = getattr(app_config, "library", "sailfish-python")
    version = getattr(app_config, "version", "0.0.0")
    http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0

    if not (endpoint and api_key and service_uuid):
        # Not configured yet; stay in Python fallback for now
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


def custom_print(*args, log=True, **kwargs):
    """
    Custom print function to intercept print statements.
    - Writes to real stdout (sys.__stdout__) to avoid recursion.
    - If log=True, ships the message via native _sffastlog.print_ when available,
      otherwise falls back to the Python interceptor path: sys.stdout.print_interceptor.do_send(...)
    """
    # Tag in debug without creating extra strings when not needed
    activate_reentrancy_guards_sys_stdout()

    # Build the message ONCE; use it for both console and network
    if args:
        # Fastest reasonable join; avoid f-strings on the hot path
        msg = " ".join(map(str, args))
    else:
        msg = ""

    # Write to the actual stdout (not our wrapper)
    if SF_DEBUG:
        # Keep your debug envelope; avoid doing any extra work when not in debug
        builtins._original_print(  # pylint: disable=protected-access
            "[[CUSTOM-PRINT]]", msg, "[[/CUSTOM-PRINT]]", file=sys.__stdout__, **kwargs
        )
    else:
        builtins._original_print(  # pylint: disable=protected-access
            msg, file=sys.__stdout__, **kwargs
        )

    # Optionally ship to backend
    if not log:
        return
    if not msg.strip():
        return

    # Get (or set) trace id exactly the way you do elsewhere
    _, trace_id = get_or_set_sf_trace_id()

    # Try native fast path; otherwise Python fallback via the PrintInterceptor attached to sys.stdout
    if _ensure_fast_print_initialized():
        try:
            # Your GraphQL schema includes "reentrancyGuardPreactive" for prints;
            # keep it false here to mirror previous behavior.
            _sffastlog.print_(contents=msg, session_id=str(trace_id), preactive=0)
            return
        except Exception as e:
            logger.exception(e)
            transmit_exception_to_sailfish(e)
            # fall back below
            pass

    # Python fallback (existing path)
    # NOTE: sys.stdout is replaced by UnifiedInterceptor, which carries `print_interceptor`.
    # If you’re not using UnifiedInterceptor in a given environment, ensure sys.stdout provides it.
    try:
        sys.stdout.print_interceptor.do_send((msg, trace_id), trace_id)
    except Exception:
        logger.exception(e)
        transmit_exception_to_sailfish(e)
        # As a last resort, swallow to keep print() non-fatal
        if SF_DEBUG:
            builtins._original_print(
                "[[CUSTOM-PRINT-FALLBACK-ERROR]] failed to send print payload [[/CUSTOM-PRINT-FALLBACK-ERROR]]",
                file=sys.__stdout__,
            )
