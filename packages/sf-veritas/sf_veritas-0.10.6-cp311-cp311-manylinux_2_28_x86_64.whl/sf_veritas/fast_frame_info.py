"""
Ultra-fast frame introspection using C extension.
Falls back to Python if C extension is not available.
"""

import sysconfig
from functools import lru_cache
from typing import Optional, Tuple

# Try to import C extension
try:
    from . import _sfframeinfo

    _FAST_FRAME_OK = True
except ImportError:
    _sfframeinfo = None
    _FAST_FRAME_OK = False

# Fallback Python implementation
_STDLIB = sysconfig.get_paths()["stdlib"]
_SITE_TAGS = ("site-packages", "dist-packages")
_SKIP_PREFIXES = (_STDLIB, "/usr/local/lib/python", "/usr/lib/python")


@lru_cache(maxsize=512)
def _is_user_code_py(path: Optional[str]) -> bool:
    """Python fallback for checking if path is user code."""
    if not path or path.startswith("<"):
        return False
    for p in _SKIP_PREFIXES:
        if path.startswith(p):
            return False
    return not any(tag in path for tag in _SITE_TAGS)


def get_code_info(func) -> Optional[Tuple[str, int, str]]:
    """
    Extract (filename, lineno, name) from a function object.
    Returns None if not user code or extraction fails.

    Uses C extension if available for ~10x speedup.
    """
    if _FAST_FRAME_OK:
        try:
            result = _sfframeinfo.get_code_info(func)
            if result:
                # Result is (filename, lineno, name, is_user)
                return (result[0], result[1], result[2])
            return None
        except Exception:
            pass  # Fall back to Python

    # Python fallback
    try:
        code = getattr(func, "__code__", None)
        if not code:
            return None

        filename = code.co_filename
        if not _is_user_code_py(filename):
            return None

        return (filename, code.co_firstlineno, func.__name__)
    except Exception:
        return None


def get_frame_info(frame) -> Optional[Tuple[str, int, str]]:
    """
    Extract (filename, lineno, name) from a frame object.
    Returns None if not user code or extraction fails.

    Uses C extension if available for ~10x speedup.
    """
    if _FAST_FRAME_OK:
        try:
            result = _sfframeinfo.get_frame_info(frame)
            if result:
                # Result is (filename, lineno, name, is_user)
                return (result[0], result[1], result[2])
            return None
        except Exception:
            pass  # Fall back to Python

    # Python fallback
    try:
        code = frame.f_code
        filename = code.co_filename
        if not _is_user_code_py(filename):
            return None

        return (filename, frame.f_lineno, code.co_name)
    except Exception:
        return None


def is_user_code_func(func) -> bool:
    """
    Quick check if function is user code.

    Uses C extension if available for ~10x speedup.
    """
    if _FAST_FRAME_OK:
        try:
            return bool(_sfframeinfo.is_user_code_func(func))
        except Exception:
            pass

    # Python fallback
    try:
        code = getattr(func, "__code__", None)
        if not code:
            return False
        return _is_user_code_py(code.co_filename)
    except Exception:
        return False
