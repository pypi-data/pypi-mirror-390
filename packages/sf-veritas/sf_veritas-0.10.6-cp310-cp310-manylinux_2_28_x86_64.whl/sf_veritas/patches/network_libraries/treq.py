"""
Header propagation + network-recording patch for **Treq**.

• Propagates SAILFISH_TRACING_HEADER (unless excluded destination).
• Records every outbound request via record_network_request(…).

It also guarantees that Twisted's reactor is *running*:

1. Prefer installing the asyncio reactor early.
2. If a different reactor is already installed, start it in a background thread
   (if it isn't running yet), so Deferreds produced by treq will fire.
"""

from __future__ import annotations

import asyncio
import os
import threading
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

from ..constants import supported_network_verbs as verbs
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


def _ensure_reactor_running() -> None:
    """
    • Try to replace Twisted's default reactor with the asyncio one.
    • If that fails because a reactor is already installed, make sure the
      existing reactor is *running* (start it in a daemon thread if needed).

    NOTE: If the application has its own reactor startup logic, it should
    start the reactor BEFORE importing treq to avoid conflicts.
    """
    # Twisted import must be inside this function to avoid premature reactor load
    from twisted.internet import reactor

    # If reactor is already running, nothing to do
    if reactor.running:
        return

    try:
        from twisted.internet import asyncioreactor

        # Already an asyncio reactor? -> nothing to do
        if reactor.__class__.__module__ == "twisted.internet.asyncioreactor":
            return

        # Try upgrade to asyncio-reactor (will raise if another reactor in use)
        asyncioreactor.install(asyncio.get_event_loop())  # type: ignore[arg-type]
        return
    except Exception:
        # Could not swap reactors (already installed). Check if we need to start it.
        # Use a more robust check to avoid race conditions
        if not reactor.running and not getattr(reactor, "_started", False):

            def _safe_reactor_run():
                try:
                    reactor.run(installSignalHandlers=False)
                except Exception:
                    # Reactor already running (race condition) - silently ignore
                    pass

            threading.Thread(
                target=_safe_reactor_run,
                daemon=True,
            ).start()
            # Give reactor a moment to start

            time.sleep(0.01)


def patch_treq(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    try:
        # Ensure a live reactor *before* importing treq
        _ensure_reactor_running()

        import treq
    except ImportError:
        return  # treq is not installed; nothing to patch

    exclude = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(exclude)

    orig_request = treq.request

    # ------------------------------------------------------------------ #
    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        if HAS_WRAPT:

            def instrumented_request(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using inject_headers_ultrafast() via wrapt."""
                # args = (method, url, ...), kwargs = {...}
                url = args[1] if len(args) > 1 else kwargs.get("url", "")

                # Get or create headers dict
                hdrs = dict(kwargs.pop("headers", {}) or {})

                # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                inject_headers_ultrafast(hdrs, url, exclude)

                kwargs["headers"] = hdrs

                # Immediately call original and return - NO timing, NO capture!
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper("treq", "request", instrumented_request)
        else:
            # Fallback: Direct patching if wrapt not available
            def patched_request_fast(method: str, url: str, **kwargs):
                """Ultra-fast header injection without wrapt."""
                # Get or create headers dict
                hdrs = dict(kwargs.pop("headers", {}) or {})

                # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                inject_headers_ultrafast(hdrs, url, exclude)

                kwargs["headers"] = hdrs

                # Immediately call original and return - NO timing, NO capture!
                return orig_request(method, url, **kwargs)

            treq.request = patched_request_fast  # type: ignore[assignment]
    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        def patched_request(method: str, url: str, **kwargs):
            # -------- header injection
            hdrs = dict(kwargs.pop("headers", {}) or {})

            # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
            inject_headers_ultrafast(hdrs, url, exclude)

            kwargs["headers"] = hdrs

            # Get trace_id for capture
            trace_id = trace_id_ctx.get(None) or ""

            # Capture request data
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
                    req_headers = orjson.dumps({str(k): str(v) for k, v in hdrs.items()})
                else:
                    req_headers = json.dumps({str(k): str(v) for k, v in hdrs.items()}).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            t0 = int(time.time() * 1_000)
            d = orig_request(method, url, **kwargs)  # Deferred

            # -------- record on success
            def _ok(resp):
                status = getattr(resp, "code", 0)
                resp_headers = b""

                # Capture response headers
                try:
                    if HAS_ORJSON:
                        resp_headers = orjson.dumps(
                            dict(resp.headers.getAllRawHeaders())
                        )
                    else:
                        resp_headers = json.dumps(
                            dict(resp.headers.getAllRawHeaders())
                        ).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                # For treq, capturing response body is complex (async via Deferred)
                # We'll record without body to keep it simple and non-blocking
                # Only capture if LD_PRELOAD is NOT active (avoid duplicates)
                if not preload_active:
                    record_network_request(
                        trace_id,
                        url,
                        method.upper(),
                        status,
                        status < 400,
                        None,
                        timestamp_start=t0,
                        timestamp_end=int(time.time() * 1_000),
                        request_data=req_data,
                        request_headers=req_headers,
                        response_headers=resp_headers,
                    )
                return resp

            # -------- record on failure
            def _err(f):
                # Only capture if LD_PRELOAD is NOT active (avoid duplicates)
                if not preload_active:
                    record_network_request(
                        trace_id,
                        url,
                        method.upper(),
                        0,
                        False,
                        str(f.value)[:255],
                        timestamp_start=t0,
                        timestamp_end=int(time.time() * 1_000),
                        request_data=req_data,
                        request_headers=req_headers,
                    )
                return f

            d.addCallbacks(_ok, _err)
            return d

        treq.request = patched_request  # type: ignore[assignment]

    # Convenience verbs → reuse patched_request
    def _verb_factory(v: str):
        def _verb(url, **k):
            return treq.request(v.upper(), url, **k)

        _verb.__name__ = v
        return _verb

    for verb in verbs:
        setattr(treq, verb, _verb_factory(verb))
