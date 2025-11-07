import os
import time
from typing import List, Optional

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

from ...constants import SAILFISH_TRACING_HEADER
from ...thread_local import trace_id_ctx
from .utils import (
    init_fast_header_check,
    inject_headers_ultrafast,
    record_network_request,
)

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active (same logic as http_client.py)."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def patch_httpcore(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Monkey-patch httpcore.ConnectionPool and AsyncConnectionPool
    to inject SAILFISH_TRACING_HEADER + FUNCSPAN_OVERRIDE_HEADER (when allowed)
    and to record every outbound request.

    When LD_PRELOAD is active: ULTRA-FAST path with <10ns overhead (header injection only).
    When LD_PRELOAD is NOT active: Full capture path with body/header recording.
    """
    try:
        import httpcore
    except ImportError:
        return  # HTTP Core not present—skip patch

    # Keep original methods
    orig_sync_req = httpcore.ConnectionPool.request
    orig_sync_stream = httpcore.ConnectionPool.stream
    orig_async_req = httpcore.AsyncConnectionPool.request
    orig_async_stream = httpcore.AsyncConnectionPool.stream

    # Normalize exclude list
    exclude = domains_to_not_propagate_headers_to or []

    # Check if LD_PRELOAD is active
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(exclude)

    # Unified _prepare_headers function for both fast and slow paths
    def _prepare_headers(url, existing_headers):
        """
        Returns (new_headers, trace_id, funcspan_override).
        Uses inject_headers_ultrafast() for ultra-fast header injection (~100ns).

        OPTIMIZED: Works with tuples directly, avoids dict conversion roundtrip.
        """
        # CRITICAL: Early exit if header already exists (prevents double injection when httpx->httpcore)
        trace_header_bytes = SAILFISH_TRACING_HEADER.encode()
        if existing_headers:
            for name, _ in existing_headers:
                if name.lower() == trace_header_bytes.lower():
                    # Header already injected by httpx - just return as-is
                    return list(existing_headers), "", None

        # OPTIMIZED: Use inject_headers_ultrafast with temporary dict, then append as tuples
        # This avoids the expensive dict→tuple→dict→tuple conversion cycle
        headers_dict = {}
        inject_headers_ultrafast(headers_dict, str(url), exclude)

        # OPTIMIZED: Build new header list (existing + new) in single pass
        hdrs = list(existing_headers) if existing_headers else []
        for key, value in headers_dict.items():
            key_bytes = key.encode("utf-8") if isinstance(key, str) else key
            value_bytes = value.encode("utf-8") if isinstance(value, str) else value
            hdrs.append((key_bytes, value_bytes))

        # Get trace_id for capture (only needed in slow path)
        trace_id = trace_id_ctx.get(None) or "" if not preload_active else ""

        return hdrs, trace_id, None

    # 1. Sync .request(...)
    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:

            def instrumented_sync_request(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using C extension via wrapt."""
                # args = (method, url, ...), kwargs = {...}
                url = args[1] if len(args) > 1 else kwargs.get("url", "")
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "httpcore", "ConnectionPool.request", instrumented_sync_request
            )
        else:

            def _patched_sync_request(self, method, url, **kwargs):
                # prepare headers & trace (ultra-fast C extension)
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers

                # Immediately call original and return - NO timing, NO capture!
                return orig_sync_req(self, method, url, **kwargs)

            httpcore.ConnectionPool.request = _patched_sync_request
    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        def _patched_sync_request(self, method, url, **kwargs):
            ts0 = int(time.time() * 1_000)
            # prepare headers & trace
            headers, trace_id, funcspan_override = _prepare_headers(
                url, kwargs.get("headers")
            )
            kwargs["headers"] = headers

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                if "content" in kwargs:
                    content = kwargs["content"]
                    if isinstance(content, bytes):
                        req_data = content
                    elif isinstance(content, str):
                        req_data = content.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps([list(h) for h in headers])
                else:
                    req_headers = json.dumps([list(h) for h in headers]).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            error = None
            resp_data = b""
            resp_headers = b""
            try:
                resp = orig_sync_req(self, method, url, **kwargs)
                success = True
                status = getattr(resp, "status_code", 0)

                # Capture response data and headers
                try:
                    resp_data = getattr(resp, "content", b"")
                    if HAS_ORJSON:
                        resp_headers = orjson.dumps([list(h) for h in resp.headers])
                    else:
                        resp_headers = json.dumps(
                            [list(h) for h in resp.headers]
                        ).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                return resp
            except Exception as e:
                success = False
                status = 0
                error = str(e)[:255]
                raise
            finally:
                ts1 = int(time.time() * 1_000)
                record_network_request(
                    trace_id,
                    str(url),
                    method,
                    status,
                    success,
                    error,
                    ts0,
                    ts1,
                    request_data=req_data,
                    response_data=resp_data,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

    # 2. Sync .stream(...)
    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:

            def instrumented_sync_stream(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using C extension via wrapt."""
                url = args[1] if len(args) > 1 else kwargs.get("url", "")
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "httpcore", "ConnectionPool.stream", instrumented_sync_stream
            )
        else:

            def _patched_sync_stream(self, method, url, **kwargs):
                # prepare headers & trace (ultra-fast C extension)
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers

                # Immediately call original and return - NO timing, NO capture!
                return orig_sync_stream(self, method, url, **kwargs)

            httpcore.ConnectionPool.stream = _patched_sync_stream
    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        def _patched_sync_stream(self, method, url, **kwargs):
            ts0 = int(time.time() * 1_000)
            headers, trace_id, funcspan_override = _prepare_headers(
                url, kwargs.get("headers")
            )
            kwargs["headers"] = headers

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                if "content" in kwargs:
                    content = kwargs["content"]
                    if isinstance(content, bytes):
                        req_data = content
                    elif isinstance(content, str):
                        req_data = content.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps([list(h) for h in headers])
                else:
                    req_headers = json.dumps([list(h) for h in headers]).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            error = None
            resp_headers = b""
            try:
                stream = orig_sync_stream(self, method, url, **kwargs)
                success = True
                # stream itself yields the body; status often on returned object
                status = 0

                # Capture response headers if available
                try:
                    if HAS_ORJSON:
                        resp_headers = orjson.dumps([list(h) for h in stream.headers])
                    else:
                        resp_headers = json.dumps(
                            [list(h) for h in stream.headers]
                        ).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                return stream
            except Exception as e:
                success = False
                status = 0
                error = str(e)[:255]
                raise
            finally:
                ts1 = int(time.time() * 1_000)
                record_network_request(
                    trace_id,
                    str(url),
                    method,
                    status,
                    success,
                    error,
                    ts0,
                    ts1,
                    request_data=req_data,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

    # 3. Async .request(...)
    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:

            async def instrumented_async_request(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using C extension via wrapt."""
                url = args[1] if len(args) > 1 else kwargs.get("url", "")
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers
                return await wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "httpcore", "AsyncConnectionPool.request", instrumented_async_request
            )
        else:

            async def _patched_async_request(self, method, url, **kwargs):
                # prepare headers & trace (ultra-fast C extension)
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers

                # Immediately call original and return - NO timing, NO capture!
                return await orig_async_req(self, method, url, **kwargs)

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        async def _patched_async_request(self, method, url, **kwargs):
            ts0 = int(time.time() * 1_000)
            headers, trace_id, funcspan_override = _prepare_headers(
                url, kwargs.get("headers")
            )
            kwargs["headers"] = headers

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                if "content" in kwargs:
                    content = kwargs["content"]
                    if isinstance(content, bytes):
                        req_data = content
                    elif isinstance(content, str):
                        req_data = content.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps([list(h) for h in headers])
                else:
                    req_headers = json.dumps([list(h) for h in headers]).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            error = None
            resp_data = b""
            resp_headers = b""
            try:
                resp = await orig_async_req(self, method, url, **kwargs)
                success = True
                status = getattr(resp, "status_code", 0)

                # Capture response data and headers
                try:
                    resp_data = getattr(resp, "content", b"")
                    if HAS_ORJSON:
                        resp_headers = orjson.dumps([list(h) for h in resp.headers])
                    else:
                        resp_headers = json.dumps(
                            [list(h) for h in resp.headers]
                        ).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                return resp
            except Exception as e:
                success = False
                status = 0
                error = str(e)[:255]
                raise
            finally:
                ts1 = int(time.time() * 1_000)
                record_network_request(
                    trace_id,
                    str(url),
                    method,
                    status,
                    success,
                    error,
                    ts0,
                    ts1,
                    request_data=req_data,
                    response_data=resp_data,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

    # 4. Async .stream(...)
    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:

            def instrumented_async_stream(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using C extension via wrapt."""
                url = args[1] if len(args) > 1 else kwargs.get("url", "")
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "httpcore", "AsyncConnectionPool.stream", instrumented_async_stream
            )
        else:

            def _patched_async_stream(self, method, url, **kwargs):
                # prepare headers & trace (ultra-fast C extension)
                headers, trace_id, funcspan_override = _prepare_headers(
                    url, kwargs.get("headers")
                )
                kwargs["headers"] = headers

                # Immediately call original and return - NO timing, NO capture!
                return orig_async_stream(self, method, url, **kwargs)

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        async def _patched_async_stream(self, method, url, **kwargs):
            ts0 = int(time.time() * 1_000)
            headers, trace_id, funcspan_override = _prepare_headers(
                url, kwargs.get("headers")
            )
            kwargs["headers"] = headers

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                if "content" in kwargs:
                    content = kwargs["content"]
                    if isinstance(content, bytes):
                        req_data = content
                    elif isinstance(content, str):
                        req_data = content.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps([list(h) for h in headers])
                else:
                    req_headers = json.dumps([list(h) for h in headers]).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            original_cm = orig_async_stream(self, method, url, **kwargs)

            class _StreamCM:
                def __init__(self, cm, req_d, req_h):
                    self._cm = cm
                    self._status = 0
                    self._req_data = req_d
                    self._req_headers = req_h
                    self._resp_headers = b""

                async def __aenter__(self):
                    response = await self._cm.__aenter__()  # now a single Response
                    # capture status (httpcore.Response.status or status_code)
                    self._status = getattr(
                        response, "status_code", getattr(response, "status", 0)
                    )

                    # Capture response headers
                    if HAS_ORJSON:
                        self._resp_headers = orjson.dumps(
                            [list(h) for h in response.headers]
                        )
                    else:
                        self._resp_headers = json.dumps(
                            [list(h) for h in response.headers]
                        ).encode("utf-8")

                    return response

                async def __aexit__(self, exc_type, exc, tb):
                    success = exc_type is None
                    ts1 = int(time.time() * 1_000)
                    record_network_request(
                        trace_id,
                        str(url),
                        method,
                        self._status,
                        success,
                        None if success else str(exc)[:255],
                        ts0,
                        ts1,
                        request_data=self._req_data,
                        request_headers=self._req_headers,
                        response_headers=self._resp_headers,
                    )
                    return await self._cm.__aexit__(exc_type, exc, tb)

            return _StreamCM(original_cm, req_data, req_headers)

    # Apply patches (only if NOT using wrapt - wrapt already applied them)
    if not (HAS_WRAPT and preload_active):
        httpcore.ConnectionPool.request = _patched_sync_request
        httpcore.ConnectionPool.stream = _patched_sync_stream
        httpcore.AsyncConnectionPool.request = _patched_async_request
        httpcore.AsyncConnectionPool.stream = _patched_async_stream
