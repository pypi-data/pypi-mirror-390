"""
Monkey-patch Niquests using EVENT HOOKS for clean, maintainable instrumentation.

Uses niquests' built-in event hook system:
- pre_send: Inject headers before request transmission
- response: Consume body and track results after response

This approach is cleaner than wrapping every method and automatically
handles all sync request types (streaming/non-streaming).

NOTE: Async support is disabled for niquests.
"""

from __future__ import annotations

import os
import time
from typing import List, Optional

from ...thread_local import trace_id_ctx
from ..constants import supported_network_verbs as verbs
from .utils import (
    init_fast_header_check,
    inject_headers_ultrafast,
    record_network_request,
    track_request_result,
)

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def patch_niquests(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Patch niquests using event hooks for clean instrumentation.

    Registers hooks on Session (sync only) to:
    1. Inject tracing headers (pre_send hook)
    2. Consume response body and track results (response hook)

    When LD_PRELOAD is active: ULTRA-FAST path with <10ns overhead (header injection only).
    When LD_PRELOAD is NOT active: Full capture path with body/header recording.

    NOTE: AsyncSession is not patched - async support is disabled.
    """
    try:
        import niquests  # type: ignore
    except ImportError:
        return

    skip = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(skip)

    # ========================================================================
    # SYNC HOOKS (for Session)
    # ========================================================================

    def pre_send_hook(req, **kwargs):
        """
        Inject tracing headers before request transmission (sync).

        Called by niquests after connection selection, before sending.
        Modifies req.headers in-place.
        """
        url = str(req.url)
        headers = req.headers  # MutableMapping - modify in-place
        inject_headers_ultrafast(headers, url, skip)
        return req

    if preload_active:
        # LD_PRELOAD mode: Only inject headers, C extension handles capture
        def response_hook(resp, **kwargs):
            """Track request success/failure (LD_PRELOAD mode - sync)."""
            url = str(resp.url)
            try:
                # CRITICAL: Consume body to release connection
                # For sync Session, .content is a property (not coroutine)
                _ = resp.content
                track_request_result(success=True, url=url)
            except Exception as e:
                track_request_result(success=False, error=e, url=url)
            return resp

    else:
        # Python-only mode: Full capture (body + headers)
        def response_hook(resp, **kwargs):
            """Capture and record request (Python-only mode - sync)."""
            url = str(resp.url)
            method = resp.request.method
            t0 = int(time.time() * 1_000)

            trace_id = trace_id_ctx.get(None) or ""

            status = getattr(resp, "status_code", 0)
            success = False
            err = None
            req_data = b""
            resp_data = b""
            req_headers = b""
            resp_headers = b""

            try:
                # Capture response data
                resp_data = resp.content  # Also consumes body
                success = True

                # Capture headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps({str(k): str(v) for k, v in resp.request.headers.items()})
                    resp_headers = orjson.dumps({str(k): str(v) for k, v in resp.headers.items()})
                else:
                    req_headers = json.dumps({str(k): str(v) for k, v in resp.request.headers.items()}).encode("utf-8")
                    resp_headers = json.dumps({str(k): str(v) for k, v in resp.headers.items()}).encode("utf-8")

                # Capture request body if available
                if hasattr(resp.request, "body") and resp.request.body:
                    body = resp.request.body
                    if isinstance(body, bytes):
                        req_data = body
                    elif isinstance(body, str):
                        req_data = body.encode("utf-8")

                track_request_result(success=True, url=url)
            except Exception as exc:
                err = str(exc)[:255]
                track_request_result(success=False, error=exc, url=url)
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

            return resp

    # ========================================================================
    # PATCH Session.__init__ to register hooks
    # ========================================================================

    SessionCls = niquests.Session
    _original_session_init = SessionCls.__init__

    def patched_session_init(self, *args, **kwargs):
        _original_session_init(self, *args, **kwargs)
        # Register hooks on the session instance
        self.hooks["pre_send"].append(pre_send_hook)
        self.hooks["response"].append(response_hook)

    SessionCls.__init__ = patched_session_init

    # ========================================================================
    # PATCH module-level functions to pass hooks
    # ========================================================================

    # Module-level sync functions (niquests.get, niquests.post, etc.)
    # These create temporary sessions internally, so we wrap them to pass hooks

    _sync_hooks = {
        "pre_send": [pre_send_hook],
        "response": [response_hook],
    }

    def _wrap_module_sync(original_fn):
        """Wrap module-level sync functions to pass hooks."""

        def wrapper(*args, **kwargs):
            # Merge our hooks with any user-provided hooks
            user_hooks = kwargs.get("hooks") or {}
            merged_hooks = {}
            for hook_type in ["pre_send", "response"]:
                merged_hooks[hook_type] = _sync_hooks.get(
                    hook_type, []
                ) + user_hooks.get(hook_type, [])
            kwargs["hooks"] = merged_hooks
            return original_fn(*args, **kwargs)

        return wrapper

    # Patch module-level sync functions
    niquests.request = _wrap_module_sync(niquests.request)
    for verb in verbs:
        if hasattr(niquests, verb):
            setattr(niquests, verb, _wrap_module_sync(getattr(niquests, verb)))
