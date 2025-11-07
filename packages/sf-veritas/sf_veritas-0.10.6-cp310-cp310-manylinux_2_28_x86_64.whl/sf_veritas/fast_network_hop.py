"""
Ultra-fast network hop sender using C extension with endpoint pre-registration.
"""

import os
from logging import getLogger
from typing import Optional, Tuple

from .regular_data_transmitter import NetworkHopsTransmitter
from .thread_local import is_network_recording_suppressed

logger = getLogger(__name__)

# Optional native fast path for network hops (C extension)
# LAZY IMPORT: Don't import at module level to avoid circular import
# Import will happen in _ensure_fast_networkhop_initialized() when first needed
_sfnetworkhop = None
_NETWORKHOP_FAST_OK = None  # None = not yet attempted, True = success, False = failed

_FAST_NETWORKHOP_READY = False  # one-time guard for native networkhop init

# GraphQL mutation string for network hops (with optional body/header capture)
_COLLECT_NETWORKHOP_MUTATION = (
    "mutation collectNetworkHops("
    "$apiKey: String!,"
    "$sessionId: String!,"
    "$timestampMs: String!,"
    "$line: String!,"
    "$column: String!,"
    "$name: String!,"
    "$entrypoint: String!,"
    "$route: String,"
    "$queryParams: String,"
    "$serviceUuid: String,"
    "$requestHeaders: String,"
    "$requestBody: String,"
    "$responseHeaders: String,"
    "$responseBody: String"
    "){collectNetworkHops("
    "apiKey:$apiKey,sessionId:$sessionId,timestampMs:$timestampMs,"
    "line:$line,column:$column,name:$name,entrypoint:$entrypoint,"
    "route:$route,queryParams:$queryParams,serviceUuid:$serviceUuid,requestHeaders:$requestHeaders,"
    "requestBody:$requestBody,responseHeaders:$responseHeaders,"
    "responseBody:$responseBody)}"
)


def _ensure_fast_networkhop_initialized() -> bool:
    global _FAST_NETWORKHOP_READY, _sfnetworkhop, _NETWORKHOP_FAST_OK

    SF_DEBUG = os.getenv("SF_DEBUG", "false").lower() == "true"

    # PERFORMANCE: Skip network hop extension when testing network library only
    if os.getenv("TESTING_NETWORK_LIBRARY_ONLY", "0") == "1":
        if SF_DEBUG:
            print(
                "[[_ensure_fast_networkhop_initialized]] Network hop extension disabled (TESTING_NETWORK_LIBRARY_ONLY=1)",
                log=False,
            )
        return False

    # LAZY IMPORT: Try to import C extension on first use
    if _NETWORKHOP_FAST_OK is None:
        try:
            from . import _sfnetworkhop as _sfnh_module

            _sfnetworkhop = _sfnh_module
            _NETWORKHOP_FAST_OK = True
            if SF_DEBUG:
                print(
                    f"[[_ensure_fast_networkhop_initialized]] Successfully imported _sfnetworkhop C extension",
                    log=False,
                )
        except Exception as e:
            if SF_DEBUG:
                print(
                    f"[[_ensure_fast_networkhop_initialized]] Failed to import _sfnetworkhop C extension: {e}",
                    log=False,
                )
            _sfnetworkhop = None
            _NETWORKHOP_FAST_OK = False

    if not _NETWORKHOP_FAST_OK:
        if SF_DEBUG:
            print(
                f"[[_ensure_fast_networkhop_initialized]] C extension not available (_NETWORKHOP_FAST_OK=False)",
                log=False,
            )
        return False

    if _FAST_NETWORKHOP_READY:
        if SF_DEBUG:
            print(
                f"[[_ensure_fast_networkhop_initialized]] Already initialized, returning True",
                log=False,
            )
        return True

    from . import app_config

    endpoint = getattr(app_config, "_sailfish_graphql_endpoint", None)
    api_key = getattr(app_config, "_sailfish_api_key", None)
    service_uuid = getattr(app_config, "_service_uuid", None)
    http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0

    if SF_DEBUG:
        print(
            f"[[_ensure_fast_networkhop_initialized]] Config: endpoint={bool(endpoint)}, api_key={bool(api_key)}, service_uuid={bool(service_uuid)}",
            log=False,
        )

    if not (endpoint and api_key and service_uuid):
        if SF_DEBUG:
            print(
                f"[[_ensure_fast_networkhop_initialized]] Missing required config, returning False",
                log=False,
            )
        return False

    try:
        if SF_DEBUG:
            print(
                f"[[_ensure_fast_networkhop_initialized]] Calling _sfnetworkhop.init() with url={endpoint}",
                log=False,
            )
        ok = _sfnetworkhop.init(
            url=endpoint,
            query=_COLLECT_NETWORKHOP_MUTATION,
            api_key=str(api_key),
            service_uuid=str(service_uuid),
            http2=http2,
        )
        _FAST_NETWORKHOP_READY = bool(ok)
        if SF_DEBUG:
            print(
                f"[[_ensure_fast_networkhop_initialized]] _sfnetworkhop.init() returned {ok}, _FAST_NETWORKHOP_READY={_FAST_NETWORKHOP_READY}",
                log=False,
            )
    except Exception as e:
        if SF_DEBUG:
            print(
                f"[[_ensure_fast_networkhop_initialized]] _sfnetworkhop.init() raised exception: {e}",
                log=False,
            )
        _FAST_NETWORKHOP_READY = False

    return _FAST_NETWORKHOP_READY


def register_endpoint(
    line: str, column: str, name: str, entrypoint: str, route: str = None
) -> int:
    """
    Register a web framework endpoint's invariant fields once.
    Returns an endpoint_id usable with fast_send_network_hop_fast(...).

    Args:
        line: Line number where the endpoint is defined
        column: Column number (typically "0")
        name: Function name of the endpoint
        entrypoint: File path where the endpoint is defined
        route: Route pattern (e.g., "/api/users/{id}") - optional
    """
    SF_DEBUG = os.getenv("SF_DEBUG", "false").lower() == "true"

    if SF_DEBUG:
        print(
            f"[[register_endpoint]] Called for {name} @ {entrypoint}:{line} (route={route})",
            log=False,
        )

    if not _ensure_fast_networkhop_initialized():
        if SF_DEBUG:
            print(
                f"[[register_endpoint]] _ensure_fast_networkhop_initialized() returned False, returning -1",
                log=False,
            )
        return -1
    try:
        eid = _sfnetworkhop.register_endpoint(
            line=line, column=column, name=name, entrypoint=entrypoint, route=route
        )
        if SF_DEBUG:
            print(
                f"[[register_endpoint]] _sfnetworkhop.register_endpoint() returned {eid}",
                log=False,
            )
        return int(eid)
    except Exception as e:
        if SF_DEBUG:
            print(
                f"[[register_endpoint]] _sfnetworkhop.register_endpoint() raised exception: {e}",
                log=False,
            )
        return -1


def fast_send_network_hop_fast(
    session_id: str,
    endpoint_id: int,
    raw_path: str = None,
    raw_query_string: bytes = None,
    request_headers: dict = None,
    request_body: bytes = None,
    response_headers: dict = None,
    response_body: bytes = None,
) -> None:
    """
    ULTRA-FAST PATH: Assumes initialization already happened (checked once at startup).
    Optionally accepts request/response headers and body for capture.

    Args:
        session_id: Unique session identifier
        endpoint_id: Pre-registered endpoint ID
        raw_path: Optional actual request path (e.g., "/log") - passed to C for JSON escaping
        raw_query_string: Optional raw query string bytes (e.g., b"foo=5") - passed to C for decoding/escaping
        request_headers: Optional dict of request headers
        request_body: Optional request body (bytes, str, or list of chunks)
        response_headers: Optional dict of response headers
        response_body: Optional response body (bytes, str, or list of chunks)
    """
    # Check if network recording is suppressed (e.g., by @skip_network_tracing decorator)
    if is_network_recording_suppressed():
        return

    # HOT PATH OPTIMIZATION: Skip initialization check after first successful init
    if not _FAST_NETWORKHOP_READY:
        if not _ensure_fast_networkhop_initialized():
            return

    # Direct C call - no exception handling (C code is bulletproof)
    if endpoint_id >= 0:
        # Check if we need the extended path (with route/query/body/header capture)
        has_extended_data = (
            raw_path is not None
            or raw_query_string is not None
            or request_headers is not None
            or request_body is not None
            or response_headers is not None
            or response_body is not None
        )

        if has_extended_data:
            # Use extended capture path - C handles all decoding/escaping
            _sfnetworkhop.networkhop_with_bodies(
                session_id=session_id,
                endpoint_id=endpoint_id,
                raw_path=raw_path,
                raw_query_string=raw_query_string,
                request_headers=request_headers,
                request_body=request_body,
                response_headers=response_headers,
                response_body=response_body,
            )
        else:
            # Ultra-fast path with NO extra data
            _sfnetworkhop.networkhop_fast(
                session_id=session_id, endpoint_id=endpoint_id
            )


def fast_send_network_hop(
    session_id: str, line: str, column: str, name: str, entrypoint: str
):
    """
    Backward-compatible API (not used by patched FastAPI; kept for other callers).
    """
    # Check if network recording is suppressed (e.g., by @skip_network_tracing decorator)
    if is_network_recording_suppressed():
        return

    if _ensure_fast_networkhop_initialized():
        try:
            # Old slow path in C; kept for compatibility
            _sfnetworkhop.networkhop(
                session_id=session_id,
                line=line,
                column=column,
                name=name,
                entrypoint=entrypoint,
            )
            return
        except Exception:
            pass

    # Fallback to Python transmitter
    NetworkHopsTransmitter().send(
        session_id=session_id,
        line=line,
        column=column,
        name=name,
        entrypoint=entrypoint,
    )
