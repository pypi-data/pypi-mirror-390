"""
Monkey-patch Tornado's HTTP clients so that

• Every outbound request carries SAILFISH_TRACING_HEADER
  (unless the destination host is excluded).
• Every request – success or failure – triggers record_network_request(…).

Covers
  • tornado.httpclient.AsyncHTTPClient.fetch   (await-able)
  • tornado.httpclient.HTTPClient.fetch        (blocking/sync)
Safe to call repeatedly; patches only once per process.
"""

from __future__ import annotations

import os
import time
from typing import List, Optional, Tuple

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


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active (same logic as http_client.py)."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def patch_tornado(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    try:
        # Tornado is optional; exit silently if missing
        from tornado.httpclient import AsyncHTTPClient, HTTPClient, HTTPRequest
    except ImportError:
        return

    exclude: List[str] = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(exclude)

    # ------------------------------------------------------------------ #
    # Helpers shared by sync & async wrappers
    # ------------------------------------------------------------------ #
    def _resolve(
        req_or_url, kwargs
    ) -> Tuple[str, str, dict]:  # → (url, METHOD, headers_dict)
        """
        Handle both call styles:

            client.fetch("https://foo", method="POST", headers={...})
            client.fetch(HTTPRequest(...))

        Always returns a mutable *headers* dict.
        """
        if isinstance(req_or_url, HTTPRequest):
            url = req_or_url.url
            method = (req_or_url.method or "GET").upper()
            hdrs = dict(req_or_url.headers or {})
        else:
            url = str(req_or_url)
            method = kwargs.get("method", "GET").upper()
            hdrs = dict(kwargs.get("headers", {}) or {})
        return url, method, hdrs

    def _inject(
        req_or_url, kwargs, hdrs: dict
    ):  # mutate request object *or* kwargs to carry hdrs
        if isinstance(req_or_url, HTTPRequest):
            req_or_url.headers = hdrs
        else:
            kwargs["headers"] = hdrs
        return req_or_url, kwargs

    # Unified _prepare function for both fast and slow paths
    def _prepare(url: str, hdrs: dict):
        """Return (trace_id, merged_headers, start_ms). Ultra-fast header injection."""
        # Make a copy for mutation
        out = dict(hdrs)

        # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
        inject_headers_ultrafast(out, url, exclude)

        # Get trace_id for capture (only used in slow path)
        if not preload_active:
            trace_id = trace_id_ctx.get(None) or ""
        else:
            trace_id = ""  # Not needed for fast path

        return trace_id, out, int(time.time() * 1_000)

    # ------------------------------------------------------------------ #
    # AsyncHTTPClient.fetch wrapper
    # ------------------------------------------------------------------ #
    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:
            # FASTEST: Use wrapt directly (OTEL-style for minimal overhead)
            async def instrumented_async_fetch(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using C extension via wrapt."""
                req_or_url = args[0] if len(args) > 0 else kwargs.get("request", "")
                url, method, hdrs_cur = _resolve(req_or_url, kwargs)
                trace_id, hdrs_new, t0 = _prepare(url, hdrs_cur)

                # Inject headers back into args/kwargs
                if len(args) > 0:
                    args = (_inject(args[0], kwargs, hdrs_new)[0],) + args[1:]
                else:
                    req_or_url, kwargs = _inject(req_or_url, kwargs, hdrs_new)

                # NO capture, NO timing, NO record - immediate return!
                return await wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "tornado.httpclient", "AsyncHTTPClient.fetch", instrumented_async_fetch
            )
        else:
            # Fallback: Direct patching if wrapt not available
            original_async_fetch = AsyncHTTPClient.fetch

            async def patched_async_fetch(self, req_or_url, *args, **kwargs):
                url, method, hdrs_cur = _resolve(req_or_url, kwargs)
                trace_id, hdrs_new, t0 = _prepare(url, hdrs_cur)
                req_or_url, kwargs = _inject(req_or_url, kwargs, hdrs_new)

                # NO capture, NO timing, NO record - immediate return!
                return await original_async_fetch(self, req_or_url, *args, **kwargs)

            AsyncHTTPClient.fetch = patched_async_fetch  # type: ignore[assignment]

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        async def patched_async_fetch(self, req_or_url, *args, **kwargs):
            url, method, hdrs_cur = _resolve(req_or_url, kwargs)
            trace_id, hdrs_new, t0 = _prepare(url, hdrs_cur)
            req_or_url, kwargs = _inject(req_or_url, kwargs, hdrs_new)

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                body = None
                if isinstance(req_or_url, HTTPRequest):
                    body = req_or_url.body
                else:
                    body = kwargs.get("body")

                if body:
                    if isinstance(body, bytes):
                        req_data = body
                    elif isinstance(body, str):
                        req_data = body.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps({str(k): str(v) for k, v in hdrs_new.items()})
                else:
                    req_headers = json.dumps({str(k): str(v) for k, v in hdrs_new.items()}).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            status, success, err = 0, False, None
            resp_data = b""
            resp_headers = b""
            try:
                resp = await original_async_fetch(self, req_or_url, *args, **kwargs)
                status = getattr(resp, "code", 0)
                success = status < 400

                # Capture response data
                try:
                    resp_data = getattr(resp, "body", b"")
                    # Capture response headers
                    if HAS_ORJSON:
                        resp_headers = orjson.dumps({str(k): str(v) for k, v in resp.headers.items()})
                    else:
                        resp_headers = json.dumps({str(k): str(v) for k, v in resp.headers.items()}).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                return resp
            except Exception as exc:  # noqa: BLE001
                err = str(exc)[:255]
                raise
            finally:
                record_network_request(
                    trace_id,
                    url,
                    method,
                    status,
                    success,
                    err,
                    timestamp_start=t0,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    response_data=resp_data,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

        if not HAS_WRAPT:
            AsyncHTTPClient.fetch = patched_async_fetch  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # HTTPClient.fetch wrapper (blocking)
    # ------------------------------------------------------------------ #
    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:
            # FASTEST: Use wrapt directly (OTEL-style for minimal overhead)
            def instrumented_sync_fetch(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using C extension via wrapt."""
                req_or_url = args[0] if len(args) > 0 else kwargs.get("request", "")
                url, method, hdrs_cur = _resolve(req_or_url, kwargs)
                trace_id, hdrs_new, t0 = _prepare(url, hdrs_cur)

                # Inject headers back into args/kwargs
                if len(args) > 0:
                    args = (_inject(args[0], kwargs, hdrs_new)[0],) + args[1:]
                else:
                    req_or_url, kwargs = _inject(req_or_url, kwargs, hdrs_new)

                # NO capture, NO timing, NO record - immediate return!
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "tornado.httpclient", "HTTPClient.fetch", instrumented_sync_fetch
            )
        else:
            # Fallback: Direct patching if wrapt not available
            original_sync_fetch = HTTPClient.fetch

            def patched_sync_fetch(self, req_or_url, *args, **kwargs):
                url, method, hdrs_cur = _resolve(req_or_url, kwargs)
                trace_id, hdrs_new, t0 = _prepare(url, hdrs_cur)
                req_or_url, kwargs = _inject(req_or_url, kwargs, hdrs_new)

                # NO capture, NO timing, NO record - immediate return!
                return original_sync_fetch(self, req_or_url, *args, **kwargs)

            HTTPClient.fetch = patched_sync_fetch  # type: ignore[assignment]

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        def patched_sync_fetch(self, req_or_url, *args, **kwargs):
            url, method, hdrs_cur = _resolve(req_or_url, kwargs)
            trace_id, hdrs_new, t0 = _prepare(url, hdrs_cur)
            req_or_url, kwargs = _inject(req_or_url, kwargs, hdrs_new)

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                body = None
                if isinstance(req_or_url, HTTPRequest):
                    body = req_or_url.body
                else:
                    body = kwargs.get("body")

                if body:
                    if isinstance(body, bytes):
                        req_data = body
                    elif isinstance(body, str):
                        req_data = body.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps({str(k): str(v) for k, v in hdrs_new.items()})
                else:
                    req_headers = json.dumps({str(k): str(v) for k, v in hdrs_new.items()}).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            status, success, err = 0, False, None
            resp_data = b""
            resp_headers = b""
            try:
                resp = original_sync_fetch(self, req_or_url, *args, **kwargs)
                status = getattr(resp, "code", 0)
                success = status < 400

                # Capture response data
                try:
                    resp_data = getattr(resp, "body", b"")
                    # Capture response headers
                    if HAS_ORJSON:
                        resp_headers = orjson.dumps({str(k): str(v) for k, v in resp.headers.items()})
                    else:
                        resp_headers = json.dumps({str(k): str(v) for k, v in resp.headers.items()}).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                return resp
            except Exception as exc:  # noqa: BLE001
                err = str(exc)[:255]
                raise
            finally:
                record_network_request(
                    trace_id,
                    url,
                    method,
                    status,
                    success,
                    err,
                    timestamp_start=t0,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    response_data=resp_data,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

        if not HAS_WRAPT:
            HTTPClient.fetch = patched_sync_fetch  # type: ignore[assignment]
