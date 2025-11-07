import json
import logging
import os
import re
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

from . import app_config, transmit_exception_to_sailfish
from .env_vars import PRINT_CONFIGURATION_STATUSES, SF_DEBUG, SF_LOG_IGNORE_REGEX
from .package_metadata import PACKAGE_LIBRARY_TYPE, __version__
from .regular_data_transmitter import ServiceIdentifier
from .request_utils import non_blocking_post
from .thread_local import (  # reentrancy_guard, activate_reentrancy_guards_logging_preactive,
    activate_reentrancy_guards_logging,
    get_or_set_sf_trace_id,
)
from .timeutil import TimeSync
from .types import CustomJSONEncoderForFrameInfo, FrameInfo
from .utils import serialize_json_with_exclusions, strtobool

# Precompile once (was re.match(pattern,..) per log)
# Loaded from SF_LOG_IGNORE_REGEX environment variable (default: suppress /healthz and /graphql/ 2xx)
_IGNORE_RE = re.compile(SF_LOG_IGNORE_REGEX)

logger = logging.getLogger(__name__)


class OutputInterceptor(object):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or app_config._sailfish_api_key
        self.endpoint = app_config._sailfish_graphql_endpoint
        self.operation_name: Optional[str] = ""
        self.query_type = "mutation"
        self.service_identifier = ServiceIdentifier()

    @property
    def query_name(self) -> str:
        return (
            self.operation_name[0].lower() + self.operation_name[1:]
            if self.operation_name
            else ""
        )

    def get_default_variables(self, session_id: Optional[str] = None):
        trace_id = session_id
        if not session_id:
            _, trace_id = get_or_set_sf_trace_id(session_id)
        timestamp_ms = TimeSync.get_instance().get_utc_time_in_ms()
        return {
            "apiKey": self.api_key,
            "serviceUuid": app_config._service_uuid,
            "library": PACKAGE_LIBRARY_TYPE,
            "sessionId": trace_id,
            "timestampMs": str(timestamp_ms),
            "version": __version__,
        }

    def get_variables(
        self,
        additional_variables: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        additional_variables = additional_variables or {}
        return {**additional_variables, **self.get_default_variables(session_id)}

    def check_if_contents_should_be_ignored(
        self, contents
    ):  # pylint: disable=unused-argument
        return False

    def _send_app_identifier(self, session_id: str) -> None:
        if SF_DEBUG:
            print("_send_app_identifier...SENDING DATA...args=", set(), log=False)
        self.service_identifier.do_send(set())

    def do_send(self, args, session_id: str) -> None:
        self._send_app_identifier(session_id)
        if SF_DEBUG:
            print(f"[[OutputInterceptor.do_send]] session_id={session_id}", log=False)
        try:
            self.send(*args)
        except RuntimeError:
            return


# sf_veritas/interceptors.py  (excerpt: LogInterceptor)
import time
from typing import Callable, Tuple

from . import app_config
from .env_vars import SF_DEBUG
from .request_utils import non_blocking_post_deferred  # Python fallback
from .thread_local import get_reentrancy_guard_logging_preactive

# Try native fast path (compiled C extension)
try:
    from . import _sffastlog

    _FAST_OK = True
except Exception:
    _sffastlog = None
    _FAST_OK = False


# GraphQL mutation (camelCase variables) — keep identical to your server schema
_COLLECT_LOGS_OP = "CollectLogs"
_COLLECT_LOGS_MUTATION = """
mutation CollectLogs(
  $apiKey: String!,
  $serviceUuid: String!,
  $sessionId: String!,
  $level: String!,
  $contents: String!,
  $reentrancyGuardPreactive: Boolean!,
  $library: String!,
  $timestampMs: String!,
  $version: String!
) {
  collectLogs(
    apiKey: $apiKey,
    serviceUuid: $serviceUuid,
    sessionId: $sessionId,
    level: $level,
    contents: $contents,
    reentrancyGuardPreactive: $reentrancyGuardPreactive,
    library: $library,
    timestampMs: $timestampMs,
    version: $version
  )
}
""".strip()

# ---------- Prints (GraphQL identical to your current schema) ----------
_COLLECT_PRINT_OP = "CollectPrintStatements"
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


class LogInterceptor:
    """
    Uses native _sffastlog if present; otherwise falls back to Python deferred sender.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Use app_config instead of os.environ to avoid KeyError
        self.endpoint = getattr(app_config, "_sailfish_graphql_endpoint", None)
        self.service_uuid = (
            getattr(app_config, "_service_uuid", None)
            or getattr(app_config, "service_uuid", None)
            or "unknown"
        )
        self.library = getattr(app_config, "library", "sailfish-python")
        self.version = getattr(app_config, "version", "0.0.0")

        if _FAST_OK and self.endpoint:
            try:
                http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0
                if SF_DEBUG:
                    print(
                        f"[[LogInterceptor.__init__]] Calling _sffastlog.init() with url={self.endpoint}"
                    )
                ok = _sffastlog.init(
                    url=self.endpoint,
                    query=_COLLECT_LOGS_MUTATION,
                    api_key=self.api_key,
                    service_uuid=str(self.service_uuid),
                    library=str(self.library),
                    version=str(self.version),
                    http2=http2,
                )
                if ok and PRINT_CONFIGURATION_STATUSES:
                    print("[_sffastlog] initialized (libcurl sender for logs)")
                elif PRINT_CONFIGURATION_STATUSES:
                    print(f"[_sffastlog] init returned {ok}")
            except Exception as e:
                if PRINT_CONFIGURATION_STATUSES:
                    print(f"[_sffastlog] init failed; falling back: {e}")

    def check_if_contents_should_be_ignored(self, contents: str) -> bool:
        """
        Check if log contents should be ignored (not sent to Sailfish).
        Uses SF_LOG_IGNORE_REGEX environment variable (default: suppress /healthz and /graphql/ 2xx).

        Returns:
            True if the log should be ignored, False otherwise
        """
        return _IGNORE_RE.match(contents or "") is not None

    def do_send(self, payload: Tuple[str, str, str], trace_id: str):
        """
        payload: (log_level, log_entry, session_id)
        """
        level, contents, session_id = payload
        preactive = bool(get_reentrancy_guard_logging_preactive())

        if SF_DEBUG:
            print(
                f"[[LogInterceptor.do_send]] level={level}, session_id={session_id}, _FAST_OK={_FAST_OK}",
                log=False,
            )

        if _FAST_OK:
            try:
                if SF_DEBUG:
                    print(
                        f"[[LogInterceptor.do_send]] Calling _sffastlog.log()",
                        log=False,
                    )
                _sffastlog.log(
                    level=level or "UNKNOWN",
                    contents=contents,
                    session_id=str(session_id),
                    preactive=preactive,
                )
                if SF_DEBUG:
                    print(
                        f"[[LogInterceptor.do_send]] _sffastlog.log() succeeded",
                        log=False,
                    )
                return
            except Exception as e:
                logger.exception(e)
                transmit_exception_to_sailfish(e)
                if SF_DEBUG:
                    print(f"[_sffastlog] log failed; fallback path: {e}", log=False)

        # --- Python fallback (deferred) ---
        ts_ms = time.time_ns() // 1_000_000
        endpoint = self.endpoint
        op = _COLLECT_LOGS_OP
        query = _COLLECT_LOGS_MUTATION
        api_key = self.api_key
        service_uuid = self.service_uuid
        library = self.library
        version = self.version

        def _builder():
            vars = {
                "apiKey": api_key,
                "serviceUuid": str(service_uuid),
                "sessionId": str(session_id),
                "level": level or "UNKNOWN",
                "contents": contents,
                "reentrancyGuardPreactive": preactive,
                "library": str(library),
                "timestampMs": str(ts_ms),
                "version": str(version),
            }
            return endpoint, op, query, vars

        non_blocking_post_deferred(_builder)

    def shutdown(self):
        if _FAST_OK:
            try:
                _sffastlog.shutdown()
            except Exception:
                pass


# ---------------- Prints (NEW native fast path) ----------------
class PrintInterceptor(OutputInterceptor):
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = app_config._sailfish_api_key
        super().__init__(api_key)
        self.operation_name = _COLLECT_PRINT_OP

        # Cache the query string
        self._QUERY = _COLLECT_PRINT_MUTATION

        # Native fast path for print, if available
        self._fast_print_ok = False
        if _FAST_OK:
            try:
                http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0
                ok = _sffastlog.init_print(
                    url=self.endpoint,
                    query=self._QUERY,
                    api_key=self.api_key,
                    service_uuid=str(app_config._service_uuid),
                    library=PACKAGE_LIBRARY_TYPE,
                    version=__version__,
                    http2=http2,
                )
                self._fast_print_ok = bool(ok)
                if PRINT_CONFIGURATION_STATUSES:
                    print("[_sffastlog] initialized (prints)")  # , log=False)
                if self._fast_print_ok and PRINT_CONFIGURATION_STATUSES:
                    print("[_sffastlog] initialized (prints)")  # , log=False)
            except Exception as e:
                logger.exception(e)
                transmit_exception_to_sailfish(e)
                if PRINT_CONFIGURATION_STATUSES:
                    print(
                        "[_sffastlog] init_print failed; fallback:", e
                    )  # , log=False)

    def send(self, contents: str, session_id: str):
        # Drop obvious noise early (cheap)
        if _IGNORE_RE.match(contents or ""):
            return

        preactive = False  # printing path uses preactive only if you need it later
        if self._fast_print_ok:
            try:
                _sffastlog.print_(  # exposed as print_ to avoid name clash
                    contents=contents,
                    session_id=str(session_id),
                    preactive=preactive,
                )
                return
            except Exception as e:
                logger.exception(e)
                transmit_exception_to_sailfish(e)
                if SF_DEBUG:
                    print("[_sffastlog] print_ failed; fallback:", e, log=False)

        # Python fallback: fast minimal dict and post
        d = self.get_default_variables(session_id)
        variables = {
            "apiKey": d["apiKey"],
            "serviceUuid": d["serviceUuid"],
            "sessionId": d["sessionId"],
            "library": d["library"],
            "timestampMs": d["timestampMs"],
            "version": d["version"],
            "contents": contents,
            "reentrancyGuardPreactive": False,
        }
        if SF_DEBUG:
            print(f"[[PrintInterceptor.send]] endpoint={self.endpoint}, sessionId={variables['sessionId']}, contents={contents[:50]!r}", log=False)
        non_blocking_post(self.endpoint, self.operation_name, self._QUERY, variables)
        if SF_DEBUG:
            print(f"[[PrintInterceptor.send]] non_blocking_post completed", log=False)


_COLLECT_EXCEPTION_OP = "CollectExceptions"
_COLLECT_EXCEPTION_MUTATION = """
mutation CollectExceptions(
  $apiKey: String!,
  $serviceUuid: String!,
  $sessionId: String!,
  $exceptionMessage: String!,
  $wasCaught: Boolean!,
  $traceJson: String!,
  $reentrancyGuardPreactive: Boolean!,
  $library: String!,
  $timestampMs: String!,
  $version: String!,
  $isFromLocalService: Boolean!
) {
  collectExceptions(
    apiKey: $apiKey,
    serviceUuid: $serviceUuid,
    sessionId: $sessionId,
    exceptionMessage: $exceptionMessage,
    wasCaught: $wasCaught,
    traceJson: $traceJson,
    reentrancyGuardPreactive: $reentrancyGuardPreactive,
    library: $library,
    timestampMs: $timestampMs,
    version: $version,
    isFromLocalService: $isFromLocalService
  )
}
""".strip()


class ExceptionInterceptor(OutputInterceptor):
    def __init__(self, api_key: str = app_config._sailfish_api_key):
        super().__init__(api_key)
        self.operation_name = _COLLECT_EXCEPTION_OP
        self._QUERY = _COLLECT_EXCEPTION_MUTATION

        # Native fast path for exceptions, if available
        self._fast_exception_ok = False
        if _FAST_OK:
            try:
                http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0
                ok = _sffastlog.init_exception(
                    url=self.endpoint,
                    query=self._QUERY,
                    api_key=self.api_key,
                    service_uuid=str(app_config._service_uuid),
                    library=PACKAGE_LIBRARY_TYPE,
                    version=__version__,
                    http2=http2,
                )
                self._fast_exception_ok = bool(ok)
                if self._fast_exception_ok and PRINT_CONFIGURATION_STATUSES:
                    print("[_sffastlog] initialized (exceptions)", log=False)
                if PRINT_CONFIGURATION_STATUSES:
                    print(
                        f"[_sffastlog] exception initialization status={ok}", log=False
                    )
            except Exception as e:
                logger.exception(e)
                transmit_exception_to_sailfish(e)
                if PRINT_CONFIGURATION_STATUSES:
                    print("[_sffastlog] init_exception failed; fallback:", e, log=False)

    def send(
        self,
        exception_message: str,
        trace: List[FrameInfo],
        session_id: str,
        was_caught: bool = True,
        is_from_local_service: bool = False,
    ):
        trace_json = json.dumps(trace, cls=CustomJSONEncoderForFrameInfo)

        if self._fast_exception_ok:
            try:
                _sffastlog.exception(
                    exception_message=exception_message,
                    trace_json=trace_json,
                    session_id=str(session_id),
                    was_caught=was_caught,
                    is_from_local_service=is_from_local_service,
                )
                return
            except Exception as e:
                logger.exception(e)
                transmit_exception_to_sailfish(e)
                if SF_DEBUG:
                    print("[_sffastlog] exception failed; fallback:", e, log=False)

        # Python fallback
        query = f"""
        {self.query_type} {self.operation_name}($apiKey: String!, $serviceUuid: String!, $sessionId: String!, $exceptionMessage: String!, $wasCaught: Boolean!, $traceJson: String!, $reentrancyGuardPreactive: Boolean!, $library: String!, $timestampMs: String!, $version: String!, $isFromLocalService: Boolean!) {{
            {self.query_name}(apiKey: $apiKey, serviceUuid: $serviceUuid, sessionId: $sessionId, exceptionMessage: $exceptionMessage, wasCaught: $wasCaught, traceJson: $traceJson, reentrancyGuardPreactive: $reentrancyGuardPreactive, library: $library, timestampMs: $timestampMs, version: $version, isFromLocalService: $isFromLocalService)
        }}
        """

        if SF_DEBUG:
            print("SENDING EXCEPTION...", log=False)
        non_blocking_post(
            self.endpoint,
            self.operation_name,
            query,
            self.get_variables(
                {
                    "apiKey": self.api_key,
                    "exceptionMessage": exception_message,
                    "traceJson": trace_json,
                    "reentrancyGuardPreactive": False,
                    "wasCaught": was_caught,
                    "isFromLocalService": is_from_local_service,
                },
                session_id,
            ),
        )


class CollectMetadataTransmitter(OutputInterceptor):
    def __init__(self, api_key: str = app_config._sailfish_api_key):
        super().__init__(api_key)
        self.operation_name = "CollectMetadata"

    def send(
        self,
        user_id: str,
        traits: Optional[Dict[str, Any]],
        traits_json: Optional[str],
        override: bool,
        session_id: str,
    ):
        if traits is None and traits_json is None:
            raise Exception(
                'Must pass in either traits or traits_json to "add_or_update_traits"'
            )
        query = f"""
        {self.query_type} {self.operation_name}($apiKey: String!, $serviceUuid: String!, $sessionId: String!, $userId: String!, $traitsJson: String!, $excludedFields: [String!]!, $library: String!, $timestampMs: String!, $version: String!, $override: Boolean!) {{
            {self.query_name}(apiKey: $apiKey, serviceUuid: $serviceUuid, sessionId: $sessionId, userId: $userId, traitsJson: $traitsJson, excludedFields: $excludedFields, library: $library, timestampMs: $timestampMs, version: $version, override: $override)
        }}
        """

        excluded_fields = []
        if traits_json is None:
            traits_json, excluded_fields = serialize_json_with_exclusions(traits)

        variables = self.get_variables(
            {
                "userId": user_id,
                "traitsJson": traits_json,
                "excludedFields": excluded_fields,
                "override": override,
            },
            session_id,
        )

        non_blocking_post(self.endpoint, self.operation_name, query, variables)
