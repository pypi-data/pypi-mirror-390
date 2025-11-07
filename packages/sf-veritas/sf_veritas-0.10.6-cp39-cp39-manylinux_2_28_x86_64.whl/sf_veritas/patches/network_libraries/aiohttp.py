import os
import time
from typing import Any, List, Optional

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

from ...constants import FUNCSPAN_OVERRIDE_HEADER, SAILFISH_TRACING_HEADER
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


def patch_aiohttp(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Monkey-patch aiohttp so that every HTTP verb:
        1) injects SAILFISH_TRACING_HEADER + FUNCSPAN_OVERRIDE_HEADER when allowed,
        2) measures timing (only when LD_PRELOAD not active),
        3) calls NetworkRequestTransmitter().do_send via record_network_request (UNLESS LD_PRELOAD active).

    When LD_PRELOAD is active: ULTRA-FAST path using TraceConfig with wrapt (OTEL-style, minimal overhead).
    When LD_PRELOAD is NOT active: Full capture path with body/header recording.
    """
    try:
        import aiohttp
    except:
        return

    skip = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(skip)

    if preload_active:
        # ========== ULTRA-FAST PATH: Direct wrapt on _request (bypass TraceConfig overhead!) ==========
        # TraceConfig adds 15-20% overhead, so we patch _request directly like OTEL does for other libraries

        if HAS_WRAPT:
            # FASTEST: Use wrapt directly on _request method (OTEL-style for minimal overhead)
            async def instrumented_request(wrapped, instance, args, kwargs):
                """
                Ultra-fast header injection using thread-local cache.
                Bypasses TraceConfig machinery for <5% overhead.
                """
                # Extract verb and URL from args
                verb_name = args[0] if args else kwargs.get("method", "GET")
                url = str(args[1] if len(args) > 1 else kwargs.get("url", ""))

                # Direct header mutation (no copy!)
                headers = kwargs.get("headers")
                if headers is None:
                    headers = {}
                    kwargs["headers"] = headers

                # CRITICAL: Skip if already injected (prevents double injection)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, url, skip)

                # NO timing, NO capture, NO threads - immediate return!
                return await wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                aiohttp.ClientSession, "_request", instrumented_request
            )

        else:
            # Fallback: Direct patching if wrapt not available
            orig_request = aiohttp.ClientSession._request

            async def patched_request(self, verb_name: str, url: Any, **kwargs):
                """Ultra-fast header injection without wrapt."""
                headers = kwargs.get("headers")
                if headers is None:
                    headers = {}
                    kwargs["headers"] = headers

                # CRITICAL: Skip if already injected (prevents double injection)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, str(url), skip)

                # NO timing, NO capture - immediate return!
                return await orig_request(self, verb_name, url, **kwargs)

            aiohttp.ClientSession._request = patched_request

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        # Uses wrapper function to capture request/response data
        orig_request = aiohttp.ClientSession._request

        async def patched_request(self, verb_name: str, url: Any, **kwargs):
            headers = kwargs.get("headers", {}) or {}
            if not isinstance(headers, dict):
                headers = dict(headers)

            # CRITICAL: Skip if already injected (prevents double injection)
            if SAILFISH_TRACING_HEADER not in headers:
                # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                inject_headers_ultrafast(headers, str(url), skip)

            kwargs["headers"] = headers

            # Get trace_id for network recording (after injection)
            trace_id = trace_id_ctx.get(None) or ""

            # SLOW PATH: LD_PRELOAD not active, do full Python-level capture
            # Capture request data as bytes - BEFORE request
            req_data = b""
            req_headers = b""
            try:
                if "json" in kwargs:
                    if HAS_ORJSON:
                        req_data = orjson.dumps(kwargs["json"])
                    else:
                        req_data = json.dumps(kwargs["json"]).encode("utf-8")
                elif "data" in kwargs:
                    data = kwargs["data"]
                    if isinstance(data, bytes):
                        req_data = data
                    elif isinstance(data, str):
                        req_data = data.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    # Convert keys to str (aiohttp may use istr which orjson doesn't accept)
                    req_headers = orjson.dumps({str(k): str(v) for k, v in headers.items()})
                else:
                    req_headers = json.dumps({str(k): str(v) for k, v in headers.items()}).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            # 2) Perform & time the request
            start = int(time.time() * 1_000)
            response = await orig_request(self, verb_name, url, **kwargs)
            end = int(time.time() * 1_000)

            # 3) Capture response metadata immediately (before response can be closed)
            status = getattr(response, "status", 0)
            ok = status < 400

            # Capture response headers immediately (cheap and safe)
            resp_headers = b""
            if HAS_ORJSON:
                # Convert keys to str (aiohttp uses istr which orjson doesn't accept)
                resp_headers = orjson.dumps({str(k): str(v) for k, v in response.headers.items()})
            else:
                resp_headers = json.dumps({str(k): str(v) for k, v in response.headers.items()}).encode("utf-8")

            # Send to C extension immediately - no background task needed!
            record_network_request(
                trace_id,
                str(url),
                verb_name.upper(),
                status,
                ok,
                None,
                timestamp_start=start,
                timestamp_end=end,
                request_data=req_data,
                response_data=b"",  # Skip body to avoid consuming stream
                request_headers=req_headers,
                response_headers=resp_headers,
            )

            # CRITICAL: Return response immediately!
            return response

        # Apply the wrapper to ClientSession._request
        aiohttp.ClientSession._request = patched_request

        # 2) Also patch the module-level aiohttp.request coroutine (for full-capture path)
        orig_module_request = getattr(aiohttp, "request", None)
        if orig_module_request:

            async def patched_module_request(verb_name: str, url: str, **kwargs):
                headers = kwargs.get("headers", {}) or {}
                if not isinstance(headers, dict):
                    headers = dict(headers)

                # CRITICAL: Skip if already injected (prevents double injection)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, str(url), skip)

                kwargs["headers"] = headers

                # Get trace_id for network recording (after injection)
                trace_id = trace_id_ctx.get(None) or ""

                # SLOW PATH: LD_PRELOAD not active, do full Python-level capture
                # Capture request data as bytes - BEFORE request
                req_data = b""
                req_headers = b""
                try:
                    if "json" in kwargs:
                        if HAS_ORJSON:
                            req_data = orjson.dumps(kwargs["json"])
                        else:
                            req_data = json.dumps(kwargs["json"]).encode("utf-8")
                    elif "data" in kwargs:
                        data = kwargs["data"]
                        if isinstance(data, bytes):
                            req_data = data
                        elif isinstance(data, str):
                            req_data = data.encode("utf-8")

                    # Capture request headers
                    if HAS_ORJSON:
                        # Convert keys to str (aiohttp may use istr which orjson doesn't accept)
                        req_headers = orjson.dumps({str(k): str(v) for k, v in headers.items()})
                    else:
                        req_headers = json.dumps({str(k): str(v) for k, v in headers.items()}).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                start = int(time.time() * 1_000)
                response = await orig_module_request(verb_name, url, **kwargs)
                end = int(time.time() * 1_000)

                status = getattr(
                    response, "status", getattr(response, "status_code", 0)
                )
                ok = status < 400

                # Capture response headers immediately (cheap and safe)
                resp_headers = b""
                if HAS_ORJSON:
                    resp_headers = orjson.dumps(dict(response.headers))
                else:
                    resp_headers = json.dumps(dict(response.headers)).encode("utf-8")

                # Send to C extension immediately - no background task needed!
                record_network_request(
                    trace_id,
                    str(url),
                    verb_name.upper(),
                    status,
                    ok,
                    None,
                    timestamp_start=start,
                    timestamp_end=end,
                    request_data=req_data,
                    response_data=b"",  # Skip body to avoid consuming stream
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

                # CRITICAL: Return response immediately!
                return response

            # Apply the wrapper to module-level request function
            aiohttp.request = patched_module_request
