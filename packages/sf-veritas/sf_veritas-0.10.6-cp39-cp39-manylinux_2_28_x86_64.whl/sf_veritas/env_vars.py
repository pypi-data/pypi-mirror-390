import logging
import os

from .utils import strtobool

LITE_DEBUGGING = strtobool(os.getenv("LITE_DEBUGGING", "false"))
SF_DEBUG = strtobool(os.getenv("SF_DEBUG", "false"))
SF_DEBUG_TRACES = strtobool(os.getenv("SF_DEBUG_TRACES", "false"))
SF_INTERNAL = strtobool(os.getenv("SF_INTERNAL", "false"))
IS_SAILFISH_COLLECTOR = strtobool(os.getenv("IS_SAILFISH_COLLECTOR", "false"))
STRAWBERRY_DEBUG = strtobool(os.getenv("STRAWBERRY_DEBUG", "false"))
CAPTURE_STRAWBERRY_ERRORS_WITH_DATA = strtobool(
    os.getenv("CAPTURE_STRAWBERRY_ERRORS_WITH_DATA", "false")
)

# Log filtering - regex pattern to suppress logs from being sent to Sailfish
# Default: suppress successful (2xx) requests to /healthz and /graphql/ endpoints
SF_LOG_IGNORE_REGEX = os.getenv(
    "SF_LOG_IGNORE_REGEX", r"HTTP\s(POST|GET)\s(\/healthz|\/graphql\/)\s2\d{2}\s.*"
)
PRINT_CONFIGURATION_STATUSES = strtobool(
    os.getenv("PRINT_CONFIGURATION_STATUSES", "false")
)

# Parent death signal control (Linux only)
# Disables automatic registration for SIGTERM on parent process death
# Useful if customers have custom signal handling that conflicts
SF_DISABLE_PARENT_DEATH_SIGNAL = strtobool(
    os.getenv("SF_DISABLE_PARENT_DEATH_SIGNAL", "false")
)

# Parent process monitoring (cross-platform)
# Interval in milliseconds to check if parent process has died (orphaned)
# Lower = faster detection, higher = less CPU overhead
# Set to 0 to disable orphan detection
SF_PARENT_MONITOR_INTERVAL_MS = int(
    os.getenv("SF_PARENT_MONITOR_INTERVAL_MS", "100")  # Default: check every 100ms
)

# Exception Tools
SAILFISH_EXCEPTION_LOCALS_HIDE_SELF = strtobool(
    os.getenv("SAILFISH_EXCEPTION_LOCALS_HIDE_SELF", "true")
)
SAILFISH_EXCEPTION_LOCALS_HIDE_DUNDER = strtobool(
    os.getenv("SAILFISH_EXCEPTION_LOCALS_HIDE_DUNDER", "true")
)
SAILFISH_EXCEPTION_LOCALS_HIDE_SUNDER = strtobool(
    os.getenv("SAILFISH_EXCEPTION_LOCALS_HIDE_SUNDER", "true")
)
SAILFISH_EXCEPTION_STACK_DEPTH_LOCALS = int(
    os.getenv("SAILFISH_EXCEPTION_STACK_DEPTH_LOCALS", "5")
)
SAILFISH_EXCEPTION_STACK_DEPTH_CODE_TRACE_DEPTH = os.getenv(
    "SAILFISH_EXCEPTION_STACK_DEPTH_CODE_TRACE_DEPTH", "full"
)
SAILFISH_EXCEPTION_STACK_DEPTH_CODE_TRACE_TYPE = os.getenv(
    "SAILFISH_EXCEPTION_STACK_DEPTH_CODE_TRACE_TYPE", "line"
)
SAILFISH_EXCEPTION_STACK_DEPTH_CODE_TRACE_TYPE_AT_OFFENSIVE_CALL = os.getenv(
    "SAILFISH_EXCEPTION_STACK_DEPTH_CODE_TRACE_TYPE_AT_OFFENSIVE_CALL", "line"
)
SAILFISH_EXCEPTION_STACK_DEPTH_CODE_VALUES_AT_FULL_DEPTH_EXCEPTION = strtobool(
    os.getenv(
        "SAILFISH_EXCEPTION_STACK_DEPTH_CODE_VALUES_AT_FULL_DEPTH_EXCEPTION", "false"
    )
)
SAILFISH_EXCEPTION_LOCALS_TYPES_TO_IGNORE = os.getenv(
    "SAILFISH_EXCEPTION_LOCALS_TYPES_TO_IGNORE",
    "strawberry.types.info.Info,graphql.type.definition.GraphQLResolveInfo,strawberry.field.StrawberryField",
)
SAILFISH_EXCEPTION_FETCH_BEYOND_OFFENDER_DEPTH = int(
    os.getenv("SAILFISH_EXCEPTION_FETCH_BEYOND_OFFENDER_DEPTH", "3")
)
SAILFISH_EXCEPTION_FETCH_LOCALS_BEYOND_OFFENDER_DEPTH = int(
    os.getenv(
        "SAILFISH_EXCEPTION_FETCH_LOCALS_BEYOND_OFFENDER_DEPTH", "5"
    )  # Sibyl launch - lower this
)
SAILFISH_EXCEPTION_FETCH_ABOVE_OFFENDER_DEPTH = int(
    os.getenv(
        "SAILFISH_EXCEPTION_FETCH_ABOVE_OFFENDER_DEPTH", "3"
    )  # Sibyl launch - lower this
)
SAILFISH_EXCEPTION_FETCH_LOCALS_ABOVE_OFFENDER_DEPTH = int(
    os.getenv(
        "SAILFISH_EXCEPTION_FETCH_LOCALS_ABOVE_OFFENDER_DEPTH", "-1"
    )  # Sibyl launch - lower this
)
SAILFISH_EXCEPTION_FETCH_ABOVE_OFFENDER_INCLUDE_INSTALLED_PACKAGES = strtobool(
    os.getenv(
        "SAILFISH_EXCEPTION_FETCH_ABOVE_OFFENDER_INCLUDE_INSTALLED_PACKAGES", "false"
    )
)


def get_log_level():
    if LOG_LEVEL_ENV_VAR == "DEBUG":
        return logging.DEBUG
    if LOG_LEVEL_ENV_VAR == "INFO":
        return logging.INFO
    if LOG_LEVEL_ENV_VAR == "WARN":
        return logging.WARN
    if LOG_LEVEL_ENV_VAR == "ERROR":
        return logging.ERROR
    return logging.CRITICAL


LOG_LEVEL_ENV_VAR = os.getenv("LOG_LEVEL", "INFO")
LOG_LEVEL = get_log_level()

# Function Span Serialization
SF_FUNCSPAN_PARSE_JSON_STRINGS = strtobool(
    os.getenv("SF_FUNCSPAN_PARSE_JSON_STRINGS", "true")
)

# Function Span Capture Control - Granular configuration
SF_FUNCSPAN_CAPTURE_ARGUMENTS = strtobool(
    os.getenv("SF_FUNCSPAN_CAPTURE_ARGUMENTS", "true")
)
SF_FUNCSPAN_CAPTURE_RETURN_VALUE = strtobool(
    os.getenv("SF_FUNCSPAN_CAPTURE_RETURN_VALUE", "true")
)

# Separate size limits for arguments vs return values
SF_FUNCSPAN_ARG_LIMIT_MB = int(os.getenv("SF_FUNCSPAN_ARG_LIMIT_MB", "1"))
SF_FUNCSPAN_RETURN_LIMIT_MB = int(os.getenv("SF_FUNCSPAN_RETURN_LIMIT_MB", "1"))

# Auto-capture child functions (default: true)
# When false, only capture top-level functions, not their children
SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS = strtobool(
    os.getenv("SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS", "true")
)

# Two-tier profiler control:
# SF_ENABLE_PROFILER: Gates installation of profiler hooks (default: false)
# SF_ENABLE_FUNCTION_SPANS: Master kill switch for capture/transmission (default: true)
SF_ENABLE_PROFILER = strtobool(os.getenv("SF_ENABLE_PROFILER", "false"))

# Include Django view functions in tracing (default: false)
# Django view functions are typically framework entry points and already traced by web framework instrumentation
# Set to true if you want detailed function-level tracing inside Django views
SF_FUNCSPAN_INCLUDE_DJANGO_VIEW_FUNCTIONS = strtobool(
    os.getenv("SF_FUNCSPAN_INCLUDE_DJANGO_VIEW_FUNCTIONS", "false")
)

# Capture spans from installed packages (site-packages, stdlib, etc.) (default: false)
# When false, only captures user code; when true, also captures installed libraries
SF_FUNCSPAN_CAPTURE_INSTALLED_PACKAGES = strtobool(
    os.getenv("SF_FUNCSPAN_CAPTURE_INSTALLED_PACKAGES", "false")
)

# Capture spans from sf_veritas telemetry code itself (default: false)
# When false, skips sf_veritas code; when true, captures our own telemetry code
SF_FUNCSPAN_CAPTURE_SF_VERITAS = strtobool(
    os.getenv("SF_FUNCSPAN_CAPTURE_SF_VERITAS", "false")
)

# Network Hop I/O Capture - OTEL-style defaults (bodies OFF for performance)
SF_NETWORKHOP_CAPTURE_ENABLED = strtobool(
    os.getenv("SF_NETWORKHOP_CAPTURE_ENABLED", "true")  # OTEL doesn't capture bodies
)
SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS = strtobool(
    os.getenv("SF_NETWORKHOP_CAPTURE_REQUEST_HEADERS", "false")
)
SF_NETWORKHOP_CAPTURE_REQUEST_BODY = strtobool(
    os.getenv(
        "SF_NETWORKHOP_CAPTURE_REQUEST_BODY", "false"
    )  # OTEL doesn't capture bodies
)
SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS = strtobool(
    os.getenv("SF_NETWORKHOP_CAPTURE_RESPONSE_HEADERS", "false")
)
SF_NETWORKHOP_CAPTURE_RESPONSE_BODY = strtobool(
    os.getenv(
        "SF_NETWORKHOP_CAPTURE_RESPONSE_BODY", "false"
    )  # OTEL doesn't capture bodies
)
SF_NETWORKHOP_REQUEST_LIMIT_MB = int(os.getenv("SF_NETWORKHOP_REQUEST_LIMIT_MB", "1"))
SF_NETWORKHOP_RESPONSE_LIMIT_MB = int(os.getenv("SF_NETWORKHOP_RESPONSE_LIMIT_MB", "1"))

# Route-based suppression for inbound network tracing (comma-separated route patterns with wildcard support)
# Example: "/healthz, /metrics, /admin/*, /api/v1/status*"
# Supports wildcards: * (matches any sequence) and ? (matches single character)
SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES = os.getenv(
    "SF_DISABLE_INBOUND_NETWORK_TRACING_ON_ROUTES", ""
)
