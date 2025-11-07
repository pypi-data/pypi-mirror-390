"""
Patch httpx to inject tracing headers and capture network requests using event hooks.

• For every outbound request, propagate the SAILFISH_TRACING_HEADER + FUNCSPAN_OVERRIDE_HEADER
  unless the destination host is in `domains_to_not_propagate_headers_to`.
• Fire NetworkRequestTransmitter via utils.record_network_request
  so we always capture (url, status, timings, success, error).
• When LD_PRELOAD is active, ONLY inject headers (skip capture - socket layer handles it).
"""

from __future__ import annotations

import asyncio
import os
import threading
import time
from typing import Dict, List, Optional, Tuple

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

from ...constants import FUNCSPAN_OVERRIDE_HEADER, SAILFISH_TRACING_HEADER
from ...thread_local import (
    activate_reentrancy_guards_exception,
    activate_reentrancy_guards_logging,
    activate_reentrancy_guards_print,
    get_funcspan_override,
    trace_id_ctx,
)
from .utils import (
    get_trace_and_should_propagate,
    get_trace_and_should_propagate_fast,
    init_fast_header_check,
    inject_headers_ultrafast,
    record_network_request,
)
from .._patch_tracker import is_already_patched, mark_as_patched

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False

###############################################################################
# Internal helpers
###############################################################################

# header names used for re-entrancy guards
REENTRANCY_GUARD_LOGGING_PREACTIVE = "reentrancy_guard_logging_preactive"
REENTRANCY_GUARD_PRINT_PREACTIVE = "reentrancy_guard_print_preactive"
REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE = "reentrancy_guard_exception_preactive"


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active (same logic as requests.py)."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def _activate_rg(headers: Dict[str, str]) -> None:
    """Turn the three 'preactive' guard flags ON for downstream hops."""
    headers[REENTRANCY_GUARD_LOGGING_PREACTIVE] = "true"
    headers[REENTRANCY_GUARD_PRINT_PREACTIVE] = "true"
    headers[REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE] = "true"


def _check_rg(headers: Dict[str, str]) -> None:
    """If any pre-active guard present, switch the corresponding guard on."""
    if headers.get(REENTRANCY_GUARD_LOGGING_PREACTIVE, "false").lower() == "true":
        activate_reentrancy_guards_logging()
    if headers.get(REENTRANCY_GUARD_PRINT_PREACTIVE, "false").lower() == "true":
        activate_reentrancy_guards_print()
    if headers.get(REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE, "false").lower() == "true":
        activate_reentrancy_guards_exception()


def _prepare(
    url: str,
    domains_to_skip: List[str],
    headers: Dict[str, str],
) -> Tuple[str, Dict[str, str], int]:
    """
    Inject trace header + funcspan override header (unless excluded) and return:
        trace_id, merged_headers, timestamp_ms

    ULTRA-FAST: <20ns overhead for header injection.
    """
    trace_id, propagate = get_trace_and_should_propagate(url, domains_to_skip)
    hdrs: Dict[str, str] = dict(headers or {})
    _check_rg(hdrs)
    if propagate:
        hdrs[SAILFISH_TRACING_HEADER] = trace_id

        # Inject funcspan override header if present (ContextVar lookup ~8ns)
        try:
            funcspan_override = get_funcspan_override()
            if funcspan_override is not None:
                hdrs[FUNCSPAN_OVERRIDE_HEADER] = funcspan_override
        except Exception:
            pass

    _activate_rg(hdrs)
    return trace_id, hdrs, int(time.time() * 1_000)


def _capture_request_data(request) -> bytes:
    """Capture request body data as bytes."""
    req_data = b""
    try:
        # Check if content is available
        if hasattr(request, "content"):
            content = request.content
            if isinstance(content, bytes):
                req_data = content
            elif isinstance(content, str):
                req_data = content.encode("utf-8")
    except Exception:  # noqa: BLE001
        pass
    return req_data


def _capture_and_record(
    trace_id: str,
    url: str,
    method: str,
    status: int,
    success: bool,
    err: str | None,
    t0: int,
    t1: int,
    req_data: bytes,
    req_headers: bytes,
    resp_data: bytes,
    resp_headers: bytes,
) -> None:
    """Schedule capture and record in background thread AFTER response is returned to user."""

    def _do_record():
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

    threading.Thread(target=_do_record, daemon=True).start()


###############################################################################
# Event hook factories
###############################################################################


def _make_request_hook(domains_to_skip: List[str], preload_active: bool):
    """Create a sync request hook that injects headers before request is sent."""

    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        def request_hook(request):
            """Inject tracing headers into outbound request (ultra-fast C extension)."""
            try:
                url = str(request.url)
                # CRITICAL: Skip if already injected (prevents double injection)
                if SAILFISH_TRACING_HEADER not in request.headers:
                    # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                    inject_headers_ultrafast(request.headers, url, domains_to_skip)
            except Exception:  # noqa: BLE001
                pass  # Fail silently to not break requests

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        def request_hook(request):
            """Inject tracing headers into outbound request (optimized - no debug logging)."""
            try:
                url = str(request.url)
                trace_id, hdrs, t0 = _prepare(
                    url, domains_to_skip, dict(request.headers)
                )

                # Update request headers
                request.headers.update(hdrs)

                # Store metadata on request for response hook to use
                # httpx Request objects always have an extensions dict
                request.extensions["sf_trace_id"] = trace_id
                request.extensions["sf_timestamp_start"] = t0

                # Capture request data
                request.extensions["sf_request_data"] = _capture_request_data(request)

                # Capture request headers
                if HAS_ORJSON:
                    request.extensions["sf_request_headers"] = orjson.dumps(
                        dict(request.headers)
                    )
                else:
                    request.extensions["sf_request_headers"] = json.dumps(
                        dict(request.headers)
                    ).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass  # Fail silently to not break requests

    return request_hook


def _make_async_request_hook(domains_to_skip: List[str], preload_active: bool):
    """Create an async request hook that injects headers before request is sent."""

    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        async def async_request_hook(request):
            """Inject tracing headers into outbound request (ultra-fast C extension)."""
            # Get trace ID and check if we should propagate
            url = str(request.url)
            # CRITICAL: Skip if already injected (prevents double injection)
            if SAILFISH_TRACING_HEADER not in request.headers:
                # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                inject_headers_ultrafast(request.headers, url, domains_to_skip)

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        async def async_request_hook(request):
            """Inject tracing headers into outbound request (optimized - no debug logging)."""
            # Get trace ID and timing
            url = str(request.url)
            trace_id = trace_id_ctx.get(None) or ""
            t0 = int(time.time() * 1_000)

            # Check and activate re-entrancy guards from incoming headers (avoid dict copy)
            req_headers = request.headers
            if (
                req_headers.get(REENTRANCY_GUARD_LOGGING_PREACTIVE, "false").lower()
                == "true"
            ):
                activate_reentrancy_guards_logging()
            if (
                req_headers.get(REENTRANCY_GUARD_PRINT_PREACTIVE, "false").lower()
                == "true"
            ):
                activate_reentrancy_guards_print()
            if (
                req_headers.get(REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE, "false").lower()
                == "true"
            ):
                activate_reentrancy_guards_exception()

            # CRITICAL: Skip if already injected (prevents double injection)
            if SAILFISH_TRACING_HEADER not in req_headers:
                # ULTRA-FAST: Thread-local cache + direct ContextVar.get() (<100ns!)
                inject_headers_ultrafast(req_headers, url, domains_to_skip)

            # Activate re-entrancy guards for downstream (inject into request)
            req_headers[REENTRANCY_GUARD_LOGGING_PREACTIVE] = "true"
            req_headers[REENTRANCY_GUARD_PRINT_PREACTIVE] = "true"
            req_headers[REENTRANCY_GUARD_EXCEPTIONS_PREACTIVE] = "true"

            # Store metadata on request for response hook to use
            request.extensions["sf_trace_id"] = trace_id
            request.extensions["sf_timestamp_start"] = t0

            # Capture request data
            request.extensions["sf_request_data"] = _capture_request_data(request)

            # Capture request headers (AFTER injection)
            if HAS_ORJSON:
                request.extensions["sf_request_headers"] = orjson.dumps(
                    dict(req_headers)
                )
            else:
                request.extensions["sf_request_headers"] = json.dumps(
                    dict(req_headers)
                ).encode("utf-8")

    return async_request_hook


def _make_response_hook(preload_active: bool):
    """Create a response hook that captures and records response data."""

    def response_hook(response):
        """Capture response data and record the network request."""
        # Skip recording if LD_PRELOAD is active (socket layer already captured it)
        if preload_active:
            return

        # Extract metadata from request
        request = response.request
        trace_id = request.extensions.get("sf_trace_id", "")
        t0 = request.extensions.get("sf_timestamp_start", 0)
        req_data = request.extensions.get("sf_request_data", b"")
        req_headers = request.extensions.get("sf_request_headers", b"")

        # Capture response data
        url = str(request.url)
        method = str(request.method).upper()
        status = response.status_code
        success = status < 400
        t1 = int(time.time() * 1_000)

        resp_data = b""
        resp_headers = b""

        try:
            # Capture response body - check if already consumed/materialized
            # Don't force materialization of streaming responses
            if hasattr(response, '_content') and response._content is not None:
                # Response body already materialized (non-streaming or already read)
                resp_data = response._content
            elif hasattr(response, 'is_stream_consumed') and not response.is_stream_consumed:
                # Streaming response not yet consumed - don't materialize
                # We'll capture what we can without breaking streaming behavior
                resp_data = b""
            else:
                # Safe to access .content (either not streaming or already consumed)
                resp_data = response.content

            # Capture response headers
            if HAS_ORJSON:
                resp_headers = orjson.dumps({str(k): str(v) for k, v in response.headers.items()})
            else:
                resp_headers = json.dumps({str(k): str(v) for k, v in response.headers.items()}).encode("utf-8")
        except Exception:  # noqa: BLE001
            pass

        # Record in background thread
        _capture_and_record(
            trace_id,
            url,
            method,
            status,
            success,
            None,
            t0,
            t1,
            req_data,
            req_headers,
            resp_data,
            resp_headers,
        )

    return response_hook


def _make_async_response_hook(preload_active: bool):
    """Create an async response hook that captures and records response data."""

    async def async_response_hook(response):
        """Capture response data and record the network request (optimized - no debug logging)."""
        # Skip recording if LD_PRELOAD is active (socket layer already captured it)
        if preload_active:
            return

        try:
            # Extract metadata from request
            request = response.request
            trace_id = request.extensions.get("sf_trace_id", "")
            t0 = request.extensions.get("sf_timestamp_start", 0)
            req_data = request.extensions.get("sf_request_data", b"")
            req_headers = request.extensions.get("sf_request_headers", b"")

            # Capture response data
            url = str(request.url)
            method = str(request.method).upper()
            status = response.status_code
            success = status < 400
            t1 = int(time.time() * 1_000)

            resp_data = b""
            resp_headers = b""

            try:
                # Capture response body - check if already consumed/materialized
                # Don't force materialization of streaming responses
                if hasattr(response, '_content') and response._content is not None:
                    # Response body already materialized (non-streaming or already read)
                    resp_data = response._content
                elif hasattr(response, 'is_stream_consumed') and not response.is_stream_consumed:
                    # Streaming response not yet consumed - don't materialize
                    # We'll capture what we can without breaking streaming behavior
                    resp_data = b""
                else:
                    # Safe to read (either not streaming or already consumed)
                    # For non-streaming async responses, read the body
                    try:
                        await response.aread()
                        resp_data = response.content
                    except asyncio.CancelledError:
                        raise  # CRITICAL: Must re-raise CancelledError immediately
                    except Exception:
                        resp_data = b""

                # Capture response headers
                if HAS_ORJSON:
                    resp_headers = orjson.dumps({str(k): str(v) for k, v in response.headers.items()})
                else:
                    resp_headers = json.dumps({str(k): str(v) for k, v in response.headers.items()}).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            # Record in background thread
            _capture_and_record(
                trace_id,
                url,
                method,
                status,
                success,
                None,
                t0,
                t1,
                req_data,
                req_headers,
                resp_data,
                resp_headers,
            )
        except Exception:  # noqa: BLE001
            pass  # Silently fail to not break requests

    return async_response_hook


###############################################################################
# Top-level patch function
###############################################################################


def patch_httpx(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Patch httpx to inject SAILFISH_TRACING_HEADER into all outbound requests
    using event hooks. Safe to call even if httpx is not installed.

    When LD_PRELOAD is active:
    - ALWAYS inject headers (trace_id + funcspan_override)
    - SKIP capture/emission (LD_PRELOAD handles at socket layer)
    - Uses ultra-fast C extension for <10ns overhead
    """
    # Idempotency guard: prevent double-patching (handles forks, reloading)
    if is_already_patched("httpx"):
        return
    mark_as_patched("httpx")

    try:
        import httpx
    except ImportError:
        return  # No httpx installed—nothing to patch

    domains = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(domains)

    # Create hooks
    sync_request_hook = _make_request_hook(domains, preload_active)
    async_request_hook = _make_async_request_hook(domains, preload_active)
    sync_response_hook = _make_response_hook(preload_active)
    async_response_hook = _make_async_response_hook(preload_active)

    # Patch Client.__init__ to attach sync hooks
    if HAS_WRAPT:

        def instrumented_client_init(wrapped, instance, args, kwargs):
            """Ultra-fast hook injection using wrapt."""
            # Get existing event_hooks or create empty dict
            event_hooks = kwargs.get("event_hooks") or {}

            # Add our sync hooks to the request and response lists
            event_hooks.setdefault("request", []).append(sync_request_hook)
            event_hooks.setdefault("response", []).append(sync_response_hook)

            kwargs["event_hooks"] = event_hooks
            return wrapped(*args, **kwargs)

        wrapt.wrap_function_wrapper(
            "httpx", "Client.__init__", instrumented_client_init
        )
    else:
        original_client_init = httpx.Client.__init__

        def patched_client_init(self, *args, **kwargs):
            # Get existing event_hooks or create empty dict
            event_hooks = kwargs.get("event_hooks") or {}

            # Add our sync hooks to the request and response lists
            event_hooks.setdefault("request", []).append(sync_request_hook)
            event_hooks.setdefault("response", []).append(sync_response_hook)

            kwargs["event_hooks"] = event_hooks
            original_client_init(self, *args, **kwargs)

        httpx.Client.__init__ = patched_client_init

    # Patch AsyncClient.__init__ to attach async hooks
    if HAS_WRAPT:

        def instrumented_async_client_init(wrapped, instance, args, kwargs):
            """Ultra-fast hook injection using wrapt."""
            # Get existing event_hooks or create empty dict
            event_hooks = kwargs.get("event_hooks") or {}

            # Add our ASYNC hooks to the request and response lists
            event_hooks.setdefault("request", []).append(async_request_hook)
            event_hooks.setdefault("response", []).append(async_response_hook)

            kwargs["event_hooks"] = event_hooks
            return wrapped(*args, **kwargs)

        wrapt.wrap_function_wrapper(
            "httpx", "AsyncClient.__init__", instrumented_async_client_init
        )
    else:
        original_async_client_init = httpx.AsyncClient.__init__

        def patched_async_client_init(self, *args, **kwargs):
            # Get existing event_hooks or create empty dict
            event_hooks = kwargs.get("event_hooks") or {}

            # Add our ASYNC hooks to the request and response lists
            event_hooks.setdefault("request", []).append(async_request_hook)
            event_hooks.setdefault("response", []).append(async_response_hook)

            kwargs["event_hooks"] = event_hooks
            original_async_client_init(self, *args, **kwargs)

        httpx.AsyncClient.__init__ = patched_async_client_init
