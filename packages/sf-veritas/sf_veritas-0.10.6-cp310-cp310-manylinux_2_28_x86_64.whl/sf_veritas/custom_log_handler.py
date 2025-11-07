import logging
from typing import Optional

from . import app_config
from .env_vars import PRINT_CONFIGURATION_STATUSES, SF_DEBUG
from .interceptors import LogInterceptor
from .thread_local import get_or_set_sf_trace_id, get_reentrancy_guard_logging_preactive

# Try native fast path (compiled C extension). If missing, we fall back.
try:
    from . import _sffastlog as _FASTMOD

    _FAST_OK = True
except Exception:
    _FASTMOD = None
    _FAST_OK = False


# Small constant table avoids attribute access for levelname on hot path
_LEVEL_NAME = {
    50: "CRITICAL",
    40: "ERROR",
    30: "WARNING",
    20: "INFO",
    10: "DEBUG",
    0: "NOTSET",
}


class CustomLogHandler(logging.Handler, LogInterceptor):
    """
    Ultra-light log handler:
      - Avoid Formatter unless explicitly set.
      - Avoid %-formatting if record.args is empty.
      - Prefer levelno→name map (micro faster than attribute lookup).
      - Fetch/generate trace_id once per emit (unchanged).
      - DIRECT native send via _sffastlog when available; Python fallback otherwise.
    """

    def __init__(self):
        logging.Handler.__init__(self)
        LogInterceptor.__init__(self, api_key=app_config._sailfish_api_key)
        if PRINT_CONFIGURATION_STATUSES:
            print("Intercepting log statements")

    def emit(self, record: logging.LogRecord, trace_id: Optional[str] = None):
        # Bind frequently used symbols to locals to reduce attribute/global lookups
        _formatter = self.formatter
        _get_tid = get_or_set_sf_trace_id
        _get_preactive = get_reentrancy_guard_logging_preactive
        _debug = SF_DEBUG
        _level_table = _LEVEL_NAME
        _fast = _FASTMOD
        _fast_ok = _FAST_OK
        _do_send = self.do_send  # Python fallback

        try:
            # FAST PATH message extraction:
            # - If a formatter is attached, defer to it (caller explicitly wants decorations)
            # - Otherwise:
            #     - If there are args, we must perform %-format (getMessage)
            #     - If no args and msg is already a str, reuse it directly (no str() allocation)
            #     - Else fall back to str(msg)
            if _formatter is None:
                if record.args:
                    log_entry = record.getMessage()
                else:
                    msg = record.msg
                    log_entry = msg if (msg.__class__ is str) else str(msg)
            else:
                log_entry = self.format(record)

            # Cheap ignore check (lives on LogInterceptor); skip everything if ignored
            # Keeps semantics identical while saving work on hot path
            try:
                if self.check_if_contents_should_be_ignored(log_entry):
                    return
            except AttributeError:
                # If not defined for some reason, proceed (older builds)
                pass

            # CHEAP LEVEL NAME:
            lvlno = record.levelno
            log_level = _level_table.get(lvlno)
            if log_level is None:  # uncommon/3rd-party custom levels
                log_level = record.levelname

            # TRACE ID ONCE (unchanged contract)
            if trace_id is None:
                _, trace_id = _get_tid(None)

            # Debug printing (rarely enabled)
            if _debug:
                # Avoid f-strings to skip extra work when disabled
                print(
                    "[[DEBUG custom_log_handler]]",
                    "trace_id=" + str(trace_id),
                    "[[" + log_level + "]]",
                    log_entry,
                    "[[/DEBUG]]",
                    log=False,
                )

            # ---------- Native fast path ----------
            if _fast_ok and _fast is not None:
                try:
                    preactive = bool(_get_preactive())
                    # Single C call → copy → enqueue → return; HTTP happens on native thread
                    _fast.log(
                        level=log_level or "UNKNOWN",
                        contents=log_entry,
                        session_id=str(trace_id),
                        preactive=preactive,
                    )
                    return
                except Exception as _e:
                    print(
                        "[_sffastlog] fast-path failed; falling back:",
                        _e,
                        log=False,
                    )
                    # fall through to Python path

            # ---------- Python fallback (deferred batching/async) ----------
            _do_send((log_level, log_entry, trace_id), trace_id)

        except Exception as e:  # keep lean; avoid storms on storms
            if _debug:
                print("CustomLogHandler.emit error:", e)
            self.handleError(record)
