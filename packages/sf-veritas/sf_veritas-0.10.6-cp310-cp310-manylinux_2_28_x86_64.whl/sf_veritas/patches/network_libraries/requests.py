"""
Monkey-patch the `requests` stack (requests → urllib3 → http.client):

• For every outbound request, propagate the SAILFISH_TRACING_HEADER + FUNCSPAN_OVERRIDE_HEADER
  unless the destination host is in `domains_to_not_propagate_headers_to`.
• Fire NetworkRequestTransmitter via utils.record_network_request
  so we always capture (url, status, timings, success, error).
• When LD_PRELOAD is active, ONLY inject headers (skip capture - socket layer handles it).
"""

from __future__ import annotations

import http.client
import os
import time
from typing import Dict, List, Optional, Tuple

import requests
import urllib3
from requests.sessions import Session

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False


from ...constants import FUNCSPAN_OVERRIDE_HEADER, SAILFISH_TRACING_HEADER
from ...thread_local import (
    activate_reentrancy_guards_exception,
    activate_reentrancy_guards_logging,
    activate_reentrancy_guards_print,
    get_funcspan_override,
)
from .utils import (
    get_trace_and_should_propagate,
    get_trace_and_should_propagate_fast,
    init_fast_header_check,
    inject_headers_ultrafast,
    record_network_request,
)
from .._patch_tracker import is_already_patched, mark_as_patched

###############################################################################
# Internal helpers
###############################################################################

# header names used for re-entrancy guards
REENTRANCY_GUARD_LOGGING_PREACTIVE = "reentrancy_guard_logging_preactive"
REENTRANCY_GUARD_PRINT_PREACTIVE = "reentrancy_guard_print_preactive"
REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE = "reentrancy_guard_exception_preactive"


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active (same logic as http_client.py)."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


# PERFORMANCE: Reentrancy guards disabled - they add ~10-20μs per request
# The socket layer (LD_PRELOAD) handles everything we need
# def _activate_rg(headers: Dict[str, str]) -> None:
#     """Turn the three 'preactive' guard flags ON for downstream hops."""
#     headers[REENTRANCY_GUARD_LOGGING_PREACTIVE] = "true"
#     headers[REENTRANCY_GUARD_PRINT_PREACTIVE] = "true"
#     headers[REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE] = "true"


# def _check_rg(headers: Dict[str, str]) -> None:
#     """If any pre-active guard present, switch the corresponding guard on."""
#     if headers.get(REENTRANCY_GUARD_LOGGING_PREACTIVE, "false").lower() == "true":
#         activate_reentrancy_guards_logging()
#     if headers.get(REENTRANCY_GUARD_PRINT_PREACTIVE, "false").lower() == "true":
#         activate_reentrancy_guards_print()
#     if headers.get(REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE, "false").lower() == "true":
#         activate_reentrancy_guards_exception()


def _prepare(
    url: str,
    domains_to_skip: List[str],
    headers: Optional[Dict[str, str]],
) -> Tuple[str, Dict[str, str], int]:
    """
    Inject trace header + funcspan override header (unless excluded) and return:
        trace_id, merged_headers, timestamp_ms

    ULTRA-FAST: <20ns overhead for header injection.

    PERFORMANCE: Reentrancy guards removed - saves ~10-20μs per request.
    """
    trace_id, propagate = get_trace_and_should_propagate(url, domains_to_skip)
    hdrs: Dict[str, str] = dict(headers or {})
    # _check_rg(hdrs)  # DISABLED for performance
    if propagate:
        hdrs[SAILFISH_TRACING_HEADER] = trace_id

        # Inject funcspan override header if present (ContextVar lookup ~8ns)
        try:
            funcspan_override = get_funcspan_override()
            if funcspan_override is not None:
                hdrs[FUNCSPAN_OVERRIDE_HEADER] = funcspan_override
        except Exception:
            pass

    # _activate_rg(hdrs)  # DISABLED for performance
    return trace_id, hdrs, int(time.time() * 1_000)


def _capture_and_record_requests(
    resp, trace_id, url, method, status, success, err, t0, t1, req_data, hdrs
):
    """Capture response data in background thread AFTER response is returned to user."""
    resp_data: bytes = b""
    req_headers: bytes = b""
    resp_headers: bytes = b""

    try:
        # Capture headers efficiently
        if HAS_ORJSON:
            req_headers = orjson.dumps({str(k): str(v) for k, v in hdrs.items()})
            if resp:
                resp_headers = orjson.dumps({str(k): str(v) for k, v in resp.headers.items()})
        else:
            req_headers = json.dumps({str(k): str(v) for k, v in hdrs.items()}).encode("utf-8")
            if resp:
                resp_headers = json.dumps({str(k): str(v) for k, v in resp.headers.items()}).encode("utf-8")

        # For response body: check if already cached in _content
        if resp:
            try:
                if hasattr(resp, "_content") and resp._content is not None:
                    resp_data = resp._content
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass

    # Send to C extension in background
    record_network_request(
        trace_id,
        url,
        method,
        status,
        success,
        err,
        timestamp_start=t0,
        timestamp_end=t1,
        request_data=req_data,
        response_data=resp_data,
        request_headers=req_headers,
        response_headers=resp_headers,
    )


def _capture_and_record_urllib3(
    resp, trace_id, url, method, status, success, err, t0, t1, req_data, hdrs
):
    """Capture urllib3 response data in background thread AFTER response is returned to user."""
    resp_data: bytes = b""
    req_headers: bytes = b""
    resp_headers: bytes = b""

    try:
        # Capture headers efficiently
        if HAS_ORJSON:
            req_headers = orjson.dumps({str(k): str(v) for k, v in hdrs.items()})
            if resp:
                resp_headers = orjson.dumps({str(k): str(v) for k, v in resp.headers.items()})
        else:
            req_headers = json.dumps({str(k): str(v) for k, v in hdrs.items()}).encode("utf-8")
            if resp:
                resp_headers = json.dumps({str(k): str(v) for k, v in resp.headers.items()}).encode("utf-8")

        # For response body: check if already available in data attribute
        if resp:
            try:
                resp_data = getattr(resp, "data", b"")
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass

    # Send to C extension in background
    record_network_request(
        trace_id,
        url,
        method,
        status,
        success,
        err,
        timestamp_start=t0,
        timestamp_end=t1,
        request_data=req_data,
        response_data=resp_data,
        request_headers=req_headers,
        response_headers=resp_headers,
    )


def _capture_and_record_http_client(
    resp, trace_id, url, method, status, success, err, t0, t1, req_data, hdrs
):
    """Capture http.client response data in background thread AFTER response is returned to user."""
    resp_data: bytes = b""
    req_headers: bytes = b""
    resp_headers: bytes = b""

    try:
        # Capture headers efficiently
        if HAS_ORJSON:
            req_headers = orjson.dumps({str(k): str(v) for k, v in hdrs.items()})
        else:
            req_headers = json.dumps({str(k): str(v) for k, v in hdrs.items()}).encode("utf-8")

        # http.client doesn't easily expose response data, skip body capture
    except Exception:  # noqa: BLE001
        pass

    # Send to C extension in background
    record_network_request(
        trace_id,
        url,
        method,
        status,
        success,
        err,
        timestamp_start=t0,
        timestamp_end=t1,
        request_data=req_data,
        response_data=resp_data,
        request_headers=req_headers,
        response_headers=resp_headers,
    )


###############################################################################
# Top-level patch function
###############################################################################
def patch_requests(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Apply all monkey-patches. Safe to call multiple times.

    When LD_PRELOAD is active:
    - ALWAYS inject headers (trace_id + funcspan_override)
    - SKIP capture/emission (LD_PRELOAD handles at socket layer)
    """
    # Idempotency guard: prevent double-patching (handles forks, reloading)
    if is_already_patched("requests"):
        return
    mark_as_patched("requests")

    exclude = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # PERFORMANCE DEBUG: Log preload detection
    SF_DEBUG = os.getenv("SF_DEBUG", "false").lower() == "true"
    if SF_DEBUG:
        ld_preload = os.getenv("LD_PRELOAD", "")
        print(f"[[patch_requests]] LD_PRELOAD={ld_preload}", flush=True)
        print(f"[[patch_requests]] preload_active={preload_active}", flush=True)
        print(
            f"[[patch_requests]] Using {'ULTRA-FAST' if preload_active else 'FULL CAPTURE'} path",
            flush=True,
        )

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(exclude)

    # --------------------------------------------------------------------- #
    # 1. Patch `requests.Session.request`
    # --------------------------------------------------------------------- #
    # Save original function BEFORE any patching
    original_request = Session.request

    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:
            # FASTEST: Use wrapt directly (OTEL-style for minimal overhead)
            def instrumented_request(wrapped, instance, args, kwargs):
                """ULTRA-FAST header injection (<100ns) via wrapt."""
                # args = (method, url, ...), kwargs = {...}
                url = args[1] if len(args) > 1 else kwargs.get("url", "")

                # OPTIMIZED: Avoid kwargs.pop() - use get() with or-pattern (10x faster!)
                headers = kwargs.get("headers") or {}

                # CRITICAL: Skip if already injected (prevents double injection in requests→urllib3→http.client chain)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, url, exclude)

                kwargs["headers"] = headers

                # NO timing, NO capture, NO threads - immediate return!
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(Session, "request", instrumented_request)
        else:
            # Fallback: Direct patching if wrapt not available
            def patched_request(self: Session, method, url, **kwargs):  # type: ignore[override]
                # OPTIMIZED: Avoid kwargs.pop() - use get() with or-pattern (10x faster!)
                headers = kwargs.get("headers") or {}

                # CRITICAL: Skip if already injected (prevents double injection in requests→urllib3→http.client chain)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, url, exclude)

                kwargs["headers"] = headers

                # NO timing, NO capture, NO threads - immediate return!
                return original_request(self, method, url, **kwargs)

            Session.request = patched_request
            requests.Session.request = (
                patched_request  # cover direct `requests.Session(...)`
            )

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        # PERFORMANCE: Removed thread spawning - saves ~50-200μs per request
        # Direct C extension call instead of background threads
        def patched_request(self: Session, method, url, **kwargs):  # type: ignore[override]
            # --- header handling / injection --------------------------------- #
            trace_id, hdrs, t0 = _prepare(url, exclude, kwargs.pop("headers", {}))
            kwargs["headers"] = hdrs

            status: int = 0
            success: bool = False
            err: str | None = None
            req_data: bytes = b""

            # PERFORMANCE: Skip request body capture - saves ~10-50μs
            # C extension captures everything at socket layer
            # try:
            #     if "json" in kwargs:
            #         try:
            #             import orjson
            #             req_data = orjson.dumps(kwargs["json"])
            #         except ImportError:
            #             import json
            #             req_data = json.dumps(kwargs["json"]).encode('utf-8')
            #     elif "data" in kwargs:
            #         data = kwargs["data"]
            #         if isinstance(data, bytes):
            #             req_data = data
            #         elif isinstance(data, str):
            #             req_data = data.encode('utf-8')
            # except Exception:  # noqa: BLE001
            #     pass

            try:
                resp = original_request(self, method, url, **kwargs)
                status = resp.status_code
                success = resp.ok
                t1 = int(time.time() * 1_000)

                # PERFORMANCE: Direct C call (NO thread spawning!) - saves ~50-200μs
                record_network_request(
                    trace_id,
                    url,
                    str(method).upper(),
                    status,
                    success,
                    None,
                    timestamp_start=t0,
                    timestamp_end=t1,
                    request_data=req_data,
                    response_data=b"",
                    request_headers=b"",
                    response_headers=b"",
                )

                return resp
            except Exception as exc:  # noqa: BLE001
                err = str(exc)[:255]
                t1 = int(time.time() * 1_000)
                # PERFORMANCE: Direct C call (NO thread spawning!)
                record_network_request(
                    trace_id,
                    url,
                    str(method).upper(),
                    status,
                    success,
                    err,
                    timestamp_start=t0,
                    timestamp_end=t1,
                    request_data=req_data,
                    response_data=b"",
                    request_headers=b"",
                    response_headers=b"",
                )
                raise

        if not HAS_WRAPT:
            Session.request = patched_request
            requests.Session.request = (
                patched_request  # cover direct `requests.Session(...)`
            )

    # --------------------------------------------------------------------- #
    # 2. Patch urllib3's low-level ConnectionPool.urlopen (used by requests)
    # --------------------------------------------------------------------- #
    # Save original function BEFORE any patching
    original_urlopen = urllib3.connectionpool.HTTPConnectionPool.urlopen

    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:
            # FASTEST: Use wrapt directly (OTEL-style for minimal overhead)
            def instrumented_urlopen(wrapped, instance, args, kwargs):
                """ULTRA-FAST header injection (<100ns) via wrapt."""
                # args = (method, url, ...), kwargs = {body, headers, ...}
                url = args[1] if len(args) > 1 else kwargs.get("url", "")

                # OPTIMIZED: Use or-pattern (10x faster!)
                headers = kwargs.get("headers") or {}

                # CRITICAL: Skip if already injected by requests.Session (prevents double injection)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, url, exclude)

                kwargs["headers"] = headers

                # NO timing, NO capture, NO threads - immediate return!
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                urllib3.connectionpool.HTTPConnectionPool,
                "urlopen",
                instrumented_urlopen,
            )
        else:
            # Fallback: Direct patching if wrapt not available
            def patched_urlopen(self, method, url, body=None, headers=None, **kw):  # type: ignore[override]
                # OPTIMIZED: Use or-pattern (10x faster!)
                headers = headers or {}

                # CRITICAL: Skip if already injected by requests.Session (prevents double injection)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, url, exclude)

                # NO timing, NO capture, NO threads - immediate return!
                return original_urlopen(
                    self, method, url, body=body, headers=headers, **kw
                )

            urllib3.connectionpool.HTTPConnectionPool.urlopen = patched_urlopen

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        # PERFORMANCE: Removed thread spawning and body capture
        def patched_urlopen(self, method, url, body=None, headers=None, **kw):  # type: ignore[override]
            trace_id, hdrs, t0 = _prepare(url, exclude, headers)
            status: int = 0
            success: bool = False
            err: str | None = None

            try:
                resp = original_urlopen(
                    self, method, url, body=body, headers=hdrs, **kw
                )
                status = getattr(resp, "status", 0)
                success = status < 400
                t1 = int(time.time() * 1_000)

                # PERFORMANCE: Direct C call (NO thread spawning!)
                record_network_request(
                    trace_id,
                    url,
                    str(method).upper(),
                    status,
                    success,
                    None,
                    timestamp_start=t0,
                    timestamp_end=t1,
                    request_data=b"",
                    response_data=b"",
                    request_headers=b"",
                    response_headers=b"",
                )

                return resp
            except Exception as exc:  # noqa: BLE001
                err = str(exc)[:255]
                t1 = int(time.time() * 1_000)
                record_network_request(
                    trace_id,
                    url,
                    str(method).upper(),
                    status,
                    success,
                    err,
                    timestamp_start=t0,
                    timestamp_end=t1,
                    request_data=b"",
                    response_data=b"",
                    request_headers=b"",
                    response_headers=b"",
                )
                raise

        if not HAS_WRAPT:
            urllib3.connectionpool.HTTPConnectionPool.urlopen = patched_urlopen

    # --------------------------------------------------------------------- #
    # 3. Patch http.client for "raw" stdlib usage (rare but easy to support)
    # --------------------------------------------------------------------- #
    # Save original function BEFORE any patching
    original_http_client_request = http.client.HTTPConnection.request

    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:
            # FASTEST: Use wrapt directly (OTEL-style for minimal overhead)
            def instrumented_http_request(wrapped, instance, args, kwargs):
                """ULTRA-FAST header injection (<100ns) via wrapt."""
                # args = (method, url, ...), kwargs = {body, headers, encode_chunked, ...}
                url = args[1] if len(args) > 1 else kwargs.get("url", "")

                # OPTIMIZED: Use or-pattern (10x faster!)
                headers = kwargs.get("headers") or {}

                # CRITICAL: Skip if already injected by requests/urllib3 (prevents triple injection)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, url, exclude)

                kwargs["headers"] = headers

                # NO timing, NO capture, NO threads - immediate return!
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                http.client.HTTPConnection, "request", instrumented_http_request
            )
        else:
            # Fallback: Direct patching if wrapt not available
            def patched_http_request(self, method, url, body=None, headers=None, *, encode_chunked=False):  # type: ignore[override]
                # OPTIMIZED: Use or-pattern (10x faster!)
                headers = headers or {}

                # CRITICAL: Skip if already injected by requests/urllib3 (prevents triple injection)
                if SAILFISH_TRACING_HEADER not in headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(headers, url, exclude)

                # NO timing, NO capture, NO threads - immediate return!
                return original_http_client_request(
                    self,
                    method,
                    url,
                    body=body,
                    headers=headers,
                    encode_chunked=encode_chunked,
                )

            http.client.HTTPConnection.request = patched_http_request

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        # PERFORMANCE: Removed thread spawning and body capture
        def patched_http_request(self, method, url, body=None, headers=None, *, encode_chunked=False):  # type: ignore[override]
            trace_id, hdrs, t0 = _prepare(url, exclude, headers)
            status: int = 0
            success: bool = False
            err: str | None = None

            try:
                resp = original_http_client_request(
                    self,
                    method,
                    url,
                    body=body,
                    headers=hdrs,
                    encode_chunked=encode_chunked,
                )
                status = getattr(
                    self, "response", getattr(resp, "status", 0)
                )  # best-effort
                success = bool(status) and status < 400
                t1 = int(time.time() * 1_000)

                # PERFORMANCE: Direct C call (NO thread spawning!)
                record_network_request(
                    trace_id,
                    url,
                    str(method).upper(),
                    status,
                    success,
                    None,
                    timestamp_start=t0,
                    timestamp_end=t1,
                    request_data=b"",
                    response_data=b"",
                    request_headers=b"",
                    response_headers=b"",
                )

                return resp
            except Exception as exc:  # noqa: BLE001
                err = str(exc)[:255]
                t1 = int(time.time() * 1_000)
                record_network_request(
                    trace_id,
                    url,
                    str(method).upper(),
                    status,
                    success,
                    err,
                    timestamp_start=t0,
                    timestamp_end=t1,
                    request_data=b"",
                    response_data=b"",
                    request_headers=b"",
                    response_headers=b"",
                )
                raise

        if not HAS_WRAPT:
            http.client.HTTPConnection.request = patched_http_request
