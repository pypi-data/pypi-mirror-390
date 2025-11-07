import os
import threading
import time
from typing import List, Optional, Sequence, Tuple, Union

from ...thread_local import outbound_header_base_ctx, trace_id_ctx
from .utils import (
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


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active (same logic as http_client.py)."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


# ----------------------- Type/encoding helpers (FIX) -----------------------
def _normalize_url_to_str(val: Union[str, bytes, None]) -> Optional[str]:
    """Return URL as str for internal logic (trace/allow), safe-decoding bytes."""
    if val is None:
        return None
    if isinstance(val, bytes):
        try:
            return val.decode("utf-8", "replace")
        except Exception:
            return val.decode("latin1", "replace")
    return val  # already str


def _ensure_bytes(s: str) -> bytes:
    """Encode a str header safely to bytes (UTF-8)."""
    return s.encode("utf-8")


def _patch_pycurl_minimal_header_injection(pycurl_module):
    """
    MINIMAL header injection for pycurl in LD_PRELOAD mode.

    CRITICAL: We must patch pycurl even in LD_PRELOAD mode because pycurl
    builds the HTTP request in C before calling send(). Headers must be
    injected BEFORE serialization, not after.

    Uses a lightweight wrapper that only intercepts setopt/perform.
    All other methods delegate directly to wrapped C object.
    Target overhead: <20μs.
    """
    _OrigCurl = pycurl_module.Curl
    HTTPHEADER = pycurl_module.HTTPHEADER

    class CurlWrapper:
        """Lightweight wrapper - only intercepts setopt(HTTPHEADER) and perform()."""
        __slots__ = ('_curl', '_user_headers')

        def __init__(self, *args, **kwargs):
            # Create real Curl instance
            self._curl = _OrigCurl(*args, **kwargs)
            self._user_headers = None

        def setopt(self, opt, val):
            """Intercept HTTPHEADER, pass everything else through."""
            if opt == HTTPHEADER:
                # Store but don't call setopt yet (avoid double call)
                self._user_headers = val
                return
            # Direct delegation to C method
            return self._curl.setopt(opt, val)

        def perform(self):
            """Inject headers before perform."""
            base_dict = outbound_header_base_ctx.get()

            # Fast path: no sf-veritas headers
            if not base_dict:
                if self._user_headers is not None:
                    self._curl.setopt(HTTPHEADER, self._user_headers)
                return self._curl.perform()

            # Fast path: no user headers
            if self._user_headers is None:
                pycurl_headers = base_dict.get("_pycurl_headers")
                if pycurl_headers is None:
                    cached_headers = base_dict.get("_cached_headers")
                    if not cached_headers:
                        return self._curl.perform()
                    pycurl_headers = [f"{k}: {v}" for k, v in cached_headers.items()]
                    base_dict["_pycurl_headers"] = pycurl_headers

                self._curl.setopt(HTTPHEADER, pycurl_headers)
                return self._curl.perform()

            # Merge path
            cached_headers = base_dict.get("_cached_headers")
            if not cached_headers:
                self._curl.setopt(HTTPHEADER, self._user_headers)
                return self._curl.perform()

            if isinstance(self._user_headers[0], bytes):
                pycurl_headers_bytes = base_dict.get("_pycurl_headers_bytes")
                if pycurl_headers_bytes is None:
                    pycurl_headers_bytes = [f"{k}: {v}".encode('utf-8') for k, v in cached_headers.items()]
                    base_dict["_pycurl_headers_bytes"] = pycurl_headers_bytes
                merged = self._user_headers + pycurl_headers_bytes
            else:
                pycurl_headers = base_dict.get("_pycurl_headers")
                if pycurl_headers is None:
                    pycurl_headers = [f"{k}: {v}" for k, v in cached_headers.items()]
                    base_dict["_pycurl_headers"] = pycurl_headers
                merged = self._user_headers + pycurl_headers

            self._curl.setopt(HTTPHEADER, merged)
            return self._curl.perform()

        def __getattr__(self, name):
            """Delegate all other methods directly to wrapped Curl object."""
            return getattr(self._curl, name)

    # Replace Curl with wrapper factory
    pycurl_module.Curl = CurlWrapper


def _normalize_headers(
    base: Sequence[Union[str, bytes]],
    injected: Sequence[str],
) -> Tuple[Sequence[Union[str, bytes]], bool]:
    """
    Ensure we return a list where *all* items are the same type.
    - If user provided bytes headers, return bytes for *everything* (including injected).
    - If user provided str headers, return str for everything.
    - If no base headers, default to str.
    Returns: (normalized_headers, are_bytes)
    """
    are_bytes = False
    for h in base:
        if isinstance(h, bytes):
            are_bytes = True
            break

    if are_bytes:
        merged: List[bytes] = []
        # Copy original as bytes (already bytes)
        merged.extend([h if isinstance(h, bytes) else _ensure_bytes(h) for h in base])
        # Append injected as bytes
        merged.extend(_ensure_bytes(h) for h in injected)
        return merged, True
    else:
        merged2: List[str] = []
        # Copy original as str (decode if user passed bytes)
        for h in base:
            if isinstance(h, bytes):
                merged2.append(h.decode("utf-8", "replace"))
            else:
                merged2.append(h)
        # Append injected as str
        merged2.extend(injected)
        return merged2, False


def patch_pycurl(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    # Idempotency guard: prevent double-patching (handles forks, reloading)
    if is_already_patched("pycurl"):
        return
    mark_as_patched("pycurl")

    try:
        import pycurl
    except ImportError:
        return

    skip = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(skip)

    # CRITICAL: Even in LD_PRELOAD mode, we MUST patch pycurl!
    # Unlike curl-cffi (which goes through Python socket calls), pycurl builds
    # the entire HTTP request in C before calling send(). By then, headers are
    # already serialized in the buffer - too late to inject!
    #
    # Solution: Minimal patch that ONLY injects headers before pycurl serializes.
    # No capture, no tracking - just get headers from ContextVar and inject.
    if preload_active:
        return _patch_pycurl_minimal_header_injection(pycurl)

    _OrigCurl = pycurl.Curl

    class WrappedCurl(_OrigCurl):  # ➊ subclass libcurl handle
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._sf_url: Union[str, bytes, None] = None
            self._sf_method: Union[str, bytes, None] = None
            self._sf_headers: List[Union[str, bytes]] = []
            self._sf_request_body: bytes = b""
            self._sf_response_buffer: List[bytes] = []
            self._sf_original_writefunction = None
            self._sf_injected_headers: List[Union[str, bytes]] = (
                []
            )  # Track what we injected (normalized)
            self._sf_in_header_injection: bool = False  # Flag to prevent recursion

        # --- intercept option setting -------------------------------------------------
        def setopt(self, opt, val):
            if opt == pycurl.URL:
                self._sf_url = val  # may be bytes or str
                # Inject headers immediately after URL is set (needed for CurlMulti)
                self._inject_and_set_headers()
            elif opt == pycurl.CUSTOMREQUEST:
                self._sf_method = val  # may be bytes or str, normalize later
            elif opt == pycurl.HTTPHEADER:
                # User is setting headers - inject ours immediately
                # BUT if we're already inside _inject_and_set_headers, just pass through
                if self._sf_in_header_injection:
                    return super().setopt(opt, val)

                # Note: val should be a sequence of str or bytes (uniform)
                self._sf_headers = list(val)
                self._inject_and_set_headers()
                return  # Don't call super() - we already set them
            elif opt == pycurl.POSTFIELDS:
                # Capture request body for POST/PUT
                if isinstance(val, bytes):
                    self._sf_request_body = val
                elif isinstance(val, str):
                    self._sf_request_body = val.encode("utf-8")
            elif opt == pycurl.WRITEFUNCTION:
                # Store user's write function to call it later
                self._sf_original_writefunction = val
            return super().setopt(opt, val)

        def _inject_and_set_headers(self):
            """Build and set headers with our injected trace headers."""
            # If URL not set yet - just set user headers as-is (but keep uniform types)
            if self._sf_url is None:
                if self._sf_headers:
                    # still enforce uniformity to avoid mixed-type lists
                    normalized, _ = _normalize_headers(self._sf_headers, [])
                    self._sf_in_header_injection = True
                    try:
                        super().setopt(pycurl.HTTPHEADER, normalized)
                    finally:
                        self._sf_in_header_injection = False
                return

            url_str = _normalize_url_to_str(self._sf_url)

            # Use inject_headers_ultrafast to get headers as dict, then convert to pycurl format
            headers_dict = {}
            inject_headers_ultrafast(headers_dict, url_str or "", skip)

            # Convert dict headers to pycurl string format ["Name: Value"]
            injected: List[str] = []
            for key, value in headers_dict.items():
                injected.append(f"{key}: {value}")

            # --- FIX: enforce uniform header element type (all-str or all-bytes) ---
            merged, _ = _normalize_headers(self._sf_headers, injected)
            self._sf_injected_headers = list(merged)  # store exactly what we set

            # Apply merged headers using super().setopt with recursion guard
            self._sf_in_header_injection = True
            try:
                super().setopt(pycurl.HTTPHEADER, merged)
            finally:
                self._sf_in_header_injection = False

        # --- wrapped perform() --------------------------------------------------------
        def perform(self):
            # ULTRA-FAST PATH: LD_PRELOAD mode - headers already injected, skip all capture
            if preload_active:
                # Headers were already injected in _inject_and_set_headers()
                # C extension handles all capture - just perform!
                return super().perform()

            # SLOW PATH: Python-only mode - need full capture and recording
            url_for_trace = _normalize_url_to_str(self._sf_url) or ""
            # Normalize method for tracing/logging; don't mutate what's set in handle
            method_s: str
            if isinstance(self._sf_method, bytes):
                try:
                    method_s = self._sf_method.decode("utf-8", "replace").upper()
                except Exception:
                    method_s = "GET"
            elif isinstance(self._sf_method, str):
                method_s = self._sf_method.upper()
            else:
                method_s = "GET"

            # Use inject_headers_ultrafast to get headers as dict, then convert to pycurl format
            headers_dict = {}
            inject_headers_ultrafast(headers_dict, url_for_trace, skip)

            # Convert dict headers to pycurl string format ["Name: Value"]
            injected_now: List[str] = []
            for key, value in headers_dict.items():
                injected_now.append(f"{key}: {value}")

            # Get trace_id for capture
            trace_id = trace_id_ctx.get(None) or ""

            # --- FIX: ensure uniform header types again at perform-time --------------
            merged, _ = _normalize_headers(self._sf_headers, injected_now)

            # Capture request headers for recording (JSON bytes)
            req_headers = b""
            try:
                # If merged is bytes, decode elements for JSON; else use as-is
                hdrs_for_json = [
                    (
                        h.decode("utf-8", "replace")
                        if isinstance(h, (bytes, bytearray))
                        else h
                    )
                    for h in merged
                ]
                if HAS_ORJSON:
                    req_headers = orjson.dumps(hdrs_for_json)
                else:
                    req_headers = json.dumps(hdrs_for_json).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            # Let libcurl negotiate & decode encodings for us
            super().setopt(pycurl.ACCEPT_ENCODING, "")

            # Push merged headers down using recursion guard
            self._sf_in_header_injection = True
            try:
                super().setopt(pycurl.HTTPHEADER, merged)
            finally:
                self._sf_in_header_injection = False

            # Set up response capture - ALWAYS chain with user's writefunction if exists
            def capture_and_forward(data):
                """Capture response data and forward to user's writefunction if set."""
                self._sf_response_buffer.append(data)
                if self._sf_original_writefunction is not None:
                    # Call user's callback and return its result
                    return self._sf_original_writefunction(data)
                return len(data)

            super().setopt(pycurl.WRITEFUNCTION, capture_and_forward)

            # timing / status / error capture
            ts0 = int(time.time() * 1_000)
            status = 0
            err: Optional[str] = None
            resp_data = b""
            try:
                rv = super().perform()
                status = int(self.getinfo(pycurl.RESPONSE_CODE) or 0)

                # Collect response data - we always capture now
                resp_data = b"".join(self._sf_response_buffer)

                return rv
            except Exception as e:
                err = str(e)[:255]
                raise
            finally:
                ts1 = int(time.time() * 1_000)
                # Only capture if LD_PRELOAD is NOT active (avoid duplicates)
                if not preload_active:
                    record_network_request(
                        trace_id,
                        url_for_trace,
                        method_s,
                        status,
                        err is None,
                        err,
                        ts0,
                        ts1,
                        request_data=self._sf_request_body,
                        response_data=resp_data,
                        request_headers=req_headers,
                    )

    pycurl.Curl = WrappedCurl
