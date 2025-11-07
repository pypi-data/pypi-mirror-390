# request_utils.py
import logging
import os
import threading
import time
from typing import Any, Callable, List, Optional, Tuple

import orjson

from .env_vars import SF_DEBUG
from .server_status import server_running
from .shutdown_flag import is_shutting_down
from .thread_local import _thread_locals, suppress_logs, suppress_network_recording

# ==========================================================
# Tunables
# ==========================================================
BATCH_MAX = int(os.getenv("SF_NBPOST_BATCH_MAX", "512"))
BATCH_FLUSH_MS = float(os.getenv("SF_NBPOST_FLUSH_MS", "2"))
CONNECT_TIMEOUT_S = float(os.getenv("SF_NBPOST_CONNECT_TIMEOUT", "0.1"))
READ_TIMEOUT_S = float(os.getenv("SF_NBPOST_READ_TIMEOUT", "0.3"))
TOTAL_TIMEOUT_S = float(os.getenv("SF_NBPOST_TOTAL_TIMEOUT", "0.7"))

# Check if h2 is available for HTTP/2 support
_HAS_H2 = False
try:
    import h2  # noqa: F401
    _HAS_H2 = True
except ImportError:
    pass

# Only enable HTTP/2 if h2 is installed AND env var is set
HTTP2_ENABLED = os.getenv("SF_NBPOST_HTTP2", "0") == "1" and _HAS_H2
DISABLE_BATCHING = os.getenv("SF_NBPOST_DISABLE_BATCHING", "1") == "1"
# Keep gzip OFF by default per perf tests
GZIP_ENABLED = os.getenv("SF_NBPOST_GZIP", "0") == "1"


# ==========================================================
# Minimal public helpers
# ==========================================================
def get_header(request, header_name):
    return request.headers.get(header_name)


def set_header(request, header_name, header_value):
    request.headers[header_name] = header_value


def is_server_running(url="http://localhost:8000/healthz"):
    """
    Lightweight liveness probe using stdlib to avoid async spin in caller thread.
    """
    global server_running
    if server_running:
        return True
    try:
        import urllib.request

        with suppress_network_recording(), suppress_logs():
            with urllib.request.urlopen(url, timeout=0.5) as r:  # nosec
                if getattr(r, "status", 0) == 200:
                    server_running = True
                    return True
    except Exception:
        pass
    return False


# ==========================================================
# Queue & worker
# ==========================================================
try:
    from queue import SimpleQueue  # C fast path
except Exception:  # pragma: no cover
    from queue import Queue as SimpleQueue  # fallback

# item variants:
#   ("POST", url, op, query, variables, wants_response, future)
#   ("DEFER", builder_callable)  # builder returns (url, op, query, variables)
_Item = Tuple[Any, ...]

_q: "SimpleQueue[_Item]" = SimpleQueue()
_started = False
_start_lock = threading.Lock()

# Worker backends
_HAS_PYCURL = False
try:
    import pycurl  # type: ignore

    _HAS_PYCURL = True
except Exception:
    _HAS_PYCURL = False

# httpx client (fallback path)
_client = None  # type: ignore[assignment]


def _ensure_started():
    global _started
    if _started:
        return
    with _start_lock:
        if _started:
            return
        t = threading.Thread(target=_bg_thread, name="nbpost-batcher", daemon=True)
        t.start()
        _started = True
        if SF_DEBUG:
            http2_status = HTTP2_ENABLED
            if not _HAS_H2 and os.getenv("SF_NBPOST_HTTP2", "0") == "1":
                http2_status = "disabled (h2 not installed)"
            print(
                f"[nbpost] started batcher (HTTP/2={http2_status}, batching={'off' if DISABLE_BATCHING else 'on'}, backend={'pycurl' if _HAS_PYCURL else 'httpx'})",
                log=False,
            )


def _bg_thread():
    """
    Background thread: pycurl multi (preferred, C fast path). Falls back to httpx.
    """
    if _HAS_PYCURL:
        _run_worker_pycurl()
    else:
        # optional uvloop for httpx path
        try:
            import uvloop  # type: ignore

            uvloop.install()
        except Exception:
            pass
        import asyncio

        asyncio.run(_run_worker_httpx())


# ==========================================================
# pycurl backend (C, HTTP/2 via libcurl/nghttp2)
# ==========================================================
def _run_worker_pycurl():
    import pycurl  # type: ignore

    # CRITICAL: Set suppress flag for the ENTIRE thread since this thread is dedicated to sending telemetry
    # This prevents the C preload library from capturing our telemetry requests
    from .thread_local import suppress_network_recording_ctx
    suppress_network_recording_ctx.set(True)
    if SF_DEBUG:
        print(f"[pycurl worker] Set suppress_network_recording_ctx to True, current value: {suppress_network_recording_ctx.get()}", log=False)

    m = pycurl.CurlMulti()
    m.setopt(pycurl.M_MAX_HOST_CONNECTIONS, 1024)
    m.setopt(pycurl.M_MAXCONNECTS, 1024)

    # CRITICAL: Add marker header so C preload library can identify and skip telemetry requests
    base_headers = [
        "Content-Type: application/json",
        "X-Sf3-TelemetryOutbound: True"
    ]
    in_flight = {}

    last_flush = time.monotonic()
    batch: List[dict] = []
    url_for_batch: Optional[str] = None

    def _add_easy(url: str, body: bytes, future):
        c = pycurl.Curl()
        c.setopt(pycurl.CONNECTTIMEOUT_MS, int(CONNECT_TIMEOUT_S * 1000))
        c.setopt(pycurl.TIMEOUT_MS, int(TOTAL_TIMEOUT_S * 1000))
        if HTTP2_ENABLED:
            c.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2TLS)
        c.setopt(pycurl.URL, url.encode("utf-8"))
        c.setopt(pycurl.NOPROGRESS, True)
        c.setopt(pycurl.NOSIGNAL, 1)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, body)
        c.setopt(pycurl.POSTFIELDSIZE, len(body))
        c.setopt(pycurl.WRITEFUNCTION, lambda _b: len(_b))
        c.setopt(pycurl.HEADERFUNCTION, lambda _b: len(_b))

        headers = list(base_headers)
        if GZIP_ENABLED:
            headers.append("Content-Encoding: gzip")
        c.setopt(pycurl.HTTPHEADER, headers)

        m.add_handle(c)
        if future is not None:
            in_flight[c] = future

    def _flush_batch(url: Optional[str], batch_payload: List[dict]):
        if not batch_payload or not url:
            return
        body = orjson.dumps(batch_payload)
        if GZIP_ENABLED:
            import gzip

            body = gzip.compress(body)
        # Note: suppress_network_recording_ctx is already set for the entire thread
        with suppress_logs():
            _add_easy(url, body, future=None)

    def _send_one(url: str, op: str, query: str, variables: dict, future):
        payload = {"query": query, "variables": variables, "operationName": op}
        body = orjson.dumps(payload)
        if GZIP_ENABLED:
            import gzip

            body = gzip.compress(body)
        # Note: suppress_network_recording_ctx is already set for the entire thread
        with suppress_logs():
            _add_easy(url, body, future=future)

    while True:
        now = time.monotonic()
        elapsed_ms = (now - last_flush) * 1000.0
        should_flush = len(batch) >= BATCH_MAX or (
            batch and elapsed_ms >= BATCH_FLUSH_MS
        )

        drained = 0
        try:
            item = _q.get(timeout=max(0.0005, BATCH_FLUSH_MS / 1000.0))
            drained += 1

            tag = item[0]
            if tag == "DEFER":
                # Build tuple on the worker; keeps request thread extremely light
                builder: Callable[[], Tuple[str, str, str, dict]] = item[1]
                url, op, query, variables = builder()
                if DISABLE_BATCHING:
                    _send_one(url, op, query, variables, None)
                else:
                    if url_for_batch is None:
                        url_for_batch = url
                    elif url != url_for_batch:
                        _flush_batch(url_for_batch, batch)
                        last_flush = time.monotonic()
                        batch.clear()
                        url_for_batch = url
                    batch.append(
                        {"query": query, "variables": variables, "operationName": op}
                    )
            else:
                # ("POST", url, op, query, variables, wants_response, future)
                _, url, op, query, variables, wants_response, fut = item
                if getattr(_thread_locals, "reentrancy_guard_logging_preactive", False):
                    variables["reentrancyGuardPreactive"] = True
                if wants_response and fut is not None:
                    _send_one(url, op, query, variables, fut)
                else:
                    if DISABLE_BATCHING:
                        _send_one(url, op, query, variables, None)
                    else:
                        if url_for_batch is None:
                            url_for_batch = url
                        elif url != url_for_batch:
                            _flush_batch(url_for_batch, batch)
                            last_flush = time.monotonic()
                            batch.clear()
                            url_for_batch = url
                        batch.append(
                            {
                                "query": query,
                                "variables": variables,
                                "operationName": op,
                            }
                        )
        except Exception:
            pass

        if should_flush and not DISABLE_BATCHING:
            _flush_batch(url_for_batch, batch)
            last_flush = time.monotonic()
            batch.clear()
            url_for_batch = None

        # Pump the multi interface
        import pycurl as _pc  # local alias for speed

        while True:
            stat, _ = m.perform()
            if stat != _pc.E_CALL_MULTI_PERFORM:
                break

        # Completed transfers
        while True:
            num_q, ok_list, err_list = m.info_read()
            for c in ok_list:
                fut = in_flight.pop(c, None)
                if fut is not None:
                    try:
                        code = c.getinfo(_pc.RESPONSE_CODE)
                        fut.set_result(code == 200)
                    except Exception as e:
                        fut.set_exception(e)
                m.remove_handle(c)
                c.close()

            for c, errno, errmsg in err_list:
                fut = in_flight.pop(c, None)
                if fut is not None:
                    try:
                        fut.set_result(False)
                    except Exception:
                        pass
                if SF_DEBUG:
                    print(f"[nbpost] pycurl error {errno}: {errmsg}", log=False)
                m.remove_handle(c)
                c.close()

            if num_q == 0:
                break

        if drained == 0 and not batch:
            try:
                m.select(0.01)  # wait for activity (max 10ms)
            except Exception:
                pass


# ==========================================================
# httpx backend (fallback)
# ==========================================================
async def _run_worker_httpx():
    global _client
    import asyncio

    import httpx

    # CRITICAL: Set suppress flag for the ENTIRE thread since this thread is dedicated to sending telemetry
    # This prevents the C preload library from capturing our telemetry requests
    from .thread_local import suppress_network_recording_ctx
    suppress_network_recording_ctx.set(True)
    if SF_DEBUG:
        print(f"[httpx worker] Set suppress_network_recording_ctx to True, current value: {suppress_network_recording_ctx.get()}", log=False)

    limits = httpx.Limits(
        max_connections=1024,
        max_keepalive_connections=1024,
        keepalive_expiry=30.0,
    )
    timeout = httpx.Timeout(
        connect=CONNECT_TIMEOUT_S,
        read=READ_TIMEOUT_S,
        write=READ_TIMEOUT_S,
        pool=TOTAL_TIMEOUT_S,
    )
    # CRITICAL: Add marker header so C preload library can identify and skip telemetry requests
    _client = httpx.AsyncClient(
        http2=HTTP2_ENABLED,
        limits=limits,
        timeout=timeout,
        headers={
            "Content-Type": "application/json",
            "X-Sf3-TelemetryOutbound": "True"
        },
    )

    try:
        last_flush = time.monotonic()
        batch: List[dict] = []
        url_for_batch: Optional[str] = None

        while True:
            now = time.monotonic()
            elapsed_ms = (now - last_flush) * 1000.0
            should_flush = len(batch) >= BATCH_MAX or (
                batch and elapsed_ms >= BATCH_FLUSH_MS
            )

            drained = 0
            try:
                item = _q.get(timeout=max(0.0005, BATCH_FLUSH_MS / 1000.0))
                drained += 1

                tag = item[0]
                if tag == "DEFER":
                    builder: Callable[[], Tuple[str, str, str, dict]] = item[1]
                    url, op, query, variables = builder()
                    if DISABLE_BATCHING:
                        await _send_one_httpx(_client, url, op, query, variables, None)
                    else:
                        if url_for_batch is None:
                            url_for_batch = url
                        elif url != url_for_batch:
                            await _flush_batch_httpx(_client, url_for_batch, batch)
                            last_flush = time.monotonic()
                            batch.clear()
                            url_for_batch = url
                        batch.append(
                            {
                                "query": query,
                                "variables": variables,
                                "operationName": op,
                            }
                        )
                else:
                    _, url, op, query, variables, wants_response, fut = item
                    if getattr(
                        _thread_locals, "reentrancy_guard_logging_preactive", False
                    ):
                        variables["reentrancyGuardPreactive"] = True
                    if wants_response and fut is not None:
                        await _send_one_httpx(_client, url, op, query, variables, fut)
                    else:
                        if DISABLE_BATCHING:
                            await _send_one_httpx(
                                _client, url, op, query, variables, None
                            )
                        else:
                            if url_for_batch is None:
                                url_for_batch = url
                            elif url != url_for_batch:
                                await _flush_batch_httpx(_client, url_for_batch, batch)
                                last_flush = time.monotonic()
                                batch.clear()
                                url_for_batch = url
                            batch.append(
                                {
                                    "query": query,
                                    "variables": variables,
                                    "operationName": op,
                                }
                            )
            except Exception:
                pass

            if should_flush and not DISABLE_BATCHING:
                if batch:
                    await _flush_batch_httpx(_client, url_for_batch, batch)
                    last_flush = time.monotonic()
                    batch.clear()
                    url_for_batch = None

            if drained == 0 and not batch:
                await asyncio.sleep(0)
    finally:
        try:
            await _client.aclose()
        except Exception:
            pass
        _client = None


async def _flush_batch_httpx(client, url: Optional[str], batch: List[dict]):
    if not batch or not url:
        return
    import httpx

    body = orjson.dumps(batch)
    headers = {}
    if GZIP_ENABLED:
        import gzip

        body = gzip.compress(body)
        headers["Content-Encoding"] = "gzip"
    try:
        # Note: suppress_network_recording_ctx is already set for the entire thread
        with suppress_logs():
            r: httpx.Response = await client.post(url, content=body, headers=headers)
        try:
            await r.aclose()
        except Exception:
            pass
        if SF_DEBUG:
            print(f"[nbpost] batch -> {r.status_code}, items={len(batch)}", log=False)
    except Exception as e:
        if SF_DEBUG:
            print(f"[nbpost] batch POST failed: {e}", log=False)


async def _send_one_httpx(
    client, url: str, op: str, query: str, variables: dict, future=None
):
    import httpx

    payload = {"query": query, "variables": variables, "operationName": op}
    body = orjson.dumps(payload)
    headers = {}
    if GZIP_ENABLED:
        import gzip

        body = gzip.compress(body)
        headers["Content-Encoding"] = "gzip"
    if SF_DEBUG:
        print(f"[nbpost] About to POST: op={op}, url={url}, sessionId={variables.get('sessionId', 'N/A')[:50]}", log=False)
    try:
        # Note: suppress_network_recording_ctx is already set for the entire thread
        with suppress_logs():
            r: httpx.Response = await client.post(url, content=body, headers=headers)
        status = r.status_code
        if SF_DEBUG:
            print(f"[nbpost] POST response: op={op}, status={status}", log=False)
        try:
            await r.aclose()
        except Exception:
            pass
        if future is not None:
            future.set_result(status == 200)
    except Exception as e:
        if future is not None:
            future.set_exception(e)
        if SF_DEBUG:
            print(f"[nbpost] POST failed: {op} {e}", log=False)


# ==========================================================
# Public API (hot path)
# ==========================================================
def non_blocking_post(url, operation_name, query, variables):
    """Enqueue and return immediately."""
    if is_shutting_down:
        return None
    _ensure_started()
    try:
        _q.put_nowait(("POST", url, operation_name, query, variables, False, None))
    except Exception:
        if SF_DEBUG:
            print("[nbpost] queue put failed", log=False)
    return None


def non_blocking_post_with_response(url, operation_name, query, variables):
    """Enqueue and return a Future-like that resolves to bool (success)."""
    if is_shutting_down:
        return None
    _ensure_started()
    from concurrent.futures import Future

    fut = Future()
    try:
        _q.put_nowait(("POST", url, operation_name, query, variables, True, fut))
    except Exception as e:
        fut.set_exception(e)
    return fut


def non_blocking_post_deferred(builder: Callable[[], Tuple[str, str, str, dict]]):
    """
    Enqueue a zero-alloc builder closure; the worker will call it to build
    (url, operation_name, query, variables) just-in-time before sending.

    This moves dict construction off the request thread entirely.
    """
    if is_shutting_down:
        return None
    _ensure_started()
    try:
        _q.put_nowait(("DEFER", builder))
    except Exception:
        if SF_DEBUG:
            print("[nbpost] queue put failed (deferred)", log=False)
    return None
