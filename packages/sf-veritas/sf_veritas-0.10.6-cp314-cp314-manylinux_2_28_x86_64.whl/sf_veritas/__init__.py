# Auto-enable LD_PRELOAD mode if libsfnettee.so is available
# This MUST be imported first, before any patches that check LD_PRELOAD
from . import _auto_preload  # noqa: F401

from .function_span_profiler import (
    skip_tracing,  # Backward compatibility
    skip_function_tracing,
    skip_network_tracing,
    capture_function_spans,
)
from .package_metadata import __version__
from .transmit_exception_to_sailfish import transmit_exception_to_sailfish
from .unified_interceptor import setup_interceptors, reinitialize_after_fork

__all__ = [
    "setup_interceptors",
    "transmit_exception_to_sailfish",
    "skip_tracing",  # Backward compatibility
    "skip_function_tracing",
    "skip_network_tracing",
    "capture_function_spans",
    "reinitialize_after_fork",
    "__version__",
]
