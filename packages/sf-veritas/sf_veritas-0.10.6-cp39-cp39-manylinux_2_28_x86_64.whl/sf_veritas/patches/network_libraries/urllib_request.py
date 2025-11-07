"""
Instrument urllib.request so that

• Every call to urlopen() or OpenerDirector.open() propagates
  SAILFISH tracing headers (unless destination host is excluded).
• Every call triggers record_network_request(…) UNLESS LD_PRELOAD is active.

The patch is safe to import multiple times.
"""

from __future__ import annotations

import io
import os
import time
from typing import List, Optional

from ...thread_local import trace_id_ctx

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

from .utils import (
    init_fast_header_check,
    inject_headers_ultrafast,
    record_network_request,
)

# ------------------------------- config / helpers --------------------------------- #

_SF_REQ_ALREADY_INJECTED_ATTR = "_sf_already_injected"
_SF_URLLIB_DEBUG = os.getenv("SF_URLLIB_DEBUG", "0") == "1"
# If true, honor urllib's env proxy logic; if false, we build a proxy-less opener for wire I/O.
trust_env = os.getenv("SF_URLLIB_TRUST_ENV", "false").lower() == "true"


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def _has_header_case_insensitive(req, name: str) -> bool:
    """True if Request already has a header named `name` (case-insensitive)."""
    try:
        items = req.header_items()  # type: ignore[attr-defined]
    except Exception:
        try:
            items = list(getattr(req, "headers", {}).items())
        except Exception:
            items = []
    lname = name.lower()
    for k, _ in items:
        if str(k).lower() == lname:
            return True
    return False


class _ResponseTee:
    """
    File-like wrapper for urllib responses that tees bytes into an internal buffer
    as the caller consumes them. On EOF/close, invokes on_complete(buffer_bytes).
    """

    __slots__ = ("_resp", "_buf", "_cap", "_done", "_on_complete", "_truncated")

    def __init__(self, resp, on_complete, cap_bytes: int = 256 * 1024):
        self._resp = resp
        self._buf = io.BytesIO()
        self._cap = cap_bytes
        self._done = False
        self._truncated = False
        self._on_complete = on_complete

    # -------- helpers --------
    def _accumulate(self, chunk: bytes) -> None:
        if not chunk:
            return
        if self._buf.tell() < self._cap:
            remaining = self._cap - self._buf.tell()
            if len(chunk) > remaining:
                self._buf.write(chunk[:remaining])
                self._truncated = True
            else:
                self._buf.write(chunk)

    def _finish_if_needed(self, reached_eof: bool) -> None:
        if reached_eof and not self._done:
            self._done = True
            try:
                payload = self._buf.getvalue()
                self._on_complete(payload, self._truncated)
            finally:
                self._buf.close()

    # -------- file-like API --------
    def read(self, size: int = -1) -> bytes:
        data = self._resp.read(size)
        self._accumulate(data)
        self._finish_if_needed(reached_eof=(not data))
        return data

    def readinto(self, b) -> int:
        n = self._resp.readinto(b)
        if n and n > 0:
            self._accumulate(memoryview(b)[:n].tobytes())
        self._finish_if_needed(reached_eof=(n == 0))
        return n

    def readline(self, size: int = -1) -> bytes:
        line = self._resp.readline(size)
        self._accumulate(line)
        self._finish_if_needed(reached_eof=(line == b""))
        return line

    def __iter__(self):
        for line in self._resp:
            self._accumulate(line)
            yield line
        self._finish_if_needed(reached_eof=True)

    def close(self):
        try:
            self._resp.close()
        finally:
            self._finish_if_needed(reached_eof=True)

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol."""
        self.close()
        return False

    def __getattr__(self, name):
        return getattr(self._resp, name)


# ------------------------------- patcher --------------------------------- #


def patch_urllib_request(
    domains_to_not_propagate_headers_to: Optional[List[str]] = None,
) -> None:
    """
    Apply patches. When LD_PRELOAD is active:
    - ALWAYS inject headers (trace_id + funcspan_override)
    - SKIP capture/emission (LD_PRELOAD handles at socket layer)
    """
    try:
        import socket as _socket  # for _GLOBAL_DEFAULT_TIMEOUT
        import urllib.error
        import urllib.request as _ur
    except ImportError:
        return

    exclude: List[str] = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension fast check once when LD_PRELOAD is active
    if preload_active:
        init_fast_header_check(exclude)

    _orig_urlopen = _ur.urlopen
    _orig_opener_open = _ur.OpenerDirector.open  # type: ignore[attr-defined]

    # -------- internal helpers (no recursion!) --------

    def _ensure_content_length_semantics(req: _ur.Request) -> None:
        """
        Guarantee standards-compliant body semantics:

        - For POST/PUT/PATCH/DELETE/OPTIONS with no body: send Content-Length: 0
        - For HEAD: no body
        - Also ensure a benign Content-Type for zero-length bodies on body-capable verbs.
        Some stacks 400 when Content-Type is missing on e.g. PUT with empty body.
        """
        method = req.get_method()

        if method == "HEAD":
            # HEAD must not have a body.
            return

        body_capable = {"POST", "PUT", "PATCH", "DELETE", "OPTIONS"}

        if method in body_capable:
            has_body = getattr(req, "data", None) is not None

            if not has_body:
                # Prefer setting an empty body so urllib emits Content-Length: 0.
                try:
                    req.data = b""
                    has_body = True
                except Exception:
                    # Fallback to explicit header only.
                    if not _has_header_case_insensitive(req, "Content-Length"):
                        try:
                            req.add_header("Content-Length", "0")
                        except Exception:
                            pass

            # Make sure a benign Content-Type exists for empty bodies on these verbs.
            # urllib adds a default Content-Type for POST, but not always for others.
            if not _has_header_case_insensitive(req, "Content-Type"):
                try:
                    # Use application/octet-stream to avoid implying form encoding.
                    req.add_header("Content-Type", "application/octet-stream")
                except Exception:
                    pass

    def _maybe_inject_headers(req: _ur.Request) -> None:
        if getattr(req, _SF_REQ_ALREADY_INJECTED_ATTR, False):
            return
        headers_dict = dict(req.headers)
        inject_headers_ultrafast(headers_dict, req.full_url, exclude)
        for k, v in headers_dict.items():
            if not _has_header_case_insensitive(req, k):
                req.add_header(k, v)
        setattr(req, _SF_REQ_ALREADY_INJECTED_ATTR, True)

    def _proxyless_open(req: _ur.Request, timeout):
        """Open using a proxy-less opener, calling the ORIGINAL .open to avoid re-entry."""
        if trust_env:
            # Honor env proxies/config via the original urlopen
            return _orig_urlopen(req, timeout=timeout)
        opener = _ur.build_opener(_ur.ProxyHandler({}))
        return _orig_opener_open(opener, req, timeout=timeout)

    # ------------------------------------------------------------------ #
    # Core helper used by both urlopen and OpenerDirector.open
    # ------------------------------------------------------------------ #
    def _inject_and_record(
        opener_call,  # callable(req, timeout=?)
        req_or_url,
        data,
        timeout,
    ):
        # 1) Normalize to a Request object (no duplicate 'data' passing later)
        if isinstance(req_or_url, _ur.Request):
            req = req_or_url
        else:
            req = _ur.Request(req_or_url, data=data)

        # 2) Header injection + body semantics (single pass)
        _maybe_inject_headers(req)
        _ensure_content_length_semantics(req)
        method = req.get_method()

        # 3) Trace id for capture (skip when LD_PRELOAD active)
        if not preload_active:
            trace_id = trace_id_ctx.get(None) or ""
        else:
            trace_id = ""

        # 4) Serialize request headers/data for capture
        req_data = b""
        req_headers = b""
        try:
            if getattr(req, "data", None):
                if isinstance(req.data, bytes):
                    req_data = req.data
                elif isinstance(req.data, str):
                    req_data = req.data.encode("utf-8")
            if HAS_ORJSON:
                req_headers = orjson.dumps({str(k): str(v) for k, v in req.headers.items()})
            else:
                req_headers = json.dumps({str(k): str(v) for k, v in req.headers.items()}).encode("utf-8")
        except Exception:
            pass

        # 5) Perform I/O
        t0 = int(time.time() * 1_000)
        try:
            resp = opener_call(req, timeout=timeout)
            status = (
                getattr(resp, "status", None) or getattr(resp, "getcode", lambda: 0)()
            )
            success = status < 400

            if _SF_URLLIB_DEBUG:
                try:
                    print(
                        f"[SF urllib] {method} {req.full_url} -> {status}", flush=True
                    )
                except Exception:
                    pass

            if HAS_ORJSON:
                resp_headers = orjson.dumps({str(k): str(v) for k, v in resp.headers.items()})
            else:
                resp_headers = json.dumps({str(k): str(v) for k, v in resp.headers.items()}).encode("utf-8")

            if preload_active:
                return resp

            def _on_complete(resp_bytes: bytes, _truncated: bool):
                record_network_request(
                    trace_id,
                    req.full_url,
                    method,
                    status,
                    success,
                    None,
                    timestamp_start=t0,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    response_data=resp_bytes,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

            cap = int(os.getenv("SF_URLOPEN_CAPTURE_CAP_BYTES", "262144"))
            return _ResponseTee(resp, _on_complete, cap_bytes=cap)

        except urllib.error.HTTPError as e:
            # 4xx/5xx → exception; capture and re-raise
            if _SF_URLLIB_DEBUG:
                try:
                    print(
                        f"[SF urllib] {req.get_method()} {req.full_url} -> {getattr(e, 'code', 0)} (HTTPError)",
                        flush=True,
                    )
                except Exception:
                    pass

            if HAS_ORJSON:
                resp_headers = orjson.dumps({str(k): str(v) for k, v in e.headers.items()})
            else:
                resp_headers = json.dumps({str(k): str(v) for k, v in e.headers.items()}).encode("utf-8")

            if not preload_active:
                body = b""
                try:
                    cap = int(os.getenv("SF_URLOPEN_CAPTURE_CAP_BYTES", "262144"))
                    body = e.read()
                    if len(body) > cap:
                        body = body[:cap]
                    # Put body back so downstream can still read it
                    e.fp = io.BytesIO(body)
                except Exception:
                    pass

                record_network_request(
                    trace_id,
                    req.full_url,
                    req.get_method(),
                    getattr(e, "code", 0) or 0,
                    False,
                    str(e),
                    timestamp_start=t0,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    response_data=body,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )
            raise

        except Exception as e:
            if _SF_URLLIB_DEBUG:
                try:
                    print(
                        f"[SF urllib] {req.get_method()} {req.full_url} -> exception: {e}",
                        flush=True,
                    )
                except Exception:
                    pass
            if not preload_active:
                record_network_request(
                    trace_id,
                    req.full_url,
                    req.get_method(),
                    0,
                    False,
                    str(e)[:255],
                    timestamp_start=t0,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    request_headers=req_headers,
                )
            raise

    # ------------------------------------------------------------------ #
    # Module-level urlopen patch
    # ------------------------------------------------------------------ #
    if HAS_WRAPT:

        def instrumented_urlopen(wrapped, instance, args, kwargs):
            # urlopen(url, data=None, timeout=..., *, cafile=..., capath=..., cadefault=..., context=...)
            url = args[0] if len(args) > 0 else kwargs.pop("url", "")
            data = args[1] if len(args) > 1 else kwargs.pop("data", None)

            if len(args) > 2:
                timeout = args[2]
            else:
                timeout = kwargs.pop("timeout", _ur.socket._GLOBAL_DEFAULT_TIMEOUT)  # type: ignore

            # We pass a callable that avoids proxies unless trust_env is set
            return _inject_and_record(_proxyless_open, url, data, timeout)

        wrapt.wrap_function_wrapper("urllib.request", "urlopen", instrumented_urlopen)
    else:

        def patched_urlopen(url, data=None, timeout=None, *a, **kw):  # type: ignore
            if "timeout" in kw:
                timeout = kw.pop("timeout")
            if "data" in kw:
                data = kw.pop("data")
            return _inject_and_record(_proxyless_open, url, data, timeout)

        _ur.urlopen = patched_urlopen  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # OpenerDirector.open patch (covers build_opener, install_opener, etc.)
    # ------------------------------------------------------------------ #
    if HAS_WRAPT:

        def instrumented_opener_open(wrapped, instance, args, kwargs):
            # Signature: open(self, fullurl, data=None, timeout=None)
            fullurl = args[0] if len(args) > 0 else kwargs.pop("fullurl", "")
            data = args[1] if len(args) > 1 else kwargs.pop("data", None)
            timeout = args[2] if len(args) > 2 else kwargs.pop("timeout", None)

            # If caller passed a Request that we already injected, short-circuit:
            if isinstance(fullurl, _ur.Request) and getattr(
                fullurl, _SF_REQ_ALREADY_INJECTED_ATTR, False
            ):
                if trust_env:
                    # Delegate to wrapped opener respecting env/proxies
                    return wrapped(fullurl, timeout=timeout)
                # Use proxy-less opener BUT call the ORIGINAL .open to avoid re-entry
                opener = _ur.build_opener(_ur.ProxyHandler({}))
                return _orig_opener_open(opener, fullurl, timeout=timeout)

            # Otherwise, flow through our injector and open without proxies (by default)
            return _inject_and_record(_proxyless_open, fullurl, data, timeout)

        wrapt.wrap_function_wrapper(
            _ur.OpenerDirector, "open", instrumented_opener_open
        )
    else:

        def patched_opener_open(self, fullurl, data=None, timeout=None, *a, **kw):  # type: ignore[override]
            if "timeout" in kw:
                timeout = kw.pop("timeout")
            if "data" in kw:
                data = kw.pop("data")

            if isinstance(fullurl, _ur.Request) and getattr(
                fullurl, _SF_REQ_ALREADY_INJECTED_ATTR, False
            ):
                if trust_env:
                    return _orig_opener_open(self, fullurl, timeout=timeout)
                opener = _ur.build_opener(_ur.ProxyHandler({}))
                return _orig_opener_open(opener, fullurl, timeout=timeout)

            return _inject_and_record(_proxyless_open, fullurl, data, timeout)

        _ur.OpenerDirector.open = patched_opener_open  # type: ignore[assignment]
