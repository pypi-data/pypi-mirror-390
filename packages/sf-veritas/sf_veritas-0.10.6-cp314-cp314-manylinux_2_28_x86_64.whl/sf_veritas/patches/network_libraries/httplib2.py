import os
import time
from typing import List, Optional

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

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


def patch_httplib2(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Monkey-patch httplib2.Http.request so that:
    1. We skip header injection for configured domains.
    2. We inject SAILFISH_TRACING_HEADER + FUNCSPAN_OVERRIDE_HEADER (fast: <20ns).
    3. We call NetworkRequestTransmitter().do_send via record_network_request() UNLESS LD_PRELOAD active.
    4. All HTTP methods (GET, POST, etc.) continue to work as before.

    When LD_PRELOAD is active: ULTRA-FAST path with <10ns overhead (header injection only).
    When LD_PRELOAD is NOT active: Full capture path with body/header recording.
    """
    try:
        import httplib2
    except ImportError:
        return

    skip = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(skip)

    # Store original for both fast and slow paths
    original_request = httplib2.Http.request

    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:
            # FASTEST: Use wrapt directly (OTEL-style for minimal overhead)
            def instrumented_request(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using inject_headers_ultrafast() via wrapt."""
                # args = (uri, method, ...), kwargs = {body, headers, ...}
                uri = args[0] if len(args) > 0 else kwargs.get("uri", "")

                # Ensure headers dict exists
                headers = kwargs.get("headers")
                if not headers:
                    headers = {}
                elif not isinstance(headers, dict):
                    headers = dict(headers)

                # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                inject_headers_ultrafast(headers, uri, skip)

                kwargs["headers"] = headers

                # Immediately call original and return - NO timing, NO capture!
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "httplib2", "Http.request", instrumented_request
            )
        else:
            # Fallback: Direct patching if wrapt not available
            def patched_request(
                self, uri, method="GET", body=None, headers=None, **kwargs
            ):
                # Ensure headers dict exists
                if not headers:
                    headers = {}
                elif not isinstance(headers, dict):
                    headers = dict(headers)

                # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                inject_headers_ultrafast(headers, uri, skip)

                # Immediately call original and return - NO timing, NO capture!
                return original_request(
                    self, uri, method, body=body, headers=headers, **kwargs
                )

            httplib2.Http.request = patched_request

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        def patched_request(self, uri, method="GET", body=None, headers=None, **kwargs):
            start_ts = int(time.time() * 1_000)

            # Ensure headers dict exists
            if not headers:
                headers = {}
            elif not isinstance(headers, dict):
                headers = dict(headers)

            # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
            inject_headers_ultrafast(headers, uri, skip)

            # Get trace_id for capture
            trace_id = trace_id_ctx.get(None) or ""

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                if body:
                    if isinstance(body, bytes):
                        req_data = body
                    elif isinstance(body, str):
                        req_data = body.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps({str(k): str(v) for k, v in headers.items()})
                else:
                    req_headers = json.dumps({str(k): str(v) for k, v in headers.items()}).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            try:
                # perform the actual HTTP call
                response, content = original_request(
                    self, uri, method, body=body, headers=headers, **kwargs
                )
                status_code = getattr(response, "status", None) or getattr(
                    response, "status_code", None
                )
                success = isinstance(status_code, int) and 200 <= status_code < 400

                # Capture response data and headers
                resp_data = b""
                resp_headers = b""

                # content is already the response body in httplib2
                resp_data = content if isinstance(content, bytes) else b""
                # Capture response headers
                if HAS_ORJSON:
                    resp_headers = orjson.dumps({str(k): str(v) for k, v in response.items()})
                else:
                    resp_headers = json.dumps({str(k): str(v) for k, v in response.items()}).encode("utf-8")

                # record success (only when LD_PRELOAD is NOT active)
                record_network_request(
                    trace_id,
                    uri,
                    method,
                    status_code,
                    success,
                    timestamp_start=start_ts,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    response_data=resp_data,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

                return response, content

            except Exception as e:
                # record failures (only when LD_PRELOAD is NOT active)
                record_network_request(
                    trace_id,
                    uri,
                    method,
                    0,
                    False,
                    error=str(e)[:255],
                    timestamp_start=start_ts,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    request_headers=req_headers,
                )
                raise

        # apply our patch (only if not using wrapt)
        if not (preload_active and HAS_WRAPT):
            httplib2.Http.request = patched_request
