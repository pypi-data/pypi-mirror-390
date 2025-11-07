# sf_veritas/patches/network_libraries/http_client.py
import os
import time
from typing import List, Optional, Tuple

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

from ... import _sffastnetworkrequest as _fast  # native module
from ...env_vars import SF_DEBUG
from ...thread_local import is_network_recording_suppressed, trace_id_ctx
from .utils import init_fast_header_check, inject_headers_ultrafast

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False
# --- Native fast path (C) readiness probe -------------------------
_FAST = None


def _fast_ready() -> bool:
    global _FAST
    if _FAST is None:
        try:
            _FAST = _fast

            if SF_DEBUG:
                try:
                    print(
                        "[http_client] _sffastnetworkrequest loaded successfully",
                        log=False,
                    )
                except TypeError:
                    print("[http_client] _sffastnetworkrequest loaded successfully")
        except Exception as e:
            _FAST = False

            if SF_DEBUG:
                try:
                    print(
                        f"[http_client] _sffastnetworkrequest NOT available: {e}",
                        log=False,
                    )
                except TypeError:
                    print(f"[http_client] _sffastnetworkrequest NOT available: {e}")
    if _FAST is False:
        return False
    try:
        ready = bool(_FAST.is_ready())

        if SF_DEBUG:
            try:
                print(
                    f"[http_client] _sffastnetworkrequest.is_ready() = {ready}",
                    log=False,
                )
            except TypeError:
                print(f"[http_client] _sffastnetworkrequest.is_ready() = {ready}")
        return ready
    except Exception as e:
        if SF_DEBUG:
            try:
                print(f"[http_client] is_ready() check failed: {e}", log=False)
            except TypeError:
                print(f"[http_client] is_ready() check failed: {e}")
        return False


def _split_headers_and_body_from_send_chunk(
    chunk: memoryview, state
) -> Tuple[Optional[bytes], Optional[bytes]]:
    if state["seen_hdr_end"]:
        return None, bytes(chunk)

    mv = chunk
    pos = mv.tobytes().find(b"\r\n\r\n")
    if pos == -1:
        state["hdr_buf"].append(bytes(mv))
        return None, None

    hdr_part = bytes(mv[: pos + 4])
    body_part = bytes(mv[pos + 4 :])
    state["hdr_buf"].append(hdr_part)
    state["seen_hdr_end"] = True
    return b"".join(state["hdr_buf"]), body_part if body_part else None


def _parse_request_headers_from_block(block: bytes) -> dict:
    headers = {}
    lines = block.split(b"\r\n")
    for raw in lines[1:]:
        if not raw:
            break
        i = raw.find(b":")
        if i <= 0:
            continue
        k = raw[:i].decode("latin1", "replace").strip()
        v = raw[i + 1 :].decode("latin1", "replace").strip()
        headers[k] = v
    return headers


def _tee_preload_active() -> bool:
    """Detect if the LD_PRELOAD tee is active; if so, skip Python-level patch."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    # match our shipped name
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def patch_http_client(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    ALWAYS patch for header injection (trace_id + funcspan_override).
    Skip capture/emission if LD_PRELOAD tee is active (socket layer already captures).

    This ensures headers propagate correctly regardless of capture mechanism.
    """
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(domains_to_not_propagate_headers_to or [])
        if SF_DEBUG:
            try:
                print(
                    "[http_client] LD_PRELOAD tee active; patching for headers only (no capture)",
                    log=False,
                )
            except TypeError:
                print(
                    "[http_client] LD_PRELOAD tee active; patching for headers only (no capture)"
                )

    # Check if C extension is available for capture (not required for header injection)
    fast_available = False
    if not preload_active:
        fast_available = _fast_ready()
        if not fast_available and SF_DEBUG:
            try:
                print(
                    "[http_client] C extension not ready - will patch for headers only (no capture)",
                    log=False,
                )
            except TypeError:
                print(
                    "[http_client] C extension not ready - will patch for headers only (no capture)"
                )

    _fast = _FAST if (not preload_active and fast_available) else None  # type: ignore[assignment]
    if domains_to_not_propagate_headers_to is None:
        domains_to_not_propagate_headers_to = []

    if SF_DEBUG:
        mode = "headers only" if preload_active else "full capture"
        try:
            print(
                f"[http_client] Patching http.client ({mode})",
                log=False,
            )
        except TypeError:
            print(f"[http_client] Patching http.client ({mode})")

    try:
        import http.client as _hc
    except ImportError:
        if SF_DEBUG:
            try:
                print("[http_client] http.client not available to patch", log=False)
            except TypeError:
                print("[http_client] http.client not available to patch")
        return

    # Body size limits (only needed if NOT using preload)
    if not preload_active:
        try:
            SFF_MAX_REQ_BODY = getattr(_fast, "SFF_MAX_REQ_BODY", 8192)
            SFF_MAX_RESP_BODY = getattr(_fast, "SFF_MAX_RESP_BODY", 8192)
        except Exception:
            SFF_MAX_REQ_BODY = 8192
            SFF_MAX_RESP_BODY = 8192
    else:
        SFF_MAX_REQ_BODY = 0
        SFF_MAX_RESP_BODY = 0

    original_request = _hc.HTTPConnection.request
    original_send = _hc.HTTPConnection.send
    original_getresponse = _hc.HTTPConnection.getresponse

    def patched_request(
        self, method, url, body=None, headers=None, *, encode_chunked=False
    ):
        # Build full URL for domain checking (http.client uses relative paths)
        full_url = url
        if not url.startswith(("http://", "https://")):
            # Relative path - build full URL from connection
            scheme = "https" if isinstance(self, _hc.HTTPSConnection) else "http"
            full_url = (
                f"{scheme}://{self.host}:{self.port}{url}"
                if self.port not in (80, 443)
                else f"{scheme}://{self.host}{url}"
            )

        # ULTRA-FAST header injection using inject_headers_ultrafast() (~100ns)
        # Create dict for injection, then check if we actually added anything
        hdrs_dict = dict(headers) if headers else {}
        original_keys = set(hdrs_dict.keys())
        inject_headers_ultrafast(
            hdrs_dict, full_url, domains_to_not_propagate_headers_to
        )

        # Only use dict if we added headers OR original had headers (preserve None if nothing to add)
        if headers or set(hdrs_dict.keys()) != original_keys:
            hdrs_out = hdrs_dict
        else:
            hdrs_out = None  # Preserve None if no headers were originally provided and none were injected

        # Only capture state if NOT using LD_PRELOAD (preload captures at socket layer)
        if not preload_active:
            # Get trace_id for capture (already injected in headers)
            trace_id = trace_id_ctx.get(None) or ""

            start_ts = int(time.time() * 1_000)
            # Store state as list [start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, seen_end]
            # Lists are mutable so patched_send can append to buffers
            self._sf_req_capture = [
                start_ts,
                trace_id,
                url,
                method,
                bytearray(),
                bytearray(),
                False,
            ]

        return original_request(
            self,
            method,
            url,
            body=body,
            headers=hdrs_out,
            encode_chunked=encode_chunked,
        )

    def patched_send(self, data):
        state = getattr(self, "_sf_req_capture", None)
        if state is not None:
            # FAST: Capture headers and body without parsing
            # state = [start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, seen_end]
            hdr_buf, body_buf, seen_end = state[4], state[5], state[6]

            if not seen_end:
                # Look for \r\n\r\n to split headers from body
                pos = data.find(b"\r\n\r\n")
                if pos >= 0:
                    hdr_buf.extend(data[: pos + 4])
                    if len(data) > pos + 4:
                        cap = SFF_MAX_REQ_BODY - len(body_buf)
                        if cap > 0:
                            body_buf.extend(data[pos + 4 : pos + 4 + cap])
                    state[6] = True  # Mark seen_end
                else:
                    hdr_buf.extend(data)
            else:
                # Already saw headers, just capture body
                cap = SFF_MAX_REQ_BODY - len(body_buf)
                if cap > 0:
                    body_buf.extend(data[:cap])

        return original_send(self, data)

    def patched_getresponse(self):
        response = original_getresponse(self)

        state = getattr(self, "_sf_req_capture", None)
        if not state:
            return response

        # Check if network recording is suppressed (e.g., by @skip_network_tracing decorator)
        if is_network_recording_suppressed():
            delattr(self, "_sf_req_capture")
            return response

        # ULTRA-FAST: Extract captured data, call C extension, return immediately
        try:
            # state = [start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, seen_end]
            start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, _ = state
            delattr(self, "_sf_req_capture")

            status = int(getattr(response, "status", 0))
            ok = 1 if status < 400 else 0
            end_ts = int(time.time() * 1_000)

            # FAST: Parse request headers from buffer
            req_headers_json = "{}"
            hdr_dict = {}
            if req_hdr_buf:
                try:
                    hdr_dict = _parse_request_headers_from_block(bytes(req_hdr_buf))
                except Exception:
                    pass

                if HAS_ORJSON:
                    req_headers_json = orjson.dumps(hdr_dict).decode("utf-8")
                else:
                    req_headers_json = json.dumps(hdr_dict).decode("utf-8")

            # FAST: Get response headers
            resp_headers_json = "{}"
            if HAS_ORJSON:
                resp_headers_json = orjson.dumps(
                    {str(k): str(v) for k, v in response.getheaders()}
                ).decode("utf-8")
            else:
                resp_headers_json = json.dumps(
                    {str(k): str(v) for k, v in response.getheaders()}
                ).decode("utf-8")

            # FAST: Peek response body (non-blocking)
            resp_body = b""
            try:
                if (
                    SFF_MAX_RESP_BODY > 0
                    and hasattr(response, "fp")
                    and hasattr(response.fp, "peek")
                ):
                    resp_body = bytes(
                        response.fp.peek(SFF_MAX_RESP_BODY)[:SFF_MAX_RESP_BODY]
                    )
            except Exception:
                pass

            # Call C extension (releases GIL internally for JSON building)
            _fast.networkhop_async(
                trace_id=trace_id,
                url=url,
                method=method,
                status=status,
                ok=ok,
                timestamp_start=start_ts,
                timestamp_end=end_ts,
                request_body=bytes(req_body_buf) if req_body_buf else b"",
                response_body=resp_body,
                request_headers_json=req_headers_json,
                response_headers_json=resp_headers_json,
            )
        except Exception:
            pass

        return response

    # ALWAYS patch request() for header injection (even with LD_PRELOAD or no C extension)
    if HAS_WRAPT:

        def instrumented_request(wrapped, instance, args, kwargs):
            """Ultra-fast header injection using wrapt."""
            method = args[0] if len(args) > 0 else kwargs.get("method", "GET")
            url = args[1] if len(args) > 1 else kwargs.get("url", "")
            body = args[2] if len(args) > 2 else kwargs.get("body", None)
            headers = args[3] if len(args) > 3 else kwargs.get("headers", None)
            encode_chunked = kwargs.get("encode_chunked", False)
            return patched_request(
                instance, method, url, body, headers, encode_chunked=encode_chunked
            )

        wrapt.wrap_function_wrapper(_hc.HTTPConnection, "request", instrumented_request)
    else:
        _hc.HTTPConnection.request = patched_request

    # ONLY patch send/getresponse if NOT using LD_PRELOAD AND C extension is available (for capture/emission)
    if not preload_active and fast_available:
        if HAS_WRAPT:

            def instrumented_send(wrapped, instance, args, kwargs):
                """Ultra-fast send wrapper using wrapt."""
                data = args[0] if len(args) > 0 else kwargs.get("data", b"")
                return patched_send(instance, data)

            def instrumented_getresponse(wrapped, instance, args, kwargs):
                """Ultra-fast getresponse wrapper using wrapt."""
                return patched_getresponse(instance)

            wrapt.wrap_function_wrapper(_hc.HTTPConnection, "send", instrumented_send)
            wrapt.wrap_function_wrapper(
                _hc.HTTPConnection, "getresponse", instrumented_getresponse
            )
        else:
            _hc.HTTPConnection.send = patched_send
            _hc.HTTPConnection.getresponse = patched_getresponse

        if SF_DEBUG:
            try:
                print("[http_client] Patched send/getresponse for capture", log=False)
            except TypeError:
                print("[http_client] Patched send/getresponse for capture")
    else:
        reason = (
            "LD_PRELOAD handles capture"
            if preload_active
            else "C extension not available"
        )
        if SF_DEBUG:
            try:
                print(
                    f"[http_client] Skipped send/getresponse patches ({reason})",
                    log=False,
                )
            except TypeError:
                print(f"[http_client] Skipped send/getresponse patches ({reason})")
