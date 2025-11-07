"""
Shared helpers used by all network-patch modules.
"""

from __future__ import annotations

import os
import time
import threading
from functools import lru_cache
from typing import List, Tuple, Optional
from urllib.parse import urlparse

from ... import app_config
from ...constants import SAILFISH_TRACING_HEADER, FUNCSPAN_OVERRIDE_HEADER
from ...env_vars import SF_DEBUG
from ...regular_data_transmitter import NetworkRequestTransmitter
from ...thread_local import (
    get_or_set_sf_trace_id,
    is_network_recording_suppressed,
    trace_id_ctx,
    funcspan_override_ctx,
    get_outbound_headers_with_new_uuid,
    get_funcspan_override,
)

# Try to import the C extension for ultra-fast network request recording
try:
    from ... import _sffastnet
    _FAST_NET_AVAILABLE = True
except ImportError:
    _FAST_NET_AVAILABLE = False
    _sffastnet = None

# Try to import the C extension for http.client patching (captures headers/bodies)
try:
    from ... import _sffastnetworkrequest
    _FAST_NETWORKREQUEST_AVAILABLE = True
except ImportError:
    _FAST_NETWORKREQUEST_AVAILABLE = False
    _sffastnetworkrequest = None

# Try to import the C extension for ultra-fast header checking (domain filtering)
try:
    from ... import _sfheadercheck
    _HAS_FAST_HEADER_CHECK = True
except ImportError:
    _HAS_FAST_HEADER_CHECK = False
    _sfheadercheck = None

_FAST_NET_INITIALIZED = False
_FAST_NETWORKREQUEST_INITIALIZED = False

# GraphQL mutation for network requests
_COLLECT_NETWORK_REQUEST_MUTATION = """
mutation collectNetworkRequest($data: NetworkRequestInput!) {
  collectNetworkRequest(data: $data)
}
"""

def init_fast_networkrequest_tracking():
    """Initialize the C extension for http.client network request tracking (with body/header capture)."""
    global _FAST_NETWORKREQUEST_INITIALIZED
    if not _FAST_NETWORKREQUEST_AVAILABLE or _FAST_NETWORKREQUEST_INITIALIZED or not _sffastnetworkrequest:
        return False

    try:
        http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0
        ok = _sffastnetworkrequest.init_networkhop(
            url=app_config._sailfish_graphql_endpoint,
            query=_COLLECT_NETWORK_REQUEST_MUTATION,
            api_key=app_config._sailfish_api_key,
            service_uuid=app_config._service_uuid or "",
            library=getattr(app_config, "library", "sf-veritas"),
            version=getattr(app_config, "version", "0.0.0"),
            http2=http2,
        )
        if ok:
            _FAST_NETWORKREQUEST_INITIALIZED = True
            if SF_DEBUG:
                print("[_sffastnetworkrequest] initialized (libcurl sender with body/header capture)", log=False)
            return True
    except Exception as e:
        if SF_DEBUG:
            print(f"[_sffastnetworkrequest] init failed; falling back: {e}", log=False)

    return False

def init_fast_network_tracking():
    """Initialize the C extensions for network request tracking (both _sffastnet and _sffastnetworkrequest)."""
    global _FAST_NET_INITIALIZED

    # Initialize _sffastnet (generic network requests)
    net_ok = False
    if _FAST_NET_AVAILABLE and not _FAST_NET_INITIALIZED and _sffastnet:
        try:
            http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0
            ok = _sffastnet.init(
                url=app_config._sailfish_graphql_endpoint,
                query=_COLLECT_NETWORK_REQUEST_MUTATION,
                api_key=app_config._sailfish_api_key,
                http2=http2,
            )
            if ok:
                _FAST_NET_INITIALIZED = True
                net_ok = True
                if SF_DEBUG:
                    print("[_sffastnet] initialized (libcurl sender)", log=False)
        except Exception as e:
            if SF_DEBUG:
                print(f"[_sffastnet] init failed; falling back: {e}", log=False)

    # Initialize _sffastnetworkrequest (http.client with body/header capture)
    netreq_ok = init_fast_networkrequest_tracking()

    return net_ok or netreq_ok


###############################################################################
# ULTRA-FAST Header Injection (<100ns target)
###############################################################################

# Thread-local cache for ultra-fast header injection
_thread_local = threading.local()

# [DIAGNOSTICS] Global counters for tracking request success/failure
_request_attempt_counter = 0
_request_success_counter = 0
_request_failure_counter = 0
_counter_lock = threading.Lock()

def get_request_stats() -> dict:
    """Get diagnostic statistics for request tracking."""
    return {
        "attempts": _request_attempt_counter,
        "success": _request_success_counter,
        "failures": _request_failure_counter,
        "deficit": _request_attempt_counter - _request_success_counter - _request_failure_counter,
    }

def print_request_stats() -> None:
    """Print diagnostic statistics for request tracking."""
    stats = get_request_stats()
    print(f"\n[REQUEST_STATS] attempts={stats['attempts']} success={stats['success']} failures={stats['failures']} deficit={stats['deficit']}", log=False)
    if stats["deficit"] > 0:
        print(f"[REQUEST_STATS] ⚠️  WARNING: {stats['deficit']} requests neither succeeded nor failed - possible bug!", log=False)
    if stats["failures"] > 0:
        print(f"[REQUEST_STATS] ⚠️  WARNING: {stats['failures']} requests failed - check error logs above", log=False)

def track_request_result(success: bool, error: Optional[Exception] = None, url: str = "") -> None:
    """Track whether a request succeeded or failed (only when SF_DEBUG is enabled)."""
    if not SF_DEBUG:
        return  # Skip tracking entirely to avoid lock contention in production

    global _request_success_counter, _request_failure_counter
    with _counter_lock:
        if success:
            _request_success_counter += 1
        else:
            _request_failure_counter += 1
            error_type = type(error).__name__ if error else "Unknown"
            error_msg = str(error) if error else "Unknown error"
            print(f"[track_request_result] ❌ REQUEST FAILED: {error_type}: {error_msg} (url={url})", log=False)

def inject_headers_ultrafast(headers_dict: dict, url: str, domains_to_skip: List[str]) -> None:
    """
    ULTRA-FAST header injection (~100ns average).

    Injects X-Sf3-Rid and X-Sf3-FunctionSpanCaptureOverride headers directly into dict.
    Uses pre-built headers from OutboundHeaderManager with background UUID4 generation.

    Performance:
    - Filtered domain: ~30ns (domain check only)
    - Fast path (pre-generated): ~100ns (domain check + header injection)
    - Slow path (generate on-demand): ~500ns (domain check + synchronous UUID4)

    Args:
        headers_dict: Dictionary to inject headers into (mutated in-place)
        url: Destination URL for domain filtering
        domains_to_skip: List of domains to skip header propagation
    """
    # [DIAGNOSTICS] Count request attempts (only when SF_DEBUG is enabled to avoid lock contention)
    if SF_DEBUG:
        global _request_attempt_counter
        with _counter_lock:
            _request_attempt_counter += 1
            attempt_id = _request_attempt_counter
        print(f"[inject_headers_ultrafast] 🚀 CALLED #{attempt_id} with url={url}, domains_to_skip={domains_to_skip}", log=False)

    # FAST: Domain filtering check (LRU cached, ~20ns)
    if domains_to_skip:
        domain = extract_domain(url)
        if domain in domains_to_skip:
            if SF_DEBUG:
                print(f"[inject_headers_ultrafast] ⛔ Skipped (domain filtered)", log=False)
            return

    # ULTRA-FAST: Get pre-built header with new UUID (~10-20ns with LD_PRELOAD)
    # Measure ONLY the critical path (excluding debug prints)
    if SF_DEBUG:
        start_ns = time.perf_counter_ns()

    outbound_headers = get_outbound_headers_with_new_uuid()

    if SF_DEBUG:
        get_headers_ns = time.perf_counter_ns() - start_ns

    if SF_DEBUG:
        print(f"[inject_headers_ultrafast] 📦 get_outbound_headers_with_new_uuid() returned: {outbound_headers} (took {get_headers_ns}ns)", log=False)

    if outbound_headers:
        # FAST: Dict update (~30ns)
        if SF_DEBUG:
            start_update_ns = time.perf_counter_ns()

        headers_dict.update(outbound_headers)

        if SF_DEBUG:
            update_ns = time.perf_counter_ns() - start_update_ns
            total_ns = get_headers_ns + update_ns
            # Pre-generated = ContextVar lookup (10-50ns) + dict.get() (10-50ns) + dict.update() (20-50ns) = ~50-150ns typical
            # Allow up to 1μs for variance (CPU scheduler, context switches, etc.)
            status = "pre-generated" if total_ns < 1000 else "generated on-demand"
            print(f"[inject_headers_ultrafast] ✅ Updated headers_dict. get={get_headers_ns}ns, update={update_ns}ns, total={total_ns}ns ({status})", log=False)
    else:
        if SF_DEBUG:
            print(f"[inject_headers_ultrafast] ⚠️ No outbound headers returned (empty dict)", log=False)


###############################################################################
# Domain-parsing utility  (no external network / no tldextract needed)
###############################################################################
@lru_cache(maxsize=256)
def extract_domain(url: str) -> str:
    """
    Return a canonical host name for header-propagation checks.

    • Works entirely offline (std-lib only) – no remote download or file locks.
    • Keeps sub-domains intact, just strips a leading “www.” and port numbers.

    Examples
    --------
    >>> extract_domain("https://www.example.com:443/path")
    'example.com'
    >>> extract_domain("https://api.foo.bar.example.co.uk/v1")
    'api.foo.bar.example.co.uk'
    """
    try:
        host = urlparse(url).hostname or url
    except Exception:
        host = url  # fall back to raw string on malformed URLs
    if host.startswith("www."):
        host = host[4:]
    return host.lower()


###############################################################################
# Header-propagation + network-recording helpers
###############################################################################
def get_trace_and_should_propagate(
    url: str,
    domains_to_not_propagate: List[str],
) -> Tuple[str, bool]:
    """
    Returns  (trace_id, should_propagate?)  for the given destination `url`.
    """
    _, trace_id = get_or_set_sf_trace_id()
    domain = extract_domain(url)
    allow_header = domain not in domains_to_not_propagate
    return trace_id, allow_header


def init_fast_header_check(domains_to_not_propagate: List[str]) -> bool:
    """
    Initialize the C extension for ultra-fast header checking with skip list.

    Should be called once at patch time to set up the domain filtering list.

    Returns: True if C extension initialized successfully, False otherwise.
    """
    if _HAS_FAST_HEADER_CHECK and _sfheadercheck:
        try:
            _sfheadercheck.init_header_check(domains_to_not_propagate)
            return True
        except Exception:
            return False
    return False


def get_trace_and_should_propagate_fast(
    url: str,
    domains_to_not_propagate: List[str],
) -> Tuple[str, bool, Optional[str]]:
    """
    Ultra-fast path using C extension for domain filtering.

    Returns: (trace_id, should_propagate, funcspan_override)

    Performance:
    - Empty skip list: ~15ns (ContextVar reads only)
    - With skip list: ~25ns (C domain parse + hash lookup + ContextVars)
    - 10x faster than Python implementation (50-100ns)

    Falls back to Python implementation if C extension not available.
    """
    if _HAS_FAST_HEADER_CHECK and _sfheadercheck:
        # C extension handles domain filtering + ContextVar reads
        # Returns: (should_inject: bool, trace_id: str, funcspan_override: str | None)
        try:
            should_inject, trace_id, funcspan_override = _sfheadercheck.should_inject_headers(url)
            return trace_id, should_inject, funcspan_override
        except Exception:
            # Fall back to Python on any error
            pass

    # Fallback to Python implementation
    trace_id, allow = get_trace_and_should_propagate(url, domains_to_not_propagate)
    funcspan_override = get_funcspan_override()
    return trace_id, allow, funcspan_override


def record_network_request(
    trace_id: str,
    url: str,
    method: str,
    status_code: int,
    success: bool,
    error: str | None = None,
    timestamp_start: int | None = None,
    timestamp_end: int | None = None,
    request_data: bytes = b"",
    response_data: bytes = b"",
    request_headers: bytes = b"",
    response_headers: bytes = b"",
) -> None:
    """
    Fire off a GraphQL NetworkRequest mutation via C extension (fast path)
    or NetworkRequestTransmitter (fallback).
    Handles tripartite trace-ID splitting and default timestamps.
    NEW: Supports request_data and response_data capture.
    """
    if is_network_recording_suppressed():
        return

    session_id, page_visit_id, request_id = None, None, None
    parts = trace_id.split("/")
    if parts:
        session_id = parts[0]
    if len(parts) > 1:
        page_visit_id = parts[1]
    if len(parts) > 2:
        request_id = parts[2]

    now_ms = lambda: int(time.time() * 1_000)  # noqa: E731
    ts0 = timestamp_start or now_ms()
    ts1 = timestamp_end or now_ms()

    # Use C fast path if available (positional args for maximum speed)
    if _FAST_NET_AVAILABLE and _sffastnet and _FAST_NET_INITIALIZED:
        # Pass bytes directly for zero-copy access
        # Order: request_id, page_visit_id, recording_session_id, service_uuid,
        #        timestamp_start, timestamp_end, response_code, success,
        #        error, url, method, request_data(bytes), response_data(bytes),
        #        request_headers(bytes), response_headers(bytes)
        _sffastnet.network_request(
            request_id or "",
            page_visit_id or "",
            session_id or "",
            app_config._service_uuid or "",
            ts0,
            ts1,
            status_code,
            success,
            None if success else ((error or "")[:255]),
            url or "",
            method.upper(),
            request_data if isinstance(request_data, bytes) else b"",
            response_data if isinstance(response_data, bytes) else b"",
            request_headers if isinstance(request_headers, bytes) else b"",
            response_headers if isinstance(response_headers, bytes) else b"",
        )
    else:
        # Fallback to Python implementation (without request/response data for now)
        NetworkRequestTransmitter().do_send(
            (
                request_id,
                page_visit_id,
                session_id,
                None,  # service_uuid (set by transmitter middleware)
                ts0,
                ts1,
                status_code,
                success,
                None if success else (error or "")[:255],
                url,
                method.upper(),
            )
        )
