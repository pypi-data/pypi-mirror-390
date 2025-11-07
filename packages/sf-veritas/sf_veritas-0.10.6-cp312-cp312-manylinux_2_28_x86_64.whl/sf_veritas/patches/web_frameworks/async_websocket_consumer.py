import inspect
import sys
import sysconfig
from functools import lru_cache, wraps
from typing import Any, Callable, Optional, Set, Tuple

from ...constants import SAILFISH_TRACING_HEADER
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
from ...thread_local import get_or_set_sf_trace_id
from ...fast_network_hop import fast_send_network_hop_fast, fast_send_network_hop, register_endpoint
from .utils import _unwrap_user_func

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# ────────────────────────────────────────────────────
# User-code predicate: skip stdlib & site-packages
# ────────────────────────────────────────────────────
_STDLIB = sysconfig.get_paths()["stdlib"]
_SITE_TAGS = ("site-packages", "dist-packages")
_SKIP_PREFIXES = (_STDLIB, "/usr/local/lib/python", "/usr/lib/python")


@lru_cache(maxsize=512)
def _is_user_code(path: Optional[str] = None) -> bool:
    """True only for your application files."""
    if not path or path.startswith("<"):
        return False
    for p in _SKIP_PREFIXES:
        if path.startswith(p):
            return False
    return not any(tag in path for tag in _SITE_TAGS)


# ────────────────────────────────────────────────────
# Patch AsyncConsumer.__call__ to hook connect + receive
# ────────────────────────────────────────────────────
def patch_async_consumer_call():
    """
    Wraps AsyncConsumer.__call__ so that for each HTTP or WebSocket
    connection:
      1) SAILFISH_TRACING_HEADER → ContextVar
      2) Emit a NetworkHop at first user frame in websocket_connect
      3) Dynamically wrap websocket_receive to emit a hop on first message
      4) Forward any exception to custom_excepthook
    """
    try:
        from channels.consumer import AsyncConsumer  # type: ignore

        orig_call = AsyncConsumer.__call__
    except:
        if PRINT_CONFIGURATION_STATUSES:
            print("Channels AsyncConsumer not found; skipping patch", log=False)
        return

    if PRINT_CONFIGURATION_STATUSES:
        print("Patching AsyncConsumer.__call__ for NetworkHops", log=False)

    @wraps(orig_call)
    async def custom_call(self, scope, receive, send):
        # — Propagate header into ContextVar —
        header_val = None
        if scope["type"] in ("http", "websocket"):
            for name, val in scope.get("headers", []):
                if name.lower() == SAILFISH_TRACING_HEADER.lower().encode():
                    header_val = val.decode("utf-8")
                    break
        get_or_set_sf_trace_id(header_val, is_associated_with_inbound_request=True)

        # — Capture request headers if enabled —
        req_headers = None
        if SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS:
            try:
                headers = scope.get("headers", [])
                req_headers = {
                    name.decode("utf-8"): val.decode("utf-8")
                    for name, val in headers
                }
                if SF_DEBUG:
                    print(f"[[async_websocket_consumer]] Captured request headers: {len(req_headers)} headers", log=False)
            except Exception as e:
                if SF_DEBUG:
                    print(f"[[async_websocket_consumer]] Failed to capture request headers: {e}", log=False)

        # — Capture request body if enabled (for HTTP, not WebSocket) —
        req_body = None
        body_parts = []
        body_size = 0
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY and scope["type"] == "http":
            try:
                # Save original receive before wrapping
                original_receive = receive

                async def receive_with_body():
                    nonlocal body_size
                    message = await original_receive()
                    if message["type"] == "http.request":
                        body_part = message.get("body", b"")
                        if body_part and body_size < _REQUEST_LIMIT_BYTES:
                            remaining = _REQUEST_LIMIT_BYTES - body_size
                            body_parts.append(body_part[:remaining])
                            body_size += len(body_part)
                    return message

                receive = receive_with_body
            except Exception as e:
                if SF_DEBUG:
                    print(f"[[async_websocket_consumer]] Failed to setup request body capture: {e}", log=False)

        # OTEL-STYLE: Capture endpoint info and pre-register
        endpoint_id = None
        endpoint_metadata = {}  # Store metadata for fallback

        def tracer(frame, event, _arg):
            nonlocal endpoint_id
            if event == "call":
                fn_path = frame.f_code.co_filename
                fn_name = frame.f_code.co_name

                if SF_DEBUG:
                    print(
                        f"[[async_websocket_consumer]] Tracer saw: {fn_name} @ {fn_path}:{frame.f_lineno} "
                        f"is_user_code={_is_user_code(fn_path)}",
                        log=False,
                    )

                if _is_user_code(fn_path):
                    hop_key = (fn_path, frame.f_lineno)

                    # Store metadata for potential fallback
                    endpoint_metadata["filename"] = fn_path
                    endpoint_metadata["line"] = frame.f_lineno
                    endpoint_metadata["name"] = fn_name

                    # Pre-register endpoint if not already registered
                    endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)
                    if endpoint_id is None:
                        if SF_DEBUG:
                            # Debug: Check if fast network hop is available
                            from ...fast_network_hop import _NETWORKHOP_FAST_OK, _FAST_NETWORKHOP_READY
                            print(
                                f"[[async_websocket_consumer]] Before register: _NETWORKHOP_FAST_OK={_NETWORKHOP_FAST_OK}, "
                                f"_FAST_NETWORKHOP_READY={_FAST_NETWORKHOP_READY}",
                                log=False,
                            )

                        endpoint_id = register_endpoint(
                            line=str(frame.f_lineno),
                            column="0",
                            name=fn_name,
                            entrypoint=fn_path,
                            route=None
                        )
                        if SF_DEBUG:
                            print(
                                f"[[async_websocket_consumer]] register_endpoint returned: {endpoint_id}",
                                log=False,
                            )

                        if endpoint_id >= 0:
                            _ENDPOINT_REGISTRY[hop_key] = endpoint_id
                            if SF_DEBUG:
                                print(
                                    f"[[async_websocket_consumer]] Registered endpoint: {fn_name} @ "
                                    f"{fn_path}:{frame.f_lineno} (id={endpoint_id})",
                                    log=False,
                                )

                    if SF_DEBUG:
                        print(
                            f"[[async_websocket_consumer]] Captured endpoint: {fn_name} "
                            f"({fn_path}:{frame.f_lineno}) endpoint_id={endpoint_id}",
                            log=False,
                        )

                    sys.setprofile(None)
                    return None
            return tracer

        sys.setprofile(tracer)

        # Track if we've emitted for this connection
        hop_emitted = False

        # Emit NetworkHop function - called when websocket_connect completes
        def emit_network_hop_sync():
            """Emit NetworkHop after websocket_connect handler runs."""
            nonlocal hop_emitted
            if hop_emitted:
                return
            hop_emitted = True

            if endpoint_id is not None and endpoint_id >= 0:
                # Fast path with C extension
                try:
                    _, session_id = get_or_set_sf_trace_id()

                    # Extract raw path and query string from scope for C to parse
                    raw_path = scope.get("path", None)  # e.g., "/ws/chat"
                    raw_query = scope.get("query_string", b"")  # e.g., b"room=123"

                    fast_send_network_hop_fast(
                        session_id=session_id,
                        endpoint_id=endpoint_id,
                        raw_path=raw_path,
                        raw_query_string=raw_query,
                        request_headers=req_headers,
                        request_body=None,  # WebSocket has no body
                        response_headers=None,
                        response_body=None,
                    )
                    if SF_DEBUG:
                        print(
                            f"[[async_websocket_consumer]] Emitted network hop (fast path): endpoint_id={endpoint_id}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG:
                        print(f"[[async_websocket_consumer]] Failed to emit (fast path): {e}", log=False)
            elif endpoint_metadata:
                # Fallback path without C extension
                try:
                    _, session_id = get_or_set_sf_trace_id()
                    if SF_DEBUG:
                        print(
                            f"[[async_websocket_consumer]] Using fallback: {endpoint_metadata['name']} @ "
                            f"{endpoint_metadata['filename']}:{endpoint_metadata['line']}",
                            log=False,
                        )
                    fast_send_network_hop(
                        session_id=session_id,
                        line=str(endpoint_metadata["line"]),
                        column="0",
                        name=endpoint_metadata["name"],
                        entrypoint=endpoint_metadata["filename"],
                    )
                    if SF_DEBUG:
                        print(
                            f"[[async_websocket_consumer]] Emitted network hop (fallback): "
                            f"{endpoint_metadata['name']}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG:
                        print(f"[[async_websocket_consumer]] Failed to emit (fallback): {e}", log=False)

        # Capture response headers and body
        resp_headers = None
        resp_body_parts = []
        resp_body_size = 0

        # Wrap send to capture response data AND emit after websocket.accept
        async def wrapped_send(message):
            nonlocal resp_headers, resp_body_size

            # Emit NetworkHop after WebSocket is accepted
            if message["type"] == "websocket.accept":
                if SF_DEBUG:
                    print(f"[[async_websocket_consumer]] WebSocket accepted, emitting NetworkHop", log=False)
                emit_network_hop_sync()

            # Capture response headers
            if message["type"] == "http.response.start" and SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                try:
                    headers = message.get("headers", [])
                    resp_headers = {
                        name.decode("utf-8"): val.decode("utf-8")
                        for name, val in headers
                    }
                    if SF_DEBUG:
                        print(f"[[async_websocket_consumer]] Captured response headers: {len(resp_headers)} headers", log=False)
                except Exception as e:
                    if SF_DEBUG:
                        print(f"[[async_websocket_consumer]] Failed to capture response headers: {e}", log=False)

            # Capture response body
            if message["type"] == "http.response.body" and SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                try:
                    body_part = message.get("body", b"")
                    if body_part and resp_body_size < _RESPONSE_LIMIT_BYTES:
                        remaining = _RESPONSE_LIMIT_BYTES - resp_body_size
                        resp_body_parts.append(body_part[:remaining])
                        resp_body_size += len(body_part)
                except Exception as e:
                    if SF_DEBUG:
                        print(f"[[async_websocket_consumer]] Failed to capture response body chunk: {e}", log=False)

            await send(message)

        # — Call through to original (handles connect, receive, disconnect) —
        try:
            await orig_call(self, scope, receive, wrapped_send)
        except Exception as exc:
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise
        finally:
            sys.setprofile(None)

    # Apply the patch
    AsyncConsumer.__call__ = custom_call

    if PRINT_CONFIGURATION_STATUSES:
        print("AsyncConsumer.__call__ patched successfully", log=False)
