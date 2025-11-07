import os
import time
from typing import List, Optional

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

import threading

from ...thread_local import get_or_set_sf_trace_id, trace_id_ctx
from ..constants import supported_network_verbs as verbs
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


def _capture_and_record_curl_cffi(
    resp,
    trace_id,
    url,
    method,
    status,
    ok,
    start,
    end,
    req_data,
    req_headers,
    preload_active,
):
    """Capture response data in background thread AFTER response is returned to user."""
    resp_data = b""
    resp_headers = b""
    error = None

    try:
        # Capture response body
        try:
            resp_data = getattr(resp, "content", b"")
        except Exception:  # noqa: BLE001
            pass

        # Capture response headers
        if HAS_ORJSON:
            resp_headers = orjson.dumps({str(k): str(v) for k, v in resp.headers.items()})
        else:
            resp_headers = json.dumps({str(k): str(v) for k, v in resp.headers.items()}).encode("utf-8")

        if not ok and not error:
            try:
                error = getattr(resp, "text", str(resp))[:255]
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass

    # Only capture if LD_PRELOAD is NOT active (avoid duplicates)
    if not preload_active:
        record_network_request(
            trace_id,
            url,
            method,
            status,
            ok,
            error,
            timestamp_start=start,
            timestamp_end=end,
            request_data=req_data,
            response_data=resp_data,
            request_headers=req_headers,
            response_headers=resp_headers,
        )


def patch_curl_cffi(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Monkey-patch curl_cffi.requests so that EVERY HTTP verb
    injects SAILFISH_TRACING_HEADER (when allowed) and then records the request.

    When LD_PRELOAD is active: ULTRA-FAST path with <10ns overhead (header injection only).
    When LD_PRELOAD is NOT active: Full capture path with body/header recording.
    """
    try:
        import curl_cffi.requests as ccr
    except ImportError:
        return

    skip = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(skip)

    # Preserve original references before any patching
    orig_request = getattr(ccr, "request", None)
    orig_session_request = None
    orig_async_session_request = None

    Session = getattr(ccr, "Session", None)
    AsyncSession = getattr(ccr, "AsyncSession", None)
    if Session:
        orig_session_request = getattr(Session, "request", None)
    if AsyncSession:
        orig_async_session_request = getattr(AsyncSession, "request", None)

    if preload_active:
        # ========== ULTRA-FAST PATH: When LD_PRELOAD is active ==========
        # Uses C extension for <10ns overhead (15ns empty list, 25ns with filtering)
        if HAS_WRAPT:
            # FASTEST: Use wrapt for ultra-low overhead
            def make_instrumented(verb_name):
                """Create a wrapt instrumented function for the given verb."""

                def instrumented(wrapped, instance, args, kwargs):
                    """Ultra-fast header injection using C extension via wrapt."""
                    # OPTIMIZED: Simplified URL extraction (prioritize kwargs, then positional args)
                    url = kwargs.get("url")
                    if not url and args:
                        # request(method, url) or get(url) - URL is typically first or second arg
                        url = (
                            args[1]
                            if verb_name == "request" and len(args) >= 2
                            else (args[0] if args else "")
                        )

                    # OPTIMIZED: Pre-allocate headers dict (use or-pattern for None)
                    headers = kwargs.get("headers") or {}
                    kwargs["headers"] = headers

                    # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                    inject_headers_ultrafast(headers, url or "", skip)

                    # Immediately call original and return - NO timing, NO threads, NO capture!
                    return wrapped(*args, **kwargs)

                return instrumented

        else:
            # Fallback: Direct patching if wrapt not available
            def make_fast_wrapper(orig_fn, verb_name):
                def fast_wrapper(*args, **kwargs):
                    # OPTIMIZED: Simplified URL extraction (same as wrapt path)
                    url = kwargs.get("url")
                    if not url and args:
                        url = (
                            args[1]
                            if verb_name == "request" and len(args) >= 2
                            else (args[0] if args else "")
                        )

                    # OPTIMIZED: Pre-allocate headers dict (use or-pattern for None)
                    headers = kwargs.get("headers") or {}
                    kwargs["headers"] = headers

                    # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                    inject_headers_ultrafast(headers, url or "", skip)

                    # Immediately call original and return - NO timing, NO threads, NO capture!
                    return orig_fn(*args, **kwargs)

                return fast_wrapper

    else:
        # ========== FULL CAPTURE PATH: When LD_PRELOAD is NOT active ==========
        # Full Python-level capture with body/header recording
        def make_fast_wrapper(orig_fn, verb_name):
            def wrapper(*args, **kwargs):
                # 1) Determine HTTP method and URL safely
                if verb_name == "request":
                    # support both request(url) and request(method, url, …)
                    if len(args) == 1 and isinstance(args[0], str):
                        method, url = "GET", args[0]
                    elif len(args) >= 2 and isinstance(args[0], str):
                        method, url = args[0].upper(), args[1]
                    elif len(args) >= 3:
                        # bound Session.request(self, method, url, …)
                        method, url = args[1].upper(), args[2]
                    else:
                        method = kwargs.get("method", "").upper()
                        url = kwargs.get("url", "")
                else:
                    method = verb_name.upper()
                    # for module-level: args[0] == url
                    # for bound: args[1] == url
                    if len(args) >= 1 and isinstance(args[0], str):
                        url = args[0]
                    elif len(args) >= 2:
                        url = args[1]
                    else:
                        url = kwargs.get("url", "")

                # 2) Header injection
                headers = kwargs.get("headers", {}) or {}

                # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                inject_headers_ultrafast(headers, url, skip)

                kwargs["headers"] = headers

                # Get trace_id for capture
                trace_id = trace_id_ctx.get(None) or ""

                # Capture request data as bytes
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
                    elif "content" in kwargs:
                        content = kwargs["content"]
                        if isinstance(content, bytes):
                            req_data = content
                        elif isinstance(content, str):
                            req_data = content.encode("utf-8")

                    # Capture request headers
                    if HAS_ORJSON:
                        req_headers = orjson.dumps({str(k): str(v) for k, v in headers.items()})
                    else:
                        req_headers = json.dumps({str(k): str(v) for k, v in headers.items()}).encode("utf-8")
                except Exception:  # noqa: BLE001
                    pass

                # 3) Perform the real call
                start = int(time.time() * 1_000)
                resp = orig_fn(*args, **kwargs)
                end = int(time.time() * 1_000)

                # 4) Get status immediately, but DEFER body/header capture
                status = getattr(resp, "status_code", None) or getattr(
                    resp, "status", 0
                )
                ok = getattr(resp, "ok", status < 400)

                # Schedule deferred capture in background thread
                threading.Thread(
                    target=_capture_and_record_curl_cffi,
                    args=(
                        resp,
                        trace_id,
                        url,
                        method,
                        status,
                        ok,
                        start,
                        end,
                        req_data,
                        req_headers,
                        False,
                    ),
                    daemon=True,
                ).start()

                # CRITICAL: Return response immediately without blocking!
                return resp

            return wrapper

    # Patch module-level verbs
    if HAS_WRAPT and preload_active:
        # Use wrapt for ultra-low overhead when LD_PRELOAD is active
        for verb in verbs:
            if getattr(ccr, verb, None):
                wrapt.wrap_function_wrapper(ccr, verb, make_instrumented(verb))

        # Patch module-level "request" method (not in standard verbs list)
        if orig_request:
            wrapt.wrap_function_wrapper(ccr, "request", make_instrumented("request"))

        # Patch Session methods
        if Session:
            for verb in verbs:
                if getattr(Session, verb, None):
                    wrapt.wrap_function_wrapper(Session, verb, make_instrumented(verb))
            # Also patch "request" method with preserved original
            if orig_session_request:
                wrapt.wrap_function_wrapper(
                    Session, "request", make_instrumented("request")
                )

        # Patch AsyncSession methods
        if AsyncSession:
            for verb in verbs:
                if getattr(AsyncSession, verb, None):
                    wrapt.wrap_function_wrapper(
                        AsyncSession, verb, make_instrumented(verb)
                    )
            # Also patch "request" method with preserved original
            if orig_async_session_request:
                wrapt.wrap_function_wrapper(
                    AsyncSession, "request", make_instrumented("request")
                )
    else:
        # Fallback: Direct patching
        for verb in verbs:
            orig = getattr(ccr, verb, None)
            if orig:
                setattr(ccr, verb, make_fast_wrapper(orig, verb))

        # Patch module-level "request" method (not in standard verbs list)
        if orig_request:
            setattr(ccr, "request", make_fast_wrapper(orig_request, "request"))

        # Patch Session methods
        if Session:
            for verb in verbs:
                orig = getattr(Session, verb, None)
                if orig:
                    setattr(Session, verb, make_fast_wrapper(orig, verb))
            # Also patch "request" method with preserved original
            if orig_session_request:
                setattr(
                    Session,
                    "request",
                    make_fast_wrapper(orig_session_request, "request"),
                )

        # Patch AsyncSession methods
        if AsyncSession:
            for verb in verbs:
                orig = getattr(AsyncSession, verb, None)
                if orig:
                    setattr(AsyncSession, verb, make_fast_wrapper(orig, verb))
            # Also patch "request" method with preserved original
            if orig_async_session_request:
                setattr(
                    AsyncSession,
                    "request",
                    make_fast_wrapper(orig_async_session_request, "request"),
                )
