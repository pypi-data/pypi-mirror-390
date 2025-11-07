"""
Central tracking for patch application to prevent double-patching.

This module maintains a registry of applied patches keyed by (patch_name, pid)
to handle worker forks (gunicorn/uvicorn) and module reloading correctly.
"""
import os
import threading

# Global registry: {(patch_name, pid): True}
_PATCHED = {}
_lock = threading.Lock()


def is_already_patched(patch_name: str) -> bool:
    """
    Check if a patch has already been applied in this process.

    Args:
        patch_name: Unique identifier for the patch (e.g., "requests", "httpx")

    Returns:
        True if already patched in current PID, False otherwise
    """
    key = (patch_name, os.getpid())
    with _lock:
        return key in _PATCHED


def mark_as_patched(patch_name: str) -> bool:
    """
    Mark a patch as applied in the current process.

    Args:
        patch_name: Unique identifier for the patch

    Returns:
        True if this is the first application, False if already patched
    """
    key = (patch_name, os.getpid())
    with _lock:
        if key in _PATCHED:
            return False
        _PATCHED[key] = True
        return True


def once(patch_name: str):
    """
    Decorator/guard for ensuring a patch runs only once per process.

    Usage:
        @once("requests")
        def patch_requests(...):
            ...

    Or as a guard:
        if not once.check("requests"):
            return  # Already patched
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if is_already_patched(patch_name):
                return  # Already patched, skip
            mark_as_patched(patch_name)
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


# Convenience method for checking
once.check = lambda name: mark_as_patched(name)
