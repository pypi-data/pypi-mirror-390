"""
• SFTracingFalconMiddleware  – propagates SAILFISH_TRACING_HEADER → ContextVar.
• per-responder wrapper      – emits ONE NetworkHop per request for
  user-land Falcon responders (sync & async), skipping Strawberry.
• patch_falcon()             – monkey-patches both falcon.App (WSGI) and
  falcon.asgi.App (ASGI) so the above logic is automatic.

This patch adds <1 µs overhead per request on CPython 3.11.
"""

from __future__ import annotations

import functools
import inspect
from types import MethodType
from typing import Any, Callable, List, Optional, Set, Tuple

from ... import _sffuncspan_config, app_config
from ...constants import (
    FUNCSPAN_OVERRIDE_HEADER_BYTES,
    SAILFISH_TRACING_HEADER,
    SAILFISH_TRACING_HEADER_BYTES,
)
from ...custom_excepthook import custom_excepthook
from ...env_vars import (
    SF_DEBUG,
    SF_NETWORKHOP_CAPTURE_REQUEST_BODY,
    SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS,
    SF_NETWORKHOP_CAPTURE_RESPONSE_BODY,
    SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS,
    SF_NETWORKHOP_REQUEST_LIMIT_MB,
    SF_NETWORKHOP_RESPONSE_LIMIT_MB,
)
from ...fast_network_hop import fast_send_network_hop_fast, register_endpoint
from ...thread_local import (
    clear_c_tls_parent_trace_id,
    clear_current_request_path,
    clear_outbound_header_base,
    clear_trace_id,
    generate_new_trace_id,
    get_or_set_sf_trace_id,
    get_sf_trace_id,
    set_current_request_path,
    set_funcspan_override,
    set_outbound_header_base,
)
from .utils import _is_user_code, _unwrap_user_func, should_skip_route  # shared helpers

# Size limits in bytes
_REQUEST_LIMIT_BYTES = SF_NETWORKHOP_REQUEST_LIMIT_MB * 1024 * 1024
_RESPONSE_LIMIT_BYTES = SF_NETWORKHOP_RESPONSE_LIMIT_MB * 1024 * 1024

# Pre-registered endpoint IDs
_ENDPOINT_REGISTRY: dict[tuple, int] = {}

# Module-level variable for routes to skip (set by patch_falcon)
_ROUTES_TO_SKIP = []

# Map resource instances to their route patterns
_RESOURCE_ROUTES: dict[int, str] = {}

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False

# ---------------------------------------------------------------------------
# 1 | Context-propagation middleware
# ---------------------------------------------------------------------------


class SFTracingFalconMiddleware:
    """Works for BOTH WSGI and ASGI flavours of Falcon."""

    # synchronous apps
    def process_request(self, req, resp):  # noqa: D401
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(req.path)

        # PERFORMANCE: Single-pass bytes-level header scan (no dict allocation until needed)
        # Scan headers once on bytes, only decode what we need, use latin-1 (fast 1:1 byte map)
        incoming_trace_raw = None  # bytes
        funcspan_raw = None  # bytes
        req_headers = None  # dict[str,str] only if capture enabled

        capture_req_headers = SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache

        # Falcon headers are accessible as req.headers (dict-like object)
        # We need to iterate through the raw headers if available
        try:
            # Try to access raw headers if available (_headers is internal dict in Falcon)
            if hasattr(req, "_headers") and req._headers:
                # Falcon WSGI stores headers internally
                hdr_items = req._headers.items()
                if capture_req_headers:
                    tmp = {}
                    for k, v in hdr_items:
                        kl = k.lower() if isinstance(k, str) else k
                        kb = kl.encode("latin-1") if isinstance(kl, str) else kl
                        vb = v.encode("latin-1") if isinstance(v, str) else v
                        if kb == SAILFISH_TRACING_HEADER_BYTES:
                            incoming_trace_raw = vb
                        elif kb == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                            funcspan_raw = vb
                        tmp[k] = v
                    req_headers = tmp
                else:
                    for k, v in hdr_items:
                        kl = k.lower() if isinstance(k, str) else k
                        kb = kl.encode("latin-1") if isinstance(kl, str) else kl
                        vb = v.encode("latin-1") if isinstance(v, str) else v
                        if kb == SAILFISH_TRACING_HEADER_BYTES:
                            incoming_trace_raw = vb
                        elif kb == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                            funcspan_raw = vb
            else:
                # Fallback: use req.get_header (slower but safer)
                incoming_trace_raw = req.get_header(SAILFISH_TRACING_HEADER)
                if incoming_trace_raw and isinstance(incoming_trace_raw, str):
                    incoming_trace_raw = incoming_trace_raw.encode("latin-1")
                funcspan_raw = req.get_header("X-Sf3-FunctionSpanCaptureOverride")
                if funcspan_raw and isinstance(funcspan_raw, str):
                    funcspan_raw = funcspan_raw.encode("latin-1")
                if capture_req_headers:
                    req_headers = dict(req.headers)
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(f"[[Falcon.process_request]] Header scan failed: {e}", log=False)
            # Fallback to simple approach
            incoming_trace_raw = req.get_header(SAILFISH_TRACING_HEADER)
            if incoming_trace_raw and isinstance(incoming_trace_raw, str):
                incoming_trace_raw = incoming_trace_raw.encode("latin-1")
            funcspan_raw = req.get_header("X-Sf3-FunctionSpanCaptureOverride")
            if funcspan_raw and isinstance(funcspan_raw, str):
                funcspan_raw = funcspan_raw.encode("latin-1")
            if capture_req_headers:
                req_headers = dict(req.headers)

        # Store captured headers for later emission
        req.context._sf_request_headers = req_headers

        # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        if incoming_trace_raw:
            # Incoming X-Sf3-Rid header provided - use it
            incoming_trace = (
                incoming_trace_raw.decode("latin-1")
                if isinstance(incoming_trace_raw, bytes)
                else incoming_trace_raw
            )
            get_or_set_sf_trace_id(
                incoming_trace, is_associated_with_inbound_request=True
            )
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # Optional funcspan override (decode only if present)
        funcspan_override_header = (
            funcspan_raw.decode("latin-1")
            if funcspan_raw and isinstance(funcspan_raw, bytes)
            else funcspan_raw
        )
        if funcspan_override_header:
            try:
                set_funcspan_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Falcon.process_request]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Falcon.process_request]] Failed to set function span override: {e}",
                        log=False,
                    )

        # Initialize outbound base without list/allocs from split()
        try:
            trace_id = get_sf_trace_id()
            if trace_id:
                s = str(trace_id)
                i = s.find("/")  # session
                j = s.find("/", i + 1) if i != -1 else -1  # page
                if j != -1:
                    base_trace = s[:j]  # "session/page"
                    set_outbound_header_base(
                        base_trace=base_trace,
                        parent_trace_id=s,  # "session/page/uuid"
                        funcspan=funcspan_override_header,
                    )
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Falcon.process_request]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Falcon.process_request]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # Capture request body if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # Falcon provides bounded_stream that we can read
                # For GET requests, this will typically be empty
                body = req.bounded_stream.read(_REQUEST_LIMIT_BYTES)
                req.context._sf_request_body = body if body else None
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Falcon]] Request body capture: {len(body) if body else 0} bytes (method={req.method})",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Falcon]] Failed to capture request body: {e}", log=False)
                req.context._sf_request_body = None
        else:
            req.context._sf_request_body = None

    # asynchronous apps
    async def process_request_async(self, req, resp):  # noqa: D401
        # Set current request path for route-based suppression (SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES)
        set_current_request_path(req.path)

        # PERFORMANCE: Single-pass bytes-level header scan (no dict allocation until needed)
        # Scan headers once on bytes, only decode what we need, use latin-1 (fast 1:1 byte map)
        incoming_trace_raw = None  # bytes
        funcspan_raw = None  # bytes
        req_headers = None  # dict[str,str] only if capture enabled

        capture_req_headers = SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS  # local cache

        # Falcon headers are accessible as req.headers (dict-like object)
        # We need to iterate through the raw headers if available
        try:
            # Try to access raw headers if available (_headers is internal dict in Falcon)
            if hasattr(req, "_headers") and req._headers:
                # Falcon ASGI stores headers internally
                hdr_items = req._headers.items()
                if capture_req_headers:
                    tmp = {}
                    for k, v in hdr_items:
                        kl = k.lower() if isinstance(k, str) else k
                        kb = kl.encode("latin-1") if isinstance(kl, str) else kl
                        vb = v.encode("latin-1") if isinstance(v, str) else v
                        if kb == SAILFISH_TRACING_HEADER_BYTES:
                            incoming_trace_raw = vb
                        elif kb == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                            funcspan_raw = vb
                        tmp[k] = v
                    req_headers = tmp
                else:
                    for k, v in hdr_items:
                        kl = k.lower() if isinstance(k, str) else k
                        kb = kl.encode("latin-1") if isinstance(kl, str) else kl
                        vb = v.encode("latin-1") if isinstance(v, str) else v
                        if kb == SAILFISH_TRACING_HEADER_BYTES:
                            incoming_trace_raw = vb
                        elif kb == FUNCSPAN_OVERRIDE_HEADER_BYTES:
                            funcspan_raw = vb
            else:
                # Fallback: use req.get_header (slower but safer)
                incoming_trace_raw = req.get_header(SAILFISH_TRACING_HEADER)
                if incoming_trace_raw and isinstance(incoming_trace_raw, str):
                    incoming_trace_raw = incoming_trace_raw.encode("latin-1")
                funcspan_raw = req.get_header("X-Sf3-FunctionSpanCaptureOverride")
                if funcspan_raw and isinstance(funcspan_raw, str):
                    funcspan_raw = funcspan_raw.encode("latin-1")
                if capture_req_headers:
                    req_headers = dict(req.headers)
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Falcon.process_request_async]] Header scan failed: {e}",
                    log=False,
                )
            # Fallback to simple approach
            incoming_trace_raw = req.get_header(SAILFISH_TRACING_HEADER)
            if incoming_trace_raw and isinstance(incoming_trace_raw, str):
                incoming_trace_raw = incoming_trace_raw.encode("latin-1")
            funcspan_raw = req.get_header("X-Sf3-FunctionSpanCaptureOverride")
            if funcspan_raw and isinstance(funcspan_raw, str):
                funcspan_raw = funcspan_raw.encode("latin-1")
            if capture_req_headers:
                req_headers = dict(req.headers)

        # Store captured headers for later emission
        req.context._sf_request_headers = req_headers

        # CRITICAL: Seed/ensure trace_id immediately (BEFORE any outbound work)
        if incoming_trace_raw:
            # Incoming X-Sf3-Rid header provided - use it
            incoming_trace = (
                incoming_trace_raw.decode("latin-1")
                if isinstance(incoming_trace_raw, bytes)
                else incoming_trace_raw
            )
            get_or_set_sf_trace_id(
                incoming_trace, is_associated_with_inbound_request=True
            )
        else:
            # No incoming X-Sf3-Rid header - generate fresh trace_id for this request
            generate_new_trace_id()

        # Optional funcspan override (decode only if present)
        funcspan_override_header = (
            funcspan_raw.decode("latin-1")
            if funcspan_raw and isinstance(funcspan_raw, bytes)
            else funcspan_raw
        )
        if funcspan_override_header:
            try:
                set_funcspan_override(funcspan_override_header)
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Falcon.process_request_async]] Set function span override from header: {funcspan_override_header}",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Falcon.process_request_async]] Failed to set function span override: {e}",
                        log=False,
                    )

        # Initialize outbound base without list/allocs from split()
        try:
            trace_id = get_sf_trace_id()
            if trace_id:
                s = str(trace_id)
                i = s.find("/")  # session
                j = s.find("/", i + 1) if i != -1 else -1  # page
                if j != -1:
                    base_trace = s[:j]  # "session/page"
                    set_outbound_header_base(
                        base_trace=base_trace,
                        parent_trace_id=s,  # "session/page/uuid"
                        funcspan=funcspan_override_header,
                    )
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Falcon.process_request_async]] Initialized outbound header base (base={base_trace[:16]}...)",
                            log=False,
                        )
        except Exception as e:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Falcon.process_request_async]] Failed to initialize outbound header base: {e}",
                    log=False,
                )

        # Capture request body if enabled
        if SF_NETWORKHOP_CAPTURE_REQUEST_BODY:
            try:
                # Falcon ASGI provides bounded_stream that we can read
                # For GET requests, this will typically be empty
                body = await req.bounded_stream.read(_REQUEST_LIMIT_BYTES)
                req.context._sf_request_body = body if body else None
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[Falcon]] Request body capture: {len(body) if body else 0} bytes (method={req.method})",
                        log=False,
                    )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(f"[[Falcon]] Failed to capture request body: {e}", log=False)
                req.context._sf_request_body = None
        else:
            req.context._sf_request_body = None

    # OTEL-STYLE: Emit network hop AFTER response (sync version)
    def process_response(self, req, resp, resource, req_succeeded):
        """Emit network hop after response built (sync version). Captures headers/bodies if enabled."""
        try:
            endpoint_id = getattr(req.context, "_sf_endpoint_id", None)
            if endpoint_id is not None and endpoint_id >= 0:
                try:
                    _, session_id = get_or_set_sf_trace_id()

                    # Get captured request data
                    req_headers = getattr(req.context, "_sf_request_headers", None)
                    req_body = getattr(req.context, "_sf_request_body", None)

                    # Capture response headers if enabled
                    resp_headers = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                        try:
                            # Debug: check what's available
                            if SF_DEBUG and app_config._interceptors_initialized:
                                attrs = [a for a in dir(resp) if not a.startswith("__")]
                                print(
                                    f"[[Falcon]] Response object has: {attrs[:10]}...",
                                    log=False,
                                )
                                if hasattr(resp, "_headers"):
                                    print(
                                        f"[[Falcon]] resp._headers = {resp._headers}",
                                        log=False,
                                    )
                                if hasattr(resp, "headers"):
                                    print(
                                        f"[[Falcon]] resp.headers type = {type(resp.headers)}",
                                        log=False,
                                    )

                            # Falcon response headers - try multiple approaches
                            if hasattr(resp, "_headers") and resp._headers:
                                resp_headers = dict(resp._headers)
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Falcon]] Captured from _headers: {resp_headers}",
                                        log=False,
                                    )
                            elif hasattr(resp, "headers"):
                                # resp.headers is a Headers object, iterate it
                                try:
                                    resp_headers = {
                                        k: v for k, v in resp.headers.items()
                                    }
                                    if (
                                        SF_DEBUG
                                        and app_config._interceptors_initialized
                                    ):
                                        print(
                                            f"[[Falcon]] Captured from headers.items(): {resp_headers}",
                                            log=False,
                                        )
                                except Exception:
                                    # Try converting to dict directly
                                    resp_headers = dict(resp.headers)
                                    if (
                                        SF_DEBUG
                                        and app_config._interceptors_initialized
                                    ):
                                        print(
                                            f"[[Falcon]] Captured from dict(headers): {resp_headers}",
                                            log=False,
                                        )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Falcon]] Failed to capture response headers: {e}",
                                    log=False,
                                )

                    # Capture response body if enabled
                    resp_body = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                        try:
                            # Falcon serializes resp.media to JSON, or uses resp.text/resp.data
                            if hasattr(resp, "text") and resp.text:
                                resp_body = resp.text.encode("utf-8")[
                                    :_RESPONSE_LIMIT_BYTES
                                ]
                            elif hasattr(resp, "data") and resp.data:
                                resp_body = resp.data[:_RESPONSE_LIMIT_BYTES]
                            elif hasattr(resp, "media") and resp.media is not None:
                                # Serialize media to JSON for capture
                                try:
                                    if HAS_ORJSON:
                                        media_json = orjson.dumps(
                                            resp.media, separators=(",", ":")
                                        )
                                    else:
                                        media_json = json.dumps(
                                            resp.media, separators=(",", ":")
                                        )
                                    resp_body = media_json.encode("utf-8")[
                                        :_RESPONSE_LIMIT_BYTES
                                    ]
                                except (TypeError, ValueError):
                                    pass
                        except Exception:
                            pass

                    # Extract raw path and query string for C to parse
                    raw_path = req.path  # e.g., "/log"
                    raw_query = (
                        req.query_string.encode("utf-8") if req.query_string else b""
                    )  # e.g., b"foo=5"

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Falcon]] About to emit network hop: endpoint_id={endpoint_id}, "
                            f"req_headers={'present' if req_headers else 'None'}, "
                            f"req_body={len(req_body) if req_body else 0} bytes, "
                            f"resp_headers={'present' if resp_headers else 'None'}, "
                            f"resp_body={len(resp_body) if resp_body else 0} bytes",
                            log=False,
                        )

                    # Direct C call - queues to background worker, returns instantly
                    # C will parse route and query_params from raw data
                    fast_send_network_hop_fast(
                        session_id=session_id,
                        endpoint_id=endpoint_id,
                        raw_path=raw_path,
                        raw_query_string=raw_query,
                        request_headers=req_headers,
                        request_body=req_body,
                        response_headers=resp_headers,
                        response_body=resp_body,
                    )

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Falcon]] Emitted network hop: endpoint_id={endpoint_id} "
                            f"session={session_id}",
                            log=False,
                        )
                except Exception as e:  # noqa: BLE001 S110
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(f"[[Falcon]] Failed to emit network hop: {e}", log=False)
        finally:
            # CRITICAL: Clear C TLS to prevent stale data in thread pools
            clear_c_tls_parent_trace_id()

            # CRITICAL: Clear outbound header base to prevent stale cached headers
            # ContextVar does NOT automatically clean up in thread pools - must clear explicitly
            clear_outbound_header_base()

            # CRITICAL: Clear trace_id to ensure fresh generation for next request
            # Without this, get_or_set_sf_trace_id() reuses trace_id from previous request
            # causing X-Sf4-Prid to stay constant when no incoming X-Sf3-Rid header
            clear_trace_id()

            # CRITICAL: Clear current request path to prevent stale data in thread pools
            clear_current_request_path()

            # Clear function span override for this request (thread-local cleanup)
            try:
                _sffuncspan_config.clear_thread_override()
            except Exception:
                pass

    async def process_response_async(self, req, resp, resource, req_succeeded):
        """Emit network hop after response built (async version). Captures headers/bodies if enabled."""
        try:
            endpoint_id = getattr(req.context, "_sf_endpoint_id", None)
            if endpoint_id is not None and endpoint_id >= 0:
                try:
                    _, session_id = get_or_set_sf_trace_id()

                    # Get captured request data
                    req_headers = getattr(req.context, "_sf_request_headers", None)
                    req_body = getattr(req.context, "_sf_request_body", None)

                    # Capture response headers if enabled
                    resp_headers = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS:
                        try:
                            # Debug: check what's available
                            if SF_DEBUG and app_config._interceptors_initialized:
                                attrs = [a for a in dir(resp) if not a.startswith("__")]
                                print(
                                    f"[[Falcon]] Response object has: {attrs[:10]}...",
                                    log=False,
                                )
                                if hasattr(resp, "_headers"):
                                    print(
                                        f"[[Falcon]] resp._headers = {resp._headers}",
                                        log=False,
                                    )
                                if hasattr(resp, "headers"):
                                    print(
                                        f"[[Falcon]] resp.headers type = {type(resp.headers)}",
                                        log=False,
                                    )

                            # Falcon response headers - try multiple approaches
                            if hasattr(resp, "_headers") and resp._headers:
                                resp_headers = dict(resp._headers)
                                if SF_DEBUG and app_config._interceptors_initialized:
                                    print(
                                        f"[[Falcon]] Captured from _headers: {resp_headers}",
                                        log=False,
                                    )
                            elif hasattr(resp, "headers"):
                                # resp.headers is a Headers object, iterate it
                                try:
                                    resp_headers = {
                                        k: v for k, v in resp.headers.items()
                                    }
                                    if (
                                        SF_DEBUG
                                        and app_config._interceptors_initialized
                                    ):
                                        print(
                                            f"[[Falcon]] Captured from headers.items(): {resp_headers}",
                                            log=False,
                                        )
                                except Exception:
                                    # Try converting to dict directly
                                    resp_headers = dict(resp.headers)
                                    if (
                                        SF_DEBUG
                                        and app_config._interceptors_initialized
                                    ):
                                        print(
                                            f"[[Falcon]] Captured from dict(headers): {resp_headers}",
                                            log=False,
                                        )
                        except Exception as e:
                            if SF_DEBUG and app_config._interceptors_initialized:
                                print(
                                    f"[[Falcon]] Failed to capture response headers: {e}",
                                    log=False,
                                )

                    # Capture response body if enabled
                    resp_body = None
                    if SF_NETWORKHOP_CAPTURE_RESPONSE_BODY:
                        try:
                            # Falcon serializes resp.media to JSON, or uses resp.text/resp.data
                            if hasattr(resp, "text") and resp.text:
                                resp_body = resp.text.encode("utf-8")[
                                    :_RESPONSE_LIMIT_BYTES
                                ]
                            elif hasattr(resp, "data") and resp.data:
                                resp_body = resp.data[:_RESPONSE_LIMIT_BYTES]
                            elif hasattr(resp, "media") and resp.media is not None:
                                # Serialize media to JSON for capture
                                try:
                                    if HAS_ORJSON:
                                        media_json = orjson.dumps(
                                            resp.media, separators=(",", ":")
                                        )
                                    else:
                                        media_json = json.dumps(
                                            resp.media, separators=(",", ":")
                                        )
                                    resp_body = media_json.encode("utf-8")[
                                        :_RESPONSE_LIMIT_BYTES
                                    ]
                                except (TypeError, ValueError):
                                    pass
                        except Exception:
                            pass

                    # Extract raw path and query string for C to parse
                    raw_path = req.path  # e.g., "/log"
                    raw_query = (
                        req.query_string.encode("utf-8") if req.query_string else b""
                    )  # e.g., b"foo=5"

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Falcon]] About to emit network hop: endpoint_id={endpoint_id}, "
                            f"req_headers={'present' if req_headers else 'None'}, "
                            f"req_body={len(req_body) if req_body else 0} bytes, "
                            f"resp_headers={'present' if resp_headers else 'None'}, "
                            f"resp_body={len(resp_body) if resp_body else 0} bytes",
                            log=False,
                        )

                    # Direct C call - queues to background worker, returns instantly
                    # C will parse route and query_params from raw data
                    fast_send_network_hop_fast(
                        session_id=session_id,
                        endpoint_id=endpoint_id,
                        raw_path=raw_path,
                        raw_query_string=raw_query,
                        request_headers=req_headers,
                        request_body=req_body,
                        response_headers=resp_headers,
                        response_body=resp_body,
                    )

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[Falcon]] Emitted network hop: endpoint_id={endpoint_id} "
                            f"session={session_id}",
                            log=False,
                        )
                except Exception as e:  # noqa: BLE001 S110
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(f"[[Falcon]] Failed to emit network hop: {e}", log=False)
        finally:
            # CRITICAL: Clear C TLS to prevent stale data in thread pools
            clear_c_tls_parent_trace_id()

            # CRITICAL: Clear outbound header base to prevent stale cached headers
            # ContextVar does NOT automatically clean up in thread pools - must clear explicitly
            clear_outbound_header_base()

            # CRITICAL: Clear trace_id to ensure fresh generation for next request
            # Without this, get_or_set_sf_trace_id() reuses trace_id from previous request
            # causing X-Sf4-Prid to stay constant when no incoming X-Sf3-Rid header
            clear_trace_id()

            # CRITICAL: Clear current request path to prevent stale data in thread pools
            clear_current_request_path()

            # Clear function span override for this request (thread-local cleanup)
            try:
                _sffuncspan_config.clear_thread_override()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# 2 | Hop-emission helper
# ---------------------------------------------------------------------------


def _capture_endpoint_info(
    req,
    hop_key: Tuple[str, int],
    fname: str,
    lno: int,
    responder_name: str,
    route: str = None,
) -> None:
    """OTEL-STYLE: Capture endpoint metadata and register endpoint for later emission."""
    # Check if route should be skipped
    if should_skip_route(route, _ROUTES_TO_SKIP):
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                f"[[Falcon]] Skipping endpoint (route matches skip pattern): {route}",
                log=False,
            )
        req.context._sf_endpoint_id = -1  # Mark as skipped
        return

    # Get or register endpoint_id
    endpoint_id = _ENDPOINT_REGISTRY.get(hop_key)

    if endpoint_id is None:
        endpoint_id = register_endpoint(
            line=str(lno),
            column="0",
            name=responder_name,
            entrypoint=fname,
            route=route,
        )
        if endpoint_id >= 0:
            _ENDPOINT_REGISTRY[hop_key] = endpoint_id
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    f"[[Falcon]] Registered endpoint: {responder_name} @ {fname}:{lno} (id={endpoint_id})",
                    log=False,
                )

    # Store endpoint_id for process_response to emit
    req.context._sf_endpoint_id = endpoint_id

    if SF_DEBUG and app_config._interceptors_initialized:
        print(
            f"[[Falcon]] Captured endpoint: {responder_name} ({fname}:{lno}) endpoint_id={endpoint_id}",
            log=False,
        )


def _make_wrapper(base_fn: Callable, resource: Any) -> Callable:
    """Return a hop-emitting, exception-capturing wrapper around *base_fn*."""

    real_fn = _unwrap_user_func(base_fn)

    # Ignore non-user and Strawberry handlers
    if real_fn.__module__.startswith("strawberry") or not _is_user_code(
        real_fn.__code__.co_filename
    ):
        return base_fn

    fname = real_fn.__code__.co_filename
    lno = real_fn.__code__.co_firstlineno
    hop_key = (fname, lno)
    responder_name = real_fn.__name__

    # ---------------- asynchronous responders ------------------------- #
    if inspect.iscoroutinefunction(base_fn):

        async def _async_wrapped(self, req, resp, *args, **kwargs):  # noqa: D401
            # Get route pattern from resource mapping
            route = _RESOURCE_ROUTES.get(id(self))
            _capture_endpoint_info(
                req, hop_key, fname, lno, responder_name, route=route
            )
            try:
                return await base_fn(self, req, resp, *args, **kwargs)
            except Exception as exc:  # catches falcon.HTTPError too
                custom_excepthook(type(exc), exc, exc.__traceback__)
                raise

        return _async_wrapped

    # ---------------- synchronous responders -------------------------- #
    def _sync_wrapped(self, req, resp, *args, **kwargs):  # noqa: D401
        # Get route pattern from resource mapping
        route = _RESOURCE_ROUTES.get(id(self))
        _capture_endpoint_info(req, hop_key, fname, lno, responder_name, route=route)
        try:
            return base_fn(self, req, resp, *args, **kwargs)
        except Exception as exc:  # catches falcon.HTTPError too
            custom_excepthook(type(exc), exc, exc.__traceback__)
            raise

    return _sync_wrapped


# ---------------------------------------------------------------------------
# 3 | Attach wrapper to every on_<METHOD> responder in a resource
# ---------------------------------------------------------------------------


def _wrap_resource(resource: Any) -> None:
    for attr in dir(resource):
        if not attr.startswith("on_"):
            continue

        handler = getattr(resource, attr)
        if not callable(handler) or getattr(handler, "__sf_hop_wrapped__", False):
            continue

        base_fn = handler.__func__ if isinstance(handler, MethodType) else handler
        wrapped_fn = _make_wrapper(base_fn, resource)
        setattr(wrapped_fn, "__sf_hop_wrapped__", True)

        # Bind to the *instance* so Falcon passes (req, resp, …) correctly
        bound = MethodType(wrapped_fn, resource)
        setattr(resource, attr, bound)


# ---------------------------------------------------------------------------
# 4 | Middleware merge utility (unchanged from earlier patch)
# ---------------------------------------------------------------------------


def _middleware_pos(cls) -> int:
    sig = inspect.signature(cls.__init__)
    params = [p for p in sig.parameters.values() if p.name != "self"]
    try:
        return [p.name for p in params].index("middleware")
    except ValueError:
        return -1


def _merge_middleware(args, kwargs, mw_pos):
    pos = list(args)
    kw = dict(kwargs)
    existing, used = None, None

    if "middleware" in kw:
        existing = kw.pop("middleware")
    if existing is None and mw_pos >= 0 and mw_pos < len(pos):
        cand = pos[mw_pos]
        # Not the Response class?
        if not inspect.isclass(cand):
            existing, used = cand, mw_pos
    if existing is None and len(pos) == 1:
        existing, used = pos[0], 0

    merged: List[Any] = []
    if existing is not None:
        merged = list(existing) if isinstance(existing, (list, tuple)) else [existing]
    merged.insert(0, SFTracingFalconMiddleware())

    if used is not None:
        pos[used] = merged
    else:
        kw["middleware"] = merged

    return tuple(pos), kw


# ---------------------------------------------------------------------------
# 5 | Patch helpers
# ---------------------------------------------------------------------------


def _patch_app_class(app_cls) -> None:
    mw_pos = _middleware_pos(app_cls)
    orig_init = app_cls.__init__
    orig_add = app_cls.add_route

    @functools.wraps(orig_init)
    def patched_init(self, *args, **kwargs):
        new_args, new_kwargs = _merge_middleware(args, kwargs, mw_pos)
        orig_init(self, *new_args, **new_kwargs)

    def patched_add_route(self, uri_template, resource, **kwargs):
        # Store route pattern for this resource instance
        _RESOURCE_ROUTES[id(resource)] = uri_template
        _wrap_resource(resource)
        return orig_add(self, uri_template, resource, **kwargs)

    app_cls.__init__ = patched_init
    app_cls.add_route = patched_add_route


# ---------------------------------------------------------------------------
# 6 | Public entry point
# ---------------------------------------------------------------------------


def patch_falcon(routes_to_skip: Optional[List[str]] = None) -> None:
    """Activate tracing for both WSGI and ASGI Falcon apps."""
    global _ROUTES_TO_SKIP
    _ROUTES_TO_SKIP = routes_to_skip or []

    try:
        import falcon
    except ImportError:  # pragma: no cover
        return

    # Patch synchronous WSGI app
    _patch_app_class(falcon.App)

    # Patch asynchronous ASGI app, if available
    try:
        from falcon.asgi import App as ASGIApp  # type: ignore

        _patch_app_class(ASGIApp)
    except ImportError:
        pass

    if SF_DEBUG and app_config._interceptors_initialized:
        print("[[patch_falcon]] Falcon tracing middleware installed", log=False)
