import fnmatch
import inspect
import sysconfig
from typing import Any, Callable, List, Optional, Set

_stdlib = sysconfig.get_paths()["stdlib"]


_ATTR_CANDIDATES = (
    "resolver",
    "func",
    "python_func",
    "_resolver",
    "wrapped_func",
    "__func",
)


def _is_user_code(path: Optional[str] = None) -> bool:
    return (
        bool(path)
        and not path.startswith(_stdlib)
        and "site-packages" not in path
        and "dist-packages" not in path
        and not path.startswith("<")
    )


def _unwrap_user_func(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Unwrap decorators & closures until we find your user function."""
    seen: Set[int] = set()
    queue = [fn]
    while queue:
        current = queue.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))

        if inspect.isfunction(current) and _is_user_code(current.__code__.co_filename):
            return current

        inner = getattr(current, "__wrapped__", None)
        if inner:
            queue.append(inner)

        for attr in _ATTR_CANDIDATES:
            attr_val = getattr(current, attr, None)
            if inspect.isfunction(attr_val):
                queue.append(attr_val)

        for cell in getattr(current, "__closure__", []) or []:
            cc = cell.cell_contents
            if inspect.isfunction(cc):
                queue.append(cc)

    return fn  # fallback


def should_skip_route(route_pattern: str, routes_to_skip: List[str]) -> bool:
    """
    Check if route should be skipped based on wildcard patterns.

    Supports Unix shell-style wildcards:
    - Exact match: "/healthz" matches "/healthz"
    - Wildcard *: "/he*" matches "/health", "/healthz", "/healthz/foo"
    - Wildcard ?: "/health?" matches "/healthz" but not "/health"
    - Character sets: "/health[z12]" matches "/healthz", "/health1", "/health2"

    Examples:
        - "/he*" → matches "/health", "/healthz", "/healthz/foo"
        - "/metrics*" → matches "/metrics", "/metrics/detailed"
        - "/api/internal/*" → matches "/api/internal/status", "/api/internal/debug"
        - "*/admin" → matches "/foo/admin", "/bar/admin"

    Args:
        route_pattern: Route pattern to check (e.g., "/healthz", "/log/{n}")
        routes_to_skip: List of patterns to skip (can contain wildcards)

    Returns:
        True if route should be skipped, False otherwise
    """
    if not routes_to_skip or not route_pattern:
        return False

    for skip_pattern in routes_to_skip:
        # Use fnmatch for Unix shell-style wildcards
        # This supports * (matches anything) and ? (matches single char)
        if fnmatch.fnmatch(route_pattern, skip_pattern):
            return True

    return False
