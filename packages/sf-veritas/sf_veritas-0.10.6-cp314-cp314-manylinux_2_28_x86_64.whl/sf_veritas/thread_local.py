import builtins
import ctypes
import fnmatch
import functools
import os
import threading
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID

from . import app_config
from .constants import (
    FUNCSPAN_OVERRIDE_HEADER,
    NONSESSION_APPLOGS,
    PARENT_SESSION_ID_HEADER,
    SAILFISH_TRACING_HEADER,
)
from .env_vars import SF_DEBUG

# Check if LD_PRELOAD is active (cached for performance)
_ld_preload_active: Optional[bool] = None

# Cache SF_DEBUG flag at module load to avoid repeated checks in hot paths
_SF_DEBUG_ENABLED = False


def is_ld_preload_active() -> bool:
    """
    Check if LD_PRELOAD with _sfteepreload is active.

    When LD_PRELOAD is active, the C extension handles UUID generation
    and appending to X-Sf3-Rid headers (much faster than Python).

    Returns True if:
    - LD_PRELOAD env var contains 'libsfnettee.so'
    - OR SF_TEEPRELOAD_ACTIVE env var is set to '1'

    This is cached on first call for performance.
    """
    global _ld_preload_active, _SF_DEBUG_ENABLED

    if _ld_preload_active is not None:
        return _ld_preload_active

    # Check if LD_PRELOAD contains our library
    ld_preload = os.getenv("LD_PRELOAD", "")
    if "libsfnettee.so" in ld_preload:
        _ld_preload_active = True
        _SF_DEBUG_ENABLED = SF_DEBUG and app_config._interceptors_initialized
        if _SF_DEBUG_ENABLED:
            print(f"[thread_local] LD_PRELOAD active: {ld_preload}", log=False)
        return True

    # Check explicit activation flag (set by LD_PRELOAD library itself)
    if os.getenv("SF_TEEPRELOAD_ACTIVE") == "1":
        _ld_preload_active = True
        _SF_DEBUG_ENABLED = SF_DEBUG and app_config._interceptors_initialized
        if _SF_DEBUG_ENABLED:
            print("[thread_local] SF_TEEPRELOAD_ACTIVE=1", log=False)
        return True

    _ld_preload_active = False
    _SF_DEBUG_ENABLED = SF_DEBUG and app_config._interceptors_initialized
    return False


# Eager initialization at module load for C TLS function pointer
_sf_tls_setter = None


def _init_c_tls_setter():
    """Initialize C TLS setter at module load time to avoid ctypes.CDLL overhead in hot path."""
    global _sf_tls_setter
    try:
        # Use the main process (LD_PRELOAD library is in the global namespace)
        _lib = ctypes.CDLL(None)
        _fn = _lib.sf_set_parent_trace_id_tls
        _fn.argtypes = [ctypes.c_char_p]
        _fn.restype = None
        _sf_tls_setter = _fn
    except Exception:
        _sf_tls_setter = False  # don't retry every call


# Initialize at module load time (moves expensive CDLL call out of hot path)
_init_c_tls_setter()


def _set_c_tls_parent_trace_id(parent: str) -> None:
    """
    Set parent trace ID in C TLS for ultra-fast access by LD_PRELOAD hooks.

    This avoids Python lookups in the C extension - the C hooks can read
    the parent PRID directly from TLS with a single memory access.

    CRITICAL: Must call clear_c_tls_parent_trace_id() at end of request to prevent stale data!

    OPTIMIZED: Disabled when LD_PRELOAD active - C code reads from ContextVar directly (faster).
    C function pointer initialized at module load time (not on first call).
    """
    # PERFORMANCE: Skip TLS call when LD_PRELOAD active - C reads from ContextVar/shared registry
    # This eliminates: string encoding (expensive!), thread-local attribute setting, ctypes overhead
    if not _ld_preload_active and _sf_tls_setter:
        # Keep bytes alive for the request lifetime to keep C pointer valid
        b = parent.encode("ascii", "ignore")
        _cached_outbound_headers_tls._tls_parent_prid_bytes = b  # anchor
        _sf_tls_setter(b)


def clear_c_tls_parent_trace_id() -> None:
    """
    Clear parent trace ID from C TLS at end of request.

    CRITICAL: Prevents stale data when threads are reused (e.g., thread pools).
    Must be called at the end of EVERY request that set the C TLS.

    OPTIMIZED: Disabled when LD_PRELOAD active - no TLS to clear.
    """
    # PERFORMANCE: Skip when LD_PRELOAD active - nothing was set in TLS
    if not _ld_preload_active and _sf_tls_setter and _sf_tls_setter is not False:
        try:
            # Set to NULL to clear
            _sf_tls_setter(None)
            # Clear the anchored bytes
            if hasattr(_cached_outbound_headers_tls, "_tls_parent_prid_bytes"):
                delattr(_cached_outbound_headers_tls, "_tls_parent_prid_bytes")
        except Exception:
            pass  # Ignore errors during cleanup


def clear_outbound_header_base() -> None:
    """
    Clear outbound header base from ContextVar at end of request.

    CRITICAL: Prevents stale X-Sf4-Prid data from persisting across requests.
    Must be called at the end of EVERY request that set the outbound header base.

    This ensures fresh header generation for each request with proper isolation.
    """
    try:
        outbound_header_base_ctx.set(None)
        if _SF_DEBUG_ENABLED:
            print(
                "[clear_outbound_header_base] Cleared outbound_header_base_ctx ContextVar",
                log=False,
            )
    except Exception as e:
        # Don't let cleanup errors break the app
        if _SF_DEBUG_ENABLED:
            print(
                f"[clear_outbound_header_base] ⚠️ Error during cleanup: {e}", log=False
            )


def clear_trace_id() -> None:
    """
    Clear trace_id from ContextVar at end of request.

    CRITICAL: Ensures fresh trace_id generation for requests without incoming X-Sf3-Rid header.
    Must be called at the end of EVERY request that didn't have an incoming trace header.

    Without this, get_or_set_sf_trace_id() reuses the trace_id from the previous request,
    causing X-Sf4-Prid to remain constant across multiple requests (same parent_trace_id).
    """
    try:
        trace_id_ctx.set(None)
        if _SF_DEBUG_ENABLED:
            print("[clear_trace_id] Cleared trace_id_ctx ContextVar", log=False)
    except Exception as e:
        # Don't let cleanup errors break the app
        if _SF_DEBUG_ENABLED:
            print(f"[clear_trace_id] ⚠️ Error during cleanup: {e}", log=False)


# Define context variables
trace_id_ctx = ContextVar("trace_id", default=None)
handled_exceptions_ctx = ContextVar("handled_exceptions", default=set())
reentrancy_guard_logging_active_ctx = ContextVar(
    "reentrancy_guard_logging_active", default=False
)
reentrancy_guard_logging_preactive_ctx = ContextVar(
    "reentrancy_guard_logging_preactive", default=False
)
reentrancy_guard_print_active_ctx = ContextVar(
    "reentrancy_guard_print_active", default=False
)
reentrancy_guard_print_preactive_ctx = ContextVar(
    "reentrancy_guard_print_preactive", default=False
)
reentrancy_guard_exception_active_ctx = ContextVar(
    "reentrancy_guard_exception_active", default=False
)
reentrancy_guard_exception_preactive_ctx = ContextVar(
    "reentrancy_guard_exception_preactive", default=False
)

# Suppressors
suppress_network_recording_ctx = ContextVar("suppress_network_recording", default=False)
suppress_log_output_ctx = ContextVar("suppress_log_output", default=False)

# Current request path for route-based suppression
current_request_path_ctx = ContextVar("current_request_path", default=None)

# Function span capture override (for header propagation)
funcspan_override_ctx = ContextVar("funcspan_override", default=None)

# Outbound header base (for ultra-fast header injection with cross-thread support)
outbound_header_base_ctx = ContextVar("outbound_header_base", default=None)

reentrancy_guard_sys_stdout_active_ctx = ContextVar(
    "reentrancy_guard_sys_stdout_active", default=False
)

# Thread-local storage as a fallback
_thread_locals = threading.local()

_shared_trace_registry = {}
_shared_trace_registry_lock = threading.RLock()

# Shared registry for outbound header base (cross-thread support, same pattern as trace_id)
_shared_outbound_header_base_registry = {}
_shared_outbound_header_base_lock = threading.RLock()

# ULTRA-FAST: Cached headers dict in thread-local storage (NO LOCK, ~10-20ns access)
# This is the fully-built headers dict, ready to inject (no dict building overhead)
_cached_outbound_headers_tls = threading.local()


def _set_shared_trace_id(trace_id: Optional[str]) -> None:
    # PERFORMANCE: In LD_PRELOAD mode, skip lock (ContextVar is primary source)
    if _ld_preload_active:
        _shared_trace_registry["trace_id"] = trace_id
        return
    with _shared_trace_registry_lock:
        _shared_trace_registry["trace_id"] = trace_id


def _set_shared_outbound_header_base(base_dict: Optional[dict]) -> None:
    """Store outbound header base in shared registry (works across threads)."""
    # PERFORMANCE: In LD_PRELOAD mode, skip lock (ContextVar is primary source)
    if _ld_preload_active:
        _shared_outbound_header_base_registry["base_dict"] = base_dict
        return
    with _shared_outbound_header_base_lock:
        _shared_outbound_header_base_registry["base_dict"] = base_dict
        _clear_cached_outbound_headers()


def _get_shared_outbound_header_base() -> Optional[dict]:
    """Get outbound header base from shared registry (works across threads)."""
    # PERFORMANCE: In LD_PRELOAD mode, skip lock (ContextVar is primary source)
    if _ld_preload_active:
        return _shared_outbound_header_base_registry.get("base_dict")
    with _shared_outbound_header_base_lock:
        return _shared_outbound_header_base_registry.get("base_dict")


def _clear_cached_outbound_headers() -> None:
    """Clear thread-local cached headers (called when base changes)."""
    try:
        if hasattr(_cached_outbound_headers_tls, "headers"):
            delattr(_cached_outbound_headers_tls, "headers")
    except AttributeError:
        pass


def _get_shared_trace_id() -> Optional[str]:
    # PERFORMANCE: In LD_PRELOAD mode, skip lock (ContextVar is primary source)
    if _ld_preload_active:
        return _shared_trace_registry.get("trace_id")
    with _shared_trace_registry_lock:
        return _shared_trace_registry.get("trace_id")


def _get_context_or_thread_local(
    ctx_var: ContextVar, attr_name: str, default: Any
) -> Any:
    return ctx_var.get()  # or getattr(_thread_locals, attr_name, default)


def _set_context_and_thread_local(
    ctx_var: ContextVar, attr_name: str, value: Any
) -> Any:
    ctx_var.set(value)
    # setattr(_thread_locals, attr_name, value)
    return value


def unset_sf_trace_id() -> None:
    _set_shared_trace_id(None)
    _set_context_and_thread_local(trace_id_ctx, "trace_id", None)
    if _SF_DEBUG_ENABLED:
        print("[[DEBUG]] unset_sf_trace_id: trace_id cleared", log=False)


def _get_or_set_context_and_thread_local(
    ctx_var: ContextVar, attr_name: str, value_if_not_set
) -> Tuple[bool, Any]:
    value = ctx_var.get()  # or getattr(_thread_locals, attr_name, None)
    if value is None:
        _set_context_and_thread_local(ctx_var, attr_name, value_if_not_set)
        return True, value_if_not_set
    return False, value


# Trace ID functions
def get_sf_trace_id() -> Optional[Union[str, UUID]]:
    # Use ContextVar for both LD_PRELOAD and Python-only modes
    # ContextVar is async-safe and thread-safe, no shared registry needed
    return _get_context_or_thread_local(trace_id_ctx, "trace_id", None)


def set_sf_trace_id(trace_id: Union[str, UUID]) -> Union[str, UUID]:
    # Set in ContextVar for both LD_PRELOAD and Python-only modes
    # ContextVar is async-safe and thread-safe, no shared registry needed
    return _set_context_and_thread_local(trace_id_ctx, "trace_id", trace_id)


def generate_new_trace_id() -> str:
    """
    Generate and set a fresh trace_id for requests without incoming X-Sf3-Rid header.

    This is called explicitly when there's no incoming tracing header, ensuring
    a fresh trace_id is generated for each request (avoiding stale ContextVar reuse).

    Returns:
        The newly generated trace_id string.
    """
    unique_id = uuid.uuid4()
    trace_id = f"{NONSESSION_APPLOGS}-v3/{app_config._sailfish_api_key}/{unique_id}"

    # Set in ContextVar
    _set_context_and_thread_local(trace_id_ctx, "trace_id", trace_id)

    if _SF_DEBUG_ENABLED:
        print(f"[generate_new_trace_id] Generated fresh trace_id: {trace_id}", log=False)

    return trace_id


def get_or_set_sf_trace_id(
    new_trace_id_if_not_set: Optional[str] = None,
    is_associated_with_inbound_request: bool = False,
) -> Tuple[bool, Union[str, UUID]]:
    ###
    ###
    ###
    ### IMPLEMENT skip if not ready yet?
    ###
    ###
    ###
    # Check if trace_id already exists
    if not new_trace_id_if_not_set:
        # Use ContextVar for both LD_PRELOAD and Python-only modes
        trace_id = _get_context_or_thread_local(trace_id_ctx, "trace_id", None)
        if trace_id:
            if _SF_DEBUG_ENABLED:
                print(f"[trace_id] Returning existing trace_id: {trace_id}", log=False)
            return False, trace_id

        # No trace_id found - generate new one
        if _SF_DEBUG_ENABLED:
            print("[trace_id] No trace_id found. Generating new trace_id.", log=False)
        unique_id = uuid.uuid4()
        trace_id = f"{NONSESSION_APPLOGS}-v3/{app_config._sailfish_api_key}/{unique_id}"

        # Set using ContextVar only (no shared registry)
        _set_context_and_thread_local(trace_id_ctx, "trace_id", trace_id)

        if _SF_DEBUG_ENABLED:
            print(f"[trace_id] Generated and set new trace_id: {trace_id}", log=False)
        return True, trace_id

    # new_trace_id_if_not_set provided - set it directly
    if _SF_DEBUG_ENABLED:
        print(
            f"[trace_id] Setting new trace_id from argument: {new_trace_id_if_not_set}",
            log=False,
        )

    # Set using ContextVar only (no shared registry)
    _set_context_and_thread_local(trace_id_ctx, "trace_id", new_trace_id_if_not_set)

    return True, new_trace_id_if_not_set


# Handled exceptions functions
def get_handled_exceptions() -> Set[Any]:
    return _get_context_or_thread_local(
        handled_exceptions_ctx, "handled_exceptions", set()
    )


def set_handled_exceptions(exceptions_set: Set[Any]) -> Set[Any]:
    return _set_context_and_thread_local(
        handled_exceptions_ctx, "handled_exceptions", exceptions_set
    )


def get_or_set_handled_exceptions(default: set = None) -> Tuple[bool, Set[Any]]:
    if default is None:
        default = set()
    return _get_or_set_context_and_thread_local(
        handled_exceptions_ctx, "handled_exceptions", default
    )


def mark_exception_handled(exception) -> None:
    handled = get_handled_exceptions()
    handled.add(id(exception))
    set_handled_exceptions(handled)
    if hasattr(exception, "_handled"):
        setattr(exception, "_handled", True)


def has_handled_exception(exception) -> bool:
    return id(exception) in get_handled_exceptions() or getattr(
        exception, "_handled", False
    )


def reset_handled_exceptions() -> Set[Any]:
    return set_handled_exceptions(set())


# Reentrancy guards (logging)
def get_reentrancy_guard_logging_active() -> bool:
    return _get_context_or_thread_local(
        reentrancy_guard_logging_active_ctx, "reentrancy_guard_logging_active", False
    )


def set_reentrancy_guard_logging_active(value: bool) -> bool:
    return _set_context_and_thread_local(
        reentrancy_guard_logging_active_ctx, "reentrancy_guard_logging_active", value
    )


def get_or_set_reentrancy_guard_logging_active(
    value_if_not_set: bool,
) -> Tuple[bool, bool]:
    return _get_or_set_context_and_thread_local(
        reentrancy_guard_logging_active_ctx,
        "reentrancy_guard_logging_active",
        value_if_not_set,
    )


def activate_reentrancy_guards_logging() -> bool:
    set_reentrancy_guard_logging_active(True)
    set_reentrancy_guard_logging_preactive(True)
    return True


def get_reentrancy_guard_logging_preactive() -> bool:
    return _get_context_or_thread_local(
        reentrancy_guard_logging_preactive_ctx,
        "reentrancy_guard_logging_preactive",
        False,
    )


def set_reentrancy_guard_logging_preactive(value: bool) -> bool:
    return _set_context_and_thread_local(
        reentrancy_guard_logging_preactive_ctx,
        "reentrancy_guard_logging_preactive",
        value,
    )


def get_or_set_reentrancy_guard_logging_preactive(
    value_if_not_set: bool,
) -> Tuple[bool, bool]:
    return _get_or_set_context_and_thread_local(
        reentrancy_guard_logging_preactive_ctx,
        "reentrancy_guard_logging_preactive",
        value_if_not_set,
    )


def activate_reentrancy_guards_logging_preactive() -> bool:
    return set_reentrancy_guard_logging_preactive(True)


# Reentrancy guards (stdout)
def get_reentrancy_guard_sys_stdout_active() -> bool:
    return _get_context_or_thread_local(
        reentrancy_guard_sys_stdout_active_ctx,
        "reentrancy_guard_sys_stdout_active",
        False,
    )


def set_reentrancy_guard_sys_stdout_active(value: bool) -> bool:
    return _set_context_and_thread_local(
        reentrancy_guard_sys_stdout_active_ctx,
        "reentrancy_guard_sys_stdout_active",
        value,
    )


def activate_reentrancy_guards_sys_stdout() -> bool:
    set_reentrancy_guard_sys_stdout_active(True)
    return True


# Reentrancy guards (print)
def get_reentrancy_guard_print_active() -> bool:
    return _get_context_or_thread_local(
        reentrancy_guard_print_active_ctx, "reentrancy_guard_print_active", False
    )


def set_reentrancy_guard_print_active(value: bool) -> bool:
    return _set_context_and_thread_local(
        reentrancy_guard_print_active_ctx, "reentrancy_guard_print_active", value
    )


def get_or_set_reentrancy_guard_print_active(
    value_if_not_set: bool,
) -> Tuple[bool, bool]:
    return _get_or_set_context_and_thread_local(
        reentrancy_guard_print_active_ctx,
        "reentrancy_guard_print_active",
        value_if_not_set,
    )


def activate_reentrancy_guards_print() -> bool:
    set_reentrancy_guard_print_active(True)
    set_reentrancy_guard_print_preactive(True)
    return True


def get_reentrancy_guard_print_preactive() -> bool:
    return _get_context_or_thread_local(
        reentrancy_guard_print_preactive_ctx, "reentrancy_guard_print_preactive", False
    )


def set_reentrancy_guard_print_preactive(value: bool) -> bool:
    return _set_context_and_thread_local(
        reentrancy_guard_print_preactive_ctx, "reentrancy_guard_print_preactive", value
    )


def get_or_set_reentrancy_guard_print_preactive(
    value_if_not_set: bool,
) -> Tuple[bool, bool]:
    return _get_or_set_context_and_thread_local(
        reentrancy_guard_print_preactive_ctx,
        "reentrancy_guard_print_preactive",
        value_if_not_set,
    )


def activate_reentrancy_guards_print_preactive() -> bool:
    return set_reentrancy_guard_print_preactive(True)


# Reentrancy guards (exception)
def get_reentrancy_guard_exception_active() -> bool:
    return _get_context_or_thread_local(
        reentrancy_guard_exception_active_ctx,
        "reentrancy_guard_exception_active",
        False,
    )


def set_reentrancy_guard_exception_active(value: bool) -> bool:
    return _set_context_and_thread_local(
        reentrancy_guard_exception_active_ctx,
        "reentrancy_guard_exception_active",
        value,
    )


def get_or_set_reentrancy_guard_exception_active(
    value_if_not_set: bool,
) -> Tuple[bool, bool]:
    return _get_or_set_context_and_thread_local(
        reentrancy_guard_exception_active_ctx,
        "reentrancy_guard_exception_active",
        value_if_not_set,
    )


def activate_reentrancy_guards_exception() -> bool:
    set_reentrancy_guard_exception_active(True)
    set_reentrancy_guard_exception_preactive(True)
    return True


def get_reentrancy_guard_exception_preactive() -> bool:
    return _get_context_or_thread_local(
        reentrancy_guard_exception_preactive_ctx,
        "reentrancy_guard_exception_preactive",
        False,
    )


def set_reentrancy_guard_exception_preactive(value: bool) -> bool:
    return _set_context_and_thread_local(
        reentrancy_guard_exception_preactive_ctx,
        "reentrancy_guard_exception_preactive",
        value,
    )


def get_or_set_reentrancy_guard_exception_preactive(
    value_if_not_set: bool,
) -> Tuple[bool, bool]:
    return _get_or_set_context_and_thread_local(
        reentrancy_guard_exception_preactive_ctx,
        "reentrancy_guard_exception_preactive",
        value_if_not_set,
    )


def activate_reentrancy_guards_exception_preactive() -> bool:
    return set_reentrancy_guard_exception_preactive(True)


# Get and set context
def get_context() -> Dict[str, Any]:
    return {
        "trace_id": get_sf_trace_id(),
        "handled_exceptions": get_handled_exceptions(),
        "reentrancy_guard_logging_active": get_reentrancy_guard_logging_active(),
        "reentrancy_guard_logging_preactive": get_reentrancy_guard_logging_preactive(),
        "reentrancy_guard_print_active": get_reentrancy_guard_print_active(),
        "reentrancy_guard_print_preactive": get_reentrancy_guard_print_preactive(),
        "reentrancy_guard_exception_active": get_reentrancy_guard_exception_active(),
        "reentrancy_guard_exception_preactive": get_reentrancy_guard_exception_preactive(),
        "reentrancy_guard_sys_stdout_active": get_reentrancy_guard_sys_stdout_active(),
        "suppress_network_recording": is_network_recording_suppressed(),
        "suppress_log_output": is_log_output_suppressed(),
    }


def set_context(context) -> None:
    set_sf_trace_id(context.get("trace_id"))
    set_handled_exceptions(context.get("handled_exceptions", set()))
    set_reentrancy_guard_logging_active(
        context.get("reentrancy_guard_logging_active", False)
    )
    set_reentrancy_guard_logging_preactive(
        context.get("reentrancy_guard_logging_preactive", False)
    )
    set_reentrancy_guard_print_active(
        context.get("reentrancy_guard_print_active", False)
    )
    set_reentrancy_guard_print_preactive(
        context.get("reentrancy_guard_print_preactive", False)
    )
    set_reentrancy_guard_exception_active(
        context.get("reentrancy_guard_exception_active", False)
    )
    set_reentrancy_guard_exception_preactive(
        context.get("reentrancy_guard_exception_preactive", False)
    )
    set_reentrancy_guard_sys_stdout_active(
        context.get("reentrancy_guard_sys_stdout_active", False)
    )
    # suppressors are transient; don't set them from incoming context


@contextmanager
def suppress_network_recording():
    token = suppress_network_recording_ctx.set(True)
    try:
        yield
    finally:
        suppress_network_recording_ctx.reset(token)


@functools.lru_cache(maxsize=1)
def _get_disabled_route_patterns() -> List[str]:
    """
    Get route patterns to skip network hop capture.

    Routes are configured via setup_interceptors(routes_to_skip_network_hops=[...])
    which defaults to the SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES env var.

    Returns a list of route patterns with wildcard support (* and ? characters).
    Cached for performance (called on every request).

    Examples:
        "/healthz, /metrics" -> ["/healthz", "/metrics"]
        "/admin/*, /api/v1/status*" -> ["/admin/*", "/api/v1/status*"]
    """
    # Get patterns from app_config (already contains parameter or env var default)
    patterns = getattr(app_config, "_routes_to_skip_network_hops", [])

    if _SF_DEBUG_ENABLED and patterns:
        print(f"[_get_disabled_route_patterns] Route patterns to skip: {patterns}", log=False)

    return patterns


def _route_matches_pattern(path: str) -> bool:
    """
    Check if the given path matches any disabled route pattern.

    Uses fnmatch for glob-style pattern matching:
    - * matches any sequence of characters
    - ? matches any single character

    Args:
        path: Request path to check (e.g., "/api/v1/users")

    Returns:
        True if path matches any disabled pattern, False otherwise.

    Examples:
        _route_matches_pattern("/healthz") -> True if "/healthz" in patterns
        _route_matches_pattern("/admin/users") -> True if "/admin/*" in patterns
        _route_matches_pattern("/api/v1/status") -> True if "/api/v1/status*" in patterns
    """
    patterns = _get_disabled_route_patterns()
    if not patterns:
        return False

    # Use fnmatch for glob pattern matching (* and ? wildcards)
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            if _SF_DEBUG_ENABLED:
                print(f"[_route_matches_pattern] Path '{path}' matches pattern '{pattern}' - suppressing", log=False)
            return True

    return False


def is_network_recording_suppressed() -> bool:
    """
    Check if network recording is suppressed.

    Checks three suppression mechanisms (any one triggers suppression):
    1. Explicit suppression via context manager or decorator (suppress_network_recording_ctx)
    2. Route-based suppression via SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES
    3. Thread-local C telemetry guard (g_in_telemetry_send) - used by C extension sender threads

    Returns:
        True if network recording is suppressed by any mechanism, False otherwise.
    """
    # Check explicit suppression (context manager / decorator)
    if suppress_network_recording_ctx.get():
        return True

    # Check route-based suppression
    current_path = get_current_request_path()
    if current_path and _route_matches_pattern(current_path):
        return True

    return False


@contextmanager
def suppress_log_output():
    token = suppress_log_output_ctx.set(True)
    try:
        yield
    finally:
        suppress_log_output_ctx.reset(token)


def is_log_output_suppressed() -> bool:
    return suppress_log_output_ctx.get()


# Current request path functions (for route-based suppression)
def set_current_request_path(path: str) -> None:
    """Set current request path for route-based network suppression."""
    current_request_path_ctx.set(path)


def get_current_request_path() -> Optional[str]:
    """Get current request path."""
    return current_request_path_ctx.get()


def clear_current_request_path() -> None:
    """Clear current request path at end of request."""
    current_request_path_ctx.set(None)


# Function span capture override functions (ultra-fast, <10ns)
def get_funcspan_override() -> Optional[str]:
    """Get function span capture override header value (fast ContextVar lookup ~8ns)."""
    return funcspan_override_ctx.get()


def set_funcspan_override(value: Optional[str]) -> Optional[str]:
    """Set function span capture override header value."""
    funcspan_override_ctx.set(value)
    return value


def clear_funcspan_override() -> None:
    """Clear function span capture override."""
    funcspan_override_ctx.set(None)


# ================================
# Outbound header generation (ultra-fast header injection with shared registry + ContextVar)
# ================================


def set_outbound_header_base(
    base_trace: str, parent_trace_id: str, funcspan: Optional[str]
) -> None:
    """
    Store base header info in BOTH shared registry AND ContextVar.

    **OPTIMIZATION:** When LD_PRELOAD is active, pre-builds the headers dict HERE
    so all outbound calls can reuse it (~10ns vs 1-10μs per call).

    Uses same pattern as trace_id for cross-thread support.

    Args:
        base_trace: Base trace path (e.g., "session_id/page_visit_id") - used for generating new X-Sf3-Rid
        parent_trace_id: FULL incoming trace_id (e.g., "session_id/page_visit_id/request_uuid") - used for X-Sf4-Prid
        funcspan: Optional function span capture override header value

    Performance: <1μs (dict creation + set operations)

    ULTRA-OPTIMIZED: Lockless path when LD_PRELOAD active, minimal dict allocations, no C calls.
    """
    # Pre-build cached headers for both LD_PRELOAD and Python-only modes
    # This optimization applies to both modes now
    if funcspan:
        # Construct nested dict in one go for funcspan case
        cached_headers = {
            SAILFISH_TRACING_HEADER: base_trace,
            PARENT_SESSION_ID_HEADER: parent_trace_id,
            FUNCSPAN_OVERRIDE_HEADER: funcspan,
        }
        base_dict = {
            "base_trace": base_trace,
            "parent_trace_id": parent_trace_id,
            "funcspan": funcspan,
            "_cached_headers": cached_headers,
        }
    else:
        # Fast path: No funcspan (most common case) - construct in one go
        cached_headers = {
            SAILFISH_TRACING_HEADER: base_trace,
            PARENT_SESSION_ID_HEADER: parent_trace_id,
        }
        base_dict = {
            "base_trace": base_trace,
            "parent_trace_id": parent_trace_id,
            "funcspan": None,
            "_cached_headers": cached_headers,
        }

    # Store in ContextVar only (no shared registry)
    outbound_header_base_ctx.set(base_dict)

    # DEBUG: Log when outbound header base is set (helps troubleshoot X-Sf4-Prid issues)
    if _SF_DEBUG_ENABLED:
        print(
            f"[set_outbound_header_base] Set parent_trace_id={parent_trace_id}, base_trace={base_trace}, cached_headers={cached_headers}",
            log=False,
        )

    # Set C TLS for non-LD_PRELOAD mode
    if not _ld_preload_active:
        _set_c_tls_parent_trace_id(parent_trace_id)


def get_outbound_headers_with_new_uuid() -> dict:
    """
    Generate fresh outbound headers with new UUID appended to base trace.

    **ULTRA-FAST when LD_PRELOAD is active:**
    - Headers dict cached in ContextVar (no lock, ~10-20ns)
    - C appends UUID at socket intercept time (no Python UUID generation)
    - Total overhead: ~10-20ns (just ContextVar read + dict return)

    **When LD_PRELOAD inactive:**
    - Each call generates new UUID in Python (~100ns)
    - Headers dict built fresh each time

    Returns:
        Dictionary with X-Sf3-Rid, X-Sf4-Prid, and optionally X-Sf3-FunctionSpanCaptureOverride.
        Empty dict if no base initialized.

    Performance:
        - LD_PRELOAD active: ~10-20ns (cached headers from ContextVar, NO LOCK)
        - LD_PRELOAD inactive: ~100ns (uuid4 generation + string concat + dict creation)
    """
    # Get base_dict from ContextVar (no shared registry fallback)
    base_dict = outbound_header_base_ctx.get()

    if not base_dict:
        if _SF_DEBUG_ENABLED:
            print(
                f"[get_outbound_headers_with_new_uuid] ⚠️ No outbound header base found in ContextVar",
                log=False,
            )
        return {}

    # ULTRA-FAST PATH: Return pre-built headers if available (LD_PRELOAD mode)
    cached_headers = base_dict.get("_cached_headers")
    if cached_headers:
        # DEBUG: ENABLED for troubleshooting X-Sf4-Prid issue
        if _SF_DEBUG_ENABLED:
            print(
                f"[get_outbound_headers_with_new_uuid] ⚡ Returning pre-built headers: {cached_headers}",
                log=False,
            )
        # Return a shallow copy to prevent mutations from affecting cached dict
        return dict(cached_headers)

    # SLOW PATH: Generate UUID in Python (Python-only mode)
    if _SF_DEBUG_ENABLED:
        print(
            f"[get_outbound_headers_with_new_uuid] 🐌 LD_PRELOAD inactive - generating UUID in Python",
            log=False,
        )

    base_trace = base_dict.get("base_trace")
    parent_trace_id = base_dict.get("parent_trace_id")
    funcspan = base_dict.get("funcspan")

    if not base_trace or not parent_trace_id:
        if _SF_DEBUG_ENABLED:
            print(
                f"[get_outbound_headers_with_new_uuid] ⚠️ Missing base_trace or parent_trace_id!",
                log=False,
            )
        return {}

    # Generate new UUID for each call
    new_uuid = str(uuid.uuid4())
    outbound_trace_id = f"{base_trace}/{new_uuid}"

    headers = {
        SAILFISH_TRACING_HEADER: outbound_trace_id,  # X-Sf3-Rid: session/page/uuid (Python)
        PARENT_SESSION_ID_HEADER: parent_trace_id,
    }

    if funcspan:
        headers[FUNCSPAN_OVERRIDE_HEADER] = funcspan

    return headers


import logging

# include httpcore/h11/h2 because we now call httpcore directly
_HTTPX_LOGGERS = ("httpx", "httpcore", "h11", "h2")


@contextmanager
def suppress_logs():
    """Temporarily silence client libraries without touching global logging config."""
    loggers = [logging.getLogger(n) for n in _HTTPX_LOGGERS]
    prev_disabled = [lg.disabled for lg in loggers]
    try:
        for lg in loggers:
            lg.disabled = True
        yield
    finally:
        for lg, was_disabled in zip(loggers, prev_disabled):
            lg.disabled = was_disabled
