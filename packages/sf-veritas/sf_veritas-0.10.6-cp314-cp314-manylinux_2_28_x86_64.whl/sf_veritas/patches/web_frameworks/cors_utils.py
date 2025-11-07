"""
Utilities for automatically injecting Sailfish headers into CORS configurations.

This module provides helper functions to ensure that Sailfish's tracing and control
headers are always included in CORS allow-headers, without disrupting user configurations.
"""

from ...env_vars import SF_DEBUG

# Sailfish headers that must be allowed for proper operation
# Include both original case and lowercase variants for compatibility
SAILFISH_CORS_HEADERS = [
    "X-Sf3-Rid",  # Tracing header (request ID)
    "x-sf3-rid",  # Lowercase variant
    "X-Sf3-FunctionSpanCaptureOverride",  # Function span capture control
    "x-sf3-functionspancaptureoverride",  # Lowercase variant
]


def inject_sailfish_headers(user_headers):
    """
    Inject Sailfish headers into a user's CORS allow-headers configuration.

    Ensures Sailfish headers come first, followed by user headers, with de-duplication.

    Args:
        user_headers: User's existing allowed headers (can be None, string, list, tuple, or set)

    Returns:
        List with Sailfish headers prepended, or None if user_headers was None

    Safety:
        - Returns None if user_headers is None (doesn't enable CORS if not configured)
        - Preserves all user headers
        - De-duplicates while maintaining order
        - Handles "*" wildcard (leaves as-is)
        - Handles comma-separated strings (common CORS format)
    """
    # Don't enable CORS if user didn't configure it
    if user_headers is None:
        return None

    # If user allows all headers with wildcard, leave as-is
    if user_headers == "*" or (isinstance(user_headers, (list, tuple)) and "*" in user_headers):
        if SF_DEBUG:
            print(
                "[[cors_utils]] User has wildcard '*' in CORS headers, skipping injection",
                log=False
            )
        return user_headers

    # Convert to list for processing
    if isinstance(user_headers, str):
        # Handle comma-separated string (common CORS format: "foo, bar, baz")
        # Split by comma and strip whitespace
        user_headers = [h.strip() for h in user_headers.split(',') if h.strip()]
        if SF_DEBUG:
            print(
                f"[[cors_utils]] Parsed string headers: {user_headers}",
                log=False
            )
    elif isinstance(user_headers, (tuple, set)):
        user_headers = list(user_headers)
    elif not isinstance(user_headers, list):
        # Handle other iterables (but NOT strings, which we handled above)
        try:
            user_headers = list(user_headers)
        except TypeError:
            # Not iterable, return as-is
            if SF_DEBUG:
                print(
                    f"[[cors_utils]] Unexpected headers type: {type(user_headers)}, skipping injection",
                    log=False
                )
            return user_headers

    # Prepend Sailfish headers, then add user headers
    combined = SAILFISH_CORS_HEADERS + user_headers

    # De-duplicate while preserving order (dict.fromkeys preserves insertion order in Python 3.7+)
    # Convert to lowercase for comparison to handle case-insensitive duplicates
    seen = set()
    deduplicated = []
    for header in combined:
        header_lower = header.lower() if isinstance(header, str) else str(header).lower()
        if header_lower not in seen:
            seen.add(header_lower)
            deduplicated.append(header)

    if SF_DEBUG:
        added_headers = [h for h in SAILFISH_CORS_HEADERS if h.lower() in seen]
        print(
            f"[[cors_utils]] Injected Sailfish headers into CORS: {added_headers}",
            log=False
        )

    return deduplicated


def should_inject_headers(allow_headers_value):
    """
    Determine if we should inject Sailfish headers based on the current value.

    Args:
        allow_headers_value: The current allow_headers value

    Returns:
        bool: True if we should inject, False otherwise
    """
    # Don't inject if CORS isn't configured
    if allow_headers_value is None:
        return False

    # Don't inject if wildcard is already present
    if allow_headers_value == "*":
        return False

    if isinstance(allow_headers_value, (list, tuple, set)):
        if "*" in allow_headers_value:
            return False

    return True
