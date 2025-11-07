"""
Function span profiler for collecting function call telemetry.

This module provides a high-performance profiler that captures function calls,
arguments, return values, and execution timing using a C extension.
"""

import functools
import inspect
import json
import sys
from typing import Any, Callable, Dict, List, Optional, Set

from . import app_config
from .env_vars import SF_DEBUG

try:
    from . import _sffuncspan

    _HAS_NATIVE = True
except ImportError:
    _HAS_NATIVE = False

from .thread_local import get_or_set_sf_trace_id

# Marker attribute for skipping function tracing
_SKIP_FUNCTION_TRACING_ATTR = "_sf_skip_function_tracing"


def skip_function_tracing(func: Callable) -> Callable:
    """
    Decorator to skip function span tracing for a specific function.

    When using automatic profiling (sys.setprofile), this decorator marks
    a function to be completely skipped by the function span profiler.

    Usage:
        @skip_function_tracing
        def internal_helper():
            # This function won't have function spans traced
            ...

    Note: This has no effect when using manual @profile_function decoration.
    """
    setattr(func, _SKIP_FUNCTION_TRACING_ATTR, True)
    return func


# Backward compatibility alias
skip_tracing = skip_function_tracing


def skip_network_tracing(func: Callable) -> Callable:
    """
    Decorator to skip network request/response tracing for a specific endpoint.

    This decorator wraps the function with the suppress_network_recording context,
    preventing all outbound HTTP/HTTPS requests made during the function execution
    from being captured and sent to the Sailfish backend.

    The actual network requests still go out normally - they're just not observed
    by the telemetry system.

    Usage:
        @skip_network_tracing
        @app.get("/healthz")
        def healthz():
            # Network requests in here won't be traced
            return {"ok": True}

        # Or for FastAPI with path parameters:
        @app.get("/admin/stats")
        @skip_network_tracing
        async def admin_stats():
            # Admin endpoint - don't trace network calls
            ...

    Note: For async functions, this works correctly with async/await.
    """
    from .thread_local import suppress_network_recording

    if inspect.iscoroutinefunction(func):
        # Async function
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with suppress_network_recording():
                return await func(*args, **kwargs)

        # Mark function so web frameworks can skip registration
        async_wrapper._sf_skip_tracing = True
        if SF_DEBUG and app_config._interceptors_initialized:
            print(
                "[[skip_network_tracing]] skipping tracing for async endpoint",
                log=False,
            )
        return async_wrapper
    else:
        # Sync function
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with suppress_network_recording():
                return func(*args, **kwargs)

        # Mark function so web frameworks can skip registration
        sync_wrapper._sf_skip_tracing = True
        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[skip_network_tracing]] skipping tracing for endpoint", log=False)
        return sync_wrapper


def profile_function(
    func: Optional[Callable] = None,
    *,
    capture_args: bool = False,
    capture_return: bool = True,
):
    """
    Decorator for manual function profiling with ultra-low overhead (~0.001-0.01%).

    This provides an alternative to automatic profiling via sys.setprofile,
    offering much lower overhead at the cost of requiring explicit decoration.

    Args:
        func: Function to decorate (when used without arguments)
        capture_args: Capture function arguments (adds ~10µs overhead)
        capture_return: Capture return value (adds ~5µs overhead)

    Usage:
        # Simple usage (fastest)
        @profile_function
        def my_function():
            ...

        # With argument capture
        @profile_function(capture_args=True)
        def my_function(x, y):
            ...

        # Without return capture (faster)
        @profile_function(capture_return=False)
        def my_function():
            ...

    Overhead:
        - No capture: ~1-2µs per call
        - With args: ~10-15µs per call
        - With return: ~5-10µs per call
        - With both: ~15-25µs per call

    This is 2000-5000x faster than sys.setprofile-based profiling!
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not _HAS_NATIVE:
                return fn(*args, **kwargs)

            # Generate span ID (fast: ~50ns)
            span_id = _sffuncspan.generate_span_id()
            parent_span_id = _sffuncspan.peek_parent_span_id()
            _sffuncspan.push_span(span_id)

            # Capture arguments if requested
            arguments_json = "{}"
            if capture_args:
                try:
                    # Build arguments dict
                    arg_names = fn.__code__.co_varnames[: fn.__code__.co_argcount]
                    args_dict = {}
                    for i, name in enumerate(arg_names):
                        if i < len(args):
                            args_dict[name] = str(args[i])[:100]  # Limit size
                    for key, value in kwargs.items():
                        args_dict[key] = str(value)[:100]
                    arguments_json = json.dumps(args_dict)
                except:
                    arguments_json = '{"_error": "failed to capture args"}'

            # Record start time (fast: ~100ns)
            start_ns = _sffuncspan.get_epoch_ns()

            # Execute function
            try:
                result = fn(*args, **kwargs)
                exception_occurred = False
            except Exception as e:
                exception_occurred = True
                result = None
                raise
            finally:
                # Record end time
                end_ns = _sffuncspan.get_epoch_ns()
                duration_ns = end_ns - start_ns

                # Pop span
                _sffuncspan.pop_span()

                # Capture return value if requested and no exception
                return_value_json = None
                if capture_return and not exception_occurred and result is not None:
                    try:
                        return_value_json = json.dumps(str(result)[:100])
                    except:
                        return_value_json = None

                # Record span (includes sampling check in C)
                try:
                    _, session_id = get_or_set_sf_trace_id()
                    _sffuncspan.record_span(
                        session_id=str(session_id),
                        span_id=span_id,
                        parent_span_id=parent_span_id,
                        file_path=fn.__code__.co_filename,
                        line_number=fn.__code__.co_firstlineno,
                        column_number=0,
                        function_name=fn.__name__,
                        arguments_json=arguments_json,
                        return_value_json=return_value_json,
                        start_time_ns=start_ns,
                        duration_ns=duration_ns,
                    )
                except:
                    pass  # Fail silently to not impact application

            return result

        return wrapper

    # Support both @profile_function and @profile_function()
    if func is None:
        return decorator
    else:
        return decorator(func)


def capture_function_spans(
    func: Optional[Callable] = None,
    *,
    include_arguments: Optional[bool] = None,
    include_return_value: Optional[bool] = None,
    arg_limit_mb: Optional[int] = None,
    return_limit_mb: Optional[int] = None,
    autocapture_all_children: Optional[bool] = None,
    sample_rate: Optional[float] = None,
):
    """
    Decorator to override function span capture settings for a specific function.

    This decorator has second-highest priority (only HTTP headers override it).
    When applied, it registers the function's config with the C extension for
    ultra-fast runtime lookups (<5ns).

    Args:
        func: Function to decorate (when used without arguments)
        include_arguments: Capture function arguments (default: from env SF_FUNCSPAN_CAPTURE_ARGUMENTS)
        include_return_value: Capture return value (default: from env SF_FUNCSPAN_CAPTURE_RETURN_VALUE)
        arg_limit_mb: Max size for arguments in MB (default: from env SF_FUNCSPAN_ARG_LIMIT_MB)
        return_limit_mb: Max size for return value in MB (default: from env SF_FUNCSPAN_RETURN_LIMIT_MB)
        autocapture_all_children: Capture all child functions (default: from env SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS)
        sample_rate: Sampling rate 0.0-1.0 (0.0=disabled, 1.0=all) (default: 1.0)

    Usage:
        # Use defaults from environment
        @capture_function_spans
        def my_function():
            ...

        # Override specific settings
        @capture_function_spans(include_arguments=False, sample_rate=0.5)
        def sensitive_function(api_key, password):
            ...

        # Capture only this function, not children
        @capture_function_spans(autocapture_all_children=False)
        def top_level_handler():
            ...

    Note:
        - No runtime overhead (no wrapper!) - config registered at decoration time
        - Works with automatic profiling (sys.setprofile) - decorator is not a wrapper
        - Override via HTTP header X-Sf3-FunctionSpanCaptureOverride for per-request control
    """

    def decorator(fn: Callable) -> Callable:
        try:
            from . import _sffuncspan_config
        except ImportError:
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[DEBUG]] capture_function_spans: Config extension not available, decorator has no effect",
                    log=False,
                )
            return fn  # No-op if config extension not available

        # Build config dict (None values mean "use default")
        config = {}

        if include_arguments is not None:
            config["include_arguments"] = include_arguments

        if include_return_value is not None:
            config["include_return_value"] = include_return_value

        if arg_limit_mb is not None:
            config["arg_limit_mb"] = arg_limit_mb

        if return_limit_mb is not None:
            config["return_limit_mb"] = return_limit_mb

        if autocapture_all_children is not None:
            config["autocapture_all_children"] = autocapture_all_children

        if sample_rate is not None:
            config["sample_rate"] = sample_rate

        # Register with C extension (only if we have config to set)
        if config:
            try:
                file_path = fn.__code__.co_filename
                func_name = fn.__name__
                _sffuncspan_config.add_function(file_path, func_name, config)

                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[DEBUG]] capture_function_spans: Registered {file_path}:{func_name} with config {config}",
                        log=False,
                    )

                # Pre-populate the profiler cache to avoid Python callbacks during profiling
                try:
                    from . import _sffuncspan

                    # Get config values with defaults
                    from .env_vars import (
                        SF_FUNCSPAN_ARG_LIMIT_MB,
                        SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS,
                        SF_FUNCSPAN_CAPTURE_ARGUMENTS,
                        SF_FUNCSPAN_CAPTURE_RETURN_VALUE,
                        SF_FUNCSPAN_RETURN_LIMIT_MB,
                    )

                    inc_args = int(
                        config.get("include_arguments", SF_FUNCSPAN_CAPTURE_ARGUMENTS)
                    )
                    inc_ret = int(
                        config.get(
                            "include_return_value", SF_FUNCSPAN_CAPTURE_RETURN_VALUE
                        )
                    )
                    autocap = int(
                        config.get(
                            "autocapture_all_children",
                            SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS,
                        )
                    )
                    arg_lim = int(config.get("arg_limit_mb", SF_FUNCSPAN_ARG_LIMIT_MB))
                    ret_lim = int(
                        config.get("return_limit_mb", SF_FUNCSPAN_RETURN_LIMIT_MB)
                    )
                    samp_rate = float(config.get("sample_rate", 1.0))

                    _sffuncspan.cache_config(
                        file_path,
                        func_name,
                        inc_args,
                        inc_ret,
                        autocap,
                        arg_lim,
                        ret_lim,
                        samp_rate,
                    )

                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[DEBUG]] capture_function_spans: Cached config for {file_path}:{func_name}",
                            log=False,
                        )
                except Exception as e:
                    if SF_DEBUG and app_config._interceptors_initialized:
                        print(
                            f"[[DEBUG]] capture_function_spans: Failed to cache config: {e}",
                            log=False,
                        )
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[DEBUG]] capture_function_spans: Failed to register function config: {e}",
                        log=False,
                    )

        return fn  # Return original function (no wrapper!)

    # Support both @capture_function_spans and @capture_function_spans()
    if func is None:
        return decorator
    else:
        return decorator(func)


class FunctionSpanProfiler:
    """
    High-performance function span profiler using sys.setprofile.

    Captures:
    - Function call location (file, line, column)
    - Function arguments (names and values)
    - Return values
    - Execution timing (start time and duration in nanoseconds)
    - Hierarchical span relationships (parent_span_id)
    """

    def __init__(
        self,
        url: str,
        query: str,
        api_key: str,
        service_uuid: str,
        library: str = "sf_veritas",
        version: str = "1.0.0",
        http2: bool = True,
        variable_capture_size_limit_mb: int = 1,
        capture_from_installed_libraries: Optional[List[str]] = None,
        sample_rate: float = 1.0,
        enable_sampling: bool = False,
        include_django_view_functions: bool = False,
    ):
        """
        Initialize the function span profiler.

        Args:
            url: GraphQL endpoint URL
            query: GraphQL mutation query for function spans
            api_key: API key for authentication
            service_uuid: Service UUID
            library: Library name (default: "sf_veritas")
            version: Library version (default: "1.0.0")
            http2: Use HTTP/2 (default: True)
            variable_capture_size_limit_mb: Max size to capture per variable (default: 1MB)
            capture_from_installed_libraries: List of library prefixes to capture from
            sample_rate: Sampling probability 0.0-1.0 (default: 1.0 = capture all, 0.1 = 10%)
            enable_sampling: Enable sampling (default: False)
        """
        if not _HAS_NATIVE:
            raise RuntimeError("Native _sffuncspan extension not available")

        self._initialized = False
        self._active = False
        self._previous_profiler = None  # Store previous profiler for chaining
        self._capture_from_installed_libraries: Set[str] = set(
            capture_from_installed_libraries or []
        )
        self._variable_capture_size_limit_mb = variable_capture_size_limit_mb

        # Track active function calls with their start times and span IDs
        self._active_calls: Dict[int, Dict[str, Any]] = {}

        # Initialize the C extension
        success = _sffuncspan.init(
            url=url,
            query=query,
            api_key=api_key,
            service_uuid=service_uuid,
            library=library,
            version=version,
            http2=1 if http2 else 0,
        )

        if not success:
            raise RuntimeError("Failed to initialize _sffuncspan")

        # Get configuration from environment variables
        from .env_vars import (
            SF_FUNCSPAN_ARG_LIMIT_MB,
            SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS,
            SF_FUNCSPAN_CAPTURE_ARGUMENTS,
            SF_FUNCSPAN_CAPTURE_INSTALLED_PACKAGES,
            SF_FUNCSPAN_CAPTURE_RETURN_VALUE,
            SF_FUNCSPAN_CAPTURE_SF_VERITAS,
            SF_FUNCSPAN_PARSE_JSON_STRINGS,
            SF_FUNCSPAN_RETURN_LIMIT_MB,
        )

        # Store DEFAULT capture flags (used as fallback if config lookup fails)
        self._default_capture_arguments = SF_FUNCSPAN_CAPTURE_ARGUMENTS
        self._default_capture_return_value = SF_FUNCSPAN_CAPTURE_RETURN_VALUE
        self._default_arg_limit_mb = SF_FUNCSPAN_ARG_LIMIT_MB
        self._default_return_limit_mb = SF_FUNCSPAN_RETURN_LIMIT_MB
        self._default_autocapture_all_children = (
            SF_FUNCSPAN_AUTOCAPTURE_ALL_CHILD_FUNCTIONS
        )

        # Try to import config system
        try:
            from . import _sffuncspan_config

            self._config_system = _sffuncspan_config
        except ImportError:
            self._config_system = None
            if SF_DEBUG and app_config._interceptors_initialized:
                print(
                    "[[DEBUG]] FunctionSpanProfiler: Config system not available, using defaults",
                    log=False,
                )

        # Track call depth for top-level-only mode
        self._call_depth = 0

        # Configure the profiler settings
        print("[FUNCSPAN_INIT] About to call _sffuncspan.configure()", flush=True)
        _sffuncspan.configure(
            variable_capture_size_limit_mb=variable_capture_size_limit_mb,
            capture_from_installed_libraries=list(
                self._capture_from_installed_libraries
            ),
            sample_rate=sample_rate,
            enable_sampling=enable_sampling,
            parse_json_strings=SF_FUNCSPAN_PARSE_JSON_STRINGS,
            capture_arguments=SF_FUNCSPAN_CAPTURE_ARGUMENTS,
            capture_return_value=SF_FUNCSPAN_CAPTURE_RETURN_VALUE,
            arg_limit_mb=SF_FUNCSPAN_ARG_LIMIT_MB,
            return_limit_mb=SF_FUNCSPAN_RETURN_LIMIT_MB,
            include_django_view_functions=include_django_view_functions,
        )

        print(f"[FUNCSPAN_INIT] About to call set_capture_installed_packages({SF_FUNCSPAN_CAPTURE_INSTALLED_PACKAGES})", flush=True)
        # Set capture_installed_packages flag in C extension
        _sffuncspan.set_capture_installed_packages(SF_FUNCSPAN_CAPTURE_INSTALLED_PACKAGES)
        print("[FUNCSPAN_INIT] Successfully called set_capture_installed_packages", flush=True)

        print(f"[FUNCSPAN_INIT] About to call set_capture_sf_veritas({SF_FUNCSPAN_CAPTURE_SF_VERITAS})", flush=True)
        # Set capture_sf_veritas flag in C extension
        _sffuncspan.set_capture_sf_veritas(SF_FUNCSPAN_CAPTURE_SF_VERITAS)
        print("[FUNCSPAN_INIT] Successfully called set_capture_sf_veritas", flush=True)

        self._initialized = True

    def _get_config_for_function(self, file_path: str, func_name: str) -> Dict:
        """
        Get configuration for a specific function.

        Looks up config from the C extension's config system, which includes:
        - HTTP header overrides (highest priority)
        - Decorator configs
        - Function-level configs from .sailfish files
        - File pragmas
        - File-level configs
        - Directory configs

        Args:
            file_path: Path to the file containing the function
            func_name: Name of the function

        Returns:
            Dict with config keys: include_arguments, include_return_value,
            arg_limit_mb, return_limit_mb, autocapture_all_children, sample_rate
        """
        if self._config_system:
            try:
                return self._config_system.get(file_path, func_name)
            except Exception as e:
                if SF_DEBUG and app_config._interceptors_initialized:
                    print(
                        f"[[DEBUG]] Failed to get config for {file_path}::{func_name}: {e}",
                        log=False,
                    )

        # Fallback to defaults if config system not available or lookup fails
        return {
            "include_arguments": self._default_capture_arguments,
            "include_return_value": self._default_capture_return_value,
            "arg_limit_mb": self._default_arg_limit_mb,
            "return_limit_mb": self._default_return_limit_mb,
            "autocapture_all_children": self._default_autocapture_all_children,
            "sample_rate": 1.0,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self._initialized:
            return {}
        return _sffuncspan.get_stats()

    def reset_stats(self):
        """Reset performance statistics."""
        if self._initialized:
            _sffuncspan.reset_stats()

    def start(self):
        """Start profiling function calls using ultra-fast C profiler."""
        print("[FUNCSPAN_START] Entering start() method", flush=True)
        if not self._initialized:
            raise RuntimeError("Profiler not initialized")

        if self._active:
            return  # Already active

        print("[FUNCSPAN_START] About to import threading", flush=True)

        # Use ultra-fast C profiler instead of Python sys.setprofile!
        # This is 100-1000x faster because:
        # 1. No Python callback overhead
        # 2. No frame attribute lookups in Python
        # 3. Direct C string operations
        # 4. Pre-built JSON in C
        # 5. Lock-free ring buffer
        try:
            import threading

            print("[FUNCSPAN_START] About to call _sffuncspan.start_c_profiler()", flush=True)
            # Start C profiler for current thread
            _sffuncspan.start_c_profiler()

            print("[FUNCSPAN_START] C profiler started, setting up threading.setprofile", flush=True)
            # For new threads, we need to set profiler via threading.setprofile
            # This is a lightweight wrapper that just calls the C profiler
            def _thread_profiler_wrapper():
                """Lightweight wrapper to enable C profiler on new threads."""
                _sffuncspan.start_c_profiler()

            # Set for all future threads (FastAPI workers, etc.)
            threading.setprofile(
                lambda *args: _sffuncspan.start_c_profiler() if args else None
            )

            print("[FUNCSPAN_START] Setting _active=True", flush=True)
            self._active = True
            print("[FUNCSPAN_START] Successfully started profiler!", flush=True)
        except Exception as e:
            print(f"[[FUNCSPAN_ERROR]] Failed to start C profiler: {e}", log=False)
            raise

    def stop(self):
        """Stop profiling function calls."""
        if not self._active:
            return

        if SF_DEBUG and app_config._interceptors_initialized:
            print("[[FUNCSPAN_DEBUG]] Stopping C profiler", log=False)

        import threading

        _sffuncspan.stop_c_profiler()
        threading.setprofile(None)
        self._active = False

    def shutdown(self):
        """Shutdown the profiler and cleanup resources."""
        self.stop()
        if self._initialized:
            _sffuncspan.shutdown()
            self._initialized = False

    def _should_capture_frame(self, frame) -> bool:
        """
        Determine if we should capture this frame.

        Args:
            frame: Python frame object

        Returns:
            True if we should capture, False otherwise
        """
        # Get the function name and file path WHERE THE FUNCTION IS DEFINED
        # This is the key - frame.f_code.co_filename tells us where the function's
        # code actually lives, not where it's being called from
        func_name = frame.f_code.co_name
        filename = frame.f_code.co_filename

        # Exclude private/dunder methods (__enter__, __exit__, __init__, etc.)
        if func_name.startswith("__") and func_name.endswith("__"):
            return False

        # ALWAYS exclude these paths (Python internals, site-packages, etc.)
        # This is THE critical check - if the function is DEFINED in site-packages,
        # we don't capture it, regardless of where it's called from
        exclude_patterns = [
            "site-packages",  # Functions defined in site-packages
            "dist-packages",  # Functions defined in dist-packages
            "/lib/python",  # Python stdlib
            "\\lib\\python",  # Python stdlib (Windows)
            "<frozen",  # Frozen modules
            "<string>",  # exec() and eval() generated code
            "importlib",  # Import machinery
            "_bootstrap",  # Bootstrap code
            "sf_veritas",  # Don't capture our own telemetry code!
        ]

        for pattern in exclude_patterns:
            if pattern in filename:
                return False

        # If library filter is set, only capture those libraries
        if self._capture_from_installed_libraries:
            # Check if it matches any of the capture prefixes
            for lib_prefix in self._capture_from_installed_libraries:
                if lib_prefix in filename:
                    return True
            return False

        # No filter set - capture everything except excluded patterns
        return True

    def _serialize_value(self, value: Any, max_size: int) -> str:
        """
        Serialize a value to JSON, respecting size limits.

        Uses ultra-fast C implementation when available (<1µs), falls back to Python.

        Args:
            value: Value to serialize
            max_size: Maximum size in bytes

        Returns:
            JSON string representation
        """
        # Use ultra-fast C serialization when available
        if _HAS_NATIVE:
            try:
                return _sffuncspan.serialize_value(value, max_size)
            except Exception:
                pass  # Fall back to Python implementation

        # Python fallback implementation (slower but always works)
        try:
            # First try: direct JSON serialization for primitives and built-ins
            serialized = json.dumps(value)
            if len(serialized) > max_size:
                return json.dumps({"_truncated": True, "_size": len(serialized)})
            return serialized
        except (TypeError, ValueError):
            pass  # Try introspection

        # Second try: Introspect the object to extract meaningful data
        type_name = type(value).__name__
        module_name = type(value).__module__

        try:
            result = {
                "_type": (
                    f"{module_name}.{type_name}"
                    if module_name != "builtins"
                    else type_name
                )
            }

            # Try __dict__ first (works for most custom objects)
            if hasattr(value, "__dict__"):
                try:
                    obj_dict = {}
                    for key, val in value.__dict__.items():
                        # Skip private/dunder attributes and callables (methods, functions)
                        if not key.startswith("_") and not callable(val):
                            try:
                                # Recursively serialize nested values (with size limit)
                                obj_dict[key] = json.loads(
                                    self._serialize_value(val, max_size // 10)
                                )
                            except:
                                obj_dict[key] = str(val)[:100]
                    if obj_dict:
                        result["attributes"] = obj_dict
                except:
                    pass

            # Try __slots__ if available
            if hasattr(value, "__slots__"):
                try:
                    slots_dict = {}
                    for slot in value.__slots__:
                        if hasattr(value, slot) and not slot.startswith("_"):
                            try:
                                slot_val = getattr(value, slot)
                                slots_dict[slot] = json.loads(
                                    self._serialize_value(slot_val, max_size // 10)
                                )
                            except:
                                slots_dict[slot] = str(getattr(value, slot, None))[:100]
                    if slots_dict:
                        result["slots"] = slots_dict
                except:
                    pass

            # Try to get useful properties/methods that might reveal data
            # Look for common patterns like .data, .value, .content, .body, .result
            for attr_name in [
                "data",
                "value",
                "content",
                "body",
                "result",
                "message",
                "text",
            ]:
                if hasattr(value, attr_name):
                    try:
                        attr_val = getattr(value, attr_name)
                        if not callable(attr_val):
                            result[attr_name] = json.loads(
                                self._serialize_value(attr_val, max_size // 10)
                            )
                    except:
                        pass

            # Add a safe repr as fallback
            try:
                result["_repr"] = str(value)[:200]
            except:
                result["_repr"] = f"<{type_name} object>"

            serialized = json.dumps(result)
            if len(serialized) > max_size:
                return json.dumps(
                    {
                        "_truncated": True,
                        "_size": len(serialized),
                        "_type": result["_type"],
                    }
                )
            return serialized

        except Exception as e:
            # Ultimate fallback
            try:
                return json.dumps(
                    {
                        "_error": "serialization failed",
                        "_type": (
                            f"{module_name}.{type_name}"
                            if module_name != "builtins"
                            else type_name
                        ),
                        "_repr": str(value)[:100] if str(value) else "<no repr>",
                    }
                )
            except:
                return json.dumps({"_error": "complete serialization failure"})

    def _capture_arguments(self, frame, arg_limit_mb: Optional[int] = None) -> str:
        """
        Capture function arguments as JSON.

        Args:
            frame: Python frame object
            arg_limit_mb: Max size for arguments in MB (default: from config)

        Returns:
            JSON string with argument names and values
        """
        code = frame.f_code
        arg_count = code.co_argcount + code.co_kwonlyargcount

        # Handle methods (skip 'self' or 'cls' if present)
        var_names = code.co_varnames[:arg_count]

        arguments = {}
        # Use arg-specific limit instead of general variable limit
        if arg_limit_mb is None:
            arg_limit_mb = self._default_arg_limit_mb
        max_size = arg_limit_mb * 1048576

        for var_name in var_names:
            if var_name in frame.f_locals:
                value = frame.f_locals[var_name]
                arguments[var_name] = self._serialize_value(
                    value, max_size // len(var_names) if var_names else max_size
                )

        return json.dumps(arguments)

    def _profile_callback(self, frame, event: str, arg):
        """
        Profile callback function called by sys.setprofile.

        Args:
            frame: Current frame
            event: Event type ('call', 'return', 'exception', etc.)
            arg: Event-specific argument
        """
        # DEBUG: Check if we're even being called
        code = frame.f_code
        func_name = code.co_name
        if SF_DEBUG and func_name == "simple_calculation":
            print(
                f"[[FUNCSPAN_DEBUG]] *** OUR CALLBACK WAS CALLED FOR {func_name}! event={event}",
                log=False,
            )

        # Chain to previous profiler first (if any)
        if self._previous_profiler is not None:
            try:
                self._previous_profiler(frame, event, arg)
            except Exception:
                pass  # Ignore errors in chained profiler

        # Fast path: Check if function has @skip_tracing decorator
        filename = code.co_filename

        # DEBUG: Log when we see simple_calculation
        if SF_DEBUG and func_name == "simple_calculation" and event == "call":
            print(
                f"[[FUNCSPAN_DEBUG]] Callback triggered: {func_name} in {filename}, event={event}",
                log=False,
            )
            print(
                f"[[FUNCSPAN_DEBUG]] Current profiler is: {sys.getprofile()}", log=False
            )
            print(f"[[FUNCSPAN_DEBUG]] We are: {self._profile_callback}", log=False)

        # Check if this function should be skipped
        # Look for the function in globals to check for skip attribute
        if "self" in frame.f_locals:
            # Method call
            obj = frame.f_locals["self"]
            if hasattr(obj, func_name):
                func = getattr(obj, func_name)
                if hasattr(func, _SKIP_FUNCTION_TRACING_ATTR):
                    return
        elif func_name in frame.f_globals:
            func = frame.f_globals[func_name]
            if callable(func) and hasattr(func, _SKIP_FUNCTION_TRACING_ATTR):
                return

        # Fast path: Check if we should even process this frame
        should_capture = self._should_capture_frame(frame)

        # DEBUG: Log capture decision for simple_calculation
        if SF_DEBUG and func_name == "simple_calculation" and event == "call":
            print(f"[[FUNCSPAN_DEBUG]] Should capture? {should_capture}", log=False)

        if not should_capture:
            return

        if event == "call":
            self._handle_call(frame)
        elif event == "return":
            self._handle_return(frame, arg)
        elif event == "exception":
            # We can choose to handle exceptions differently if needed
            pass

    def _handle_call(self, frame):
        """
        Handle a function call event.

        Args:
            frame: Python frame object
        """
        if not self._should_capture_frame(frame):
            return

        # Get frame info early for config lookup
        code = frame.f_code
        file_path = code.co_filename
        function_name = code.co_name

        # Look up config for this function to check autocapture setting
        config = self._get_config_for_function(file_path, function_name)

        # Check if we should skip child functions
        should_skip_child = False
        if (
            not config.get(
                "autocapture_all_children", self._default_autocapture_all_children
            )
            and self._call_depth > 0
        ):
            # We're inside a captured function and child capture is disabled
            should_skip_child = True

        # Increment call depth (even for skipped calls, so we track nesting)
        self._call_depth += 1

        # If we're skipping this child function, mark it but don't capture
        if should_skip_child:
            frame_id = id(frame)
            self._active_calls[frame_id] = {
                "captured": False
            }  # Not captured, just tracking
            return

        # Generate span ID
        span_id = _sffuncspan.generate_span_id()

        # Get parent span ID from the stack
        parent_span_id = _sffuncspan.peek_parent_span_id()

        # Push current span onto stack
        _sffuncspan.push_span(span_id)

        # Record start time
        start_time_ns = _sffuncspan.get_epoch_ns()

        # Get remaining frame info (file_path, function_name already extracted above)
        line_number = frame.f_lineno
        column_number = 0  # Python doesn't provide column info easily

        # Config was already looked up above for autocapture check, reuse it

        # Capture arguments (or skip if disabled)
        if config["include_arguments"]:
            arg_limit_mb = config.get("arg_limit_mb", self._default_arg_limit_mb)
            arguments_json = self._capture_arguments(frame, arg_limit_mb=arg_limit_mb)
        else:
            arguments_json = "{}"  # Empty object if arguments capture is disabled

        # Store call info for when it returns (including the config!)
        frame_id = id(frame)
        self._active_calls[frame_id] = {
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "file_path": file_path,
            "line_number": line_number,
            "column_number": column_number,
            "function_name": function_name,
            "arguments_json": arguments_json,
            "start_time_ns": start_time_ns,
            "captured": True,  # Mark that we actually captured this call
            "config": config,  # Store config for use in _handle_return
        }

    def _handle_return(self, frame, return_value):
        """
        Handle a function return event.

        Args:
            frame: Python frame object
            return_value: The value being returned
        """
        frame_id = id(frame)

        # Check if we have a record of this call
        if frame_id not in self._active_calls:
            return

        call_info = self._active_calls.pop(frame_id)

        # Decrement call depth
        if self._call_depth > 0:
            self._call_depth -= 1

        # If this was a skipped child function, we're done
        if not call_info.get("captured", False):
            return

        # Pop span from stack
        _sffuncspan.pop_span()

        # Calculate duration
        end_time_ns = _sffuncspan.get_epoch_ns()
        duration_ns = end_time_ns - call_info["start_time_ns"]

        # Get config for this function (from stored call info)
        config = call_info.get("config", {})
        if not config:
            # Fallback if config wasn't stored (shouldn't happen)
            config = self._get_config_for_function(
                call_info["file_path"], call_info["function_name"]
            )

        # Serialize return value (or skip if disabled by config)
        if config.get("include_return_value", self._default_capture_return_value):
            max_size = (
                config.get("return_limit_mb", self._default_return_limit_mb) * 1048576
            )
            return_value_json = self._serialize_value(return_value, max_size)
        else:
            return_value_json = None  # No return value if disabled

        # Get session ID (trace ID)
        _, session_id = get_or_set_sf_trace_id()

        # Record the span
        _sffuncspan.record_span(
            session_id=str(session_id),
            span_id=call_info["span_id"],
            parent_span_id=call_info["parent_span_id"],
            file_path=call_info["file_path"],
            line_number=call_info["line_number"],
            column_number=call_info["column_number"],
            function_name=call_info["function_name"],
            arguments_json=call_info["arguments_json"],
            return_value_json=return_value_json,
            start_time_ns=call_info["start_time_ns"],
            duration_ns=duration_ns,
        )

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False


# Global profiler instance
_global_profiler: Optional[FunctionSpanProfiler] = None


def init_function_span_profiler(
    url: str,
    query: str,
    api_key: str,
    service_uuid: str,
    library: str = "sf_veritas",
    version: str = "1.0.0",
    http2: bool = True,
    variable_capture_size_limit_mb: int = 1,
    capture_from_installed_libraries: Optional[List[str]] = None,
    sample_rate: float = 1.0,
    enable_sampling: bool = False,
    include_django_view_functions: bool = False,
    auto_start: bool = True,
) -> FunctionSpanProfiler:
    """
    Initialize the global function span profiler.

    Args:
        url: GraphQL endpoint URL
        query: GraphQL mutation query for function spans
        api_key: API key for authentication
        service_uuid: Service UUID
        library: Library name (default: "sf_veritas")
        version: Library version (default: "1.0.0")
        http2: Use HTTP/2 (default: True)
        variable_capture_size_limit_mb: Max size to capture per variable (default: 1MB)
        capture_from_installed_libraries: List of library prefixes to capture from
        sample_rate: Sampling probability 0.0-1.0 (default: 1.0 = capture all, 0.1 = 10%)
        enable_sampling: Enable sampling (default: False)
        auto_start: Automatically start profiling (default: True)

    Returns:
        FunctionSpanProfiler instance
    """
    global _global_profiler

    if _global_profiler is not None:
        _global_profiler.shutdown()

    _global_profiler = FunctionSpanProfiler(
        url=url,
        query=query,
        api_key=api_key,
        service_uuid=service_uuid,
        library=library,
        version=version,
        http2=http2,
        variable_capture_size_limit_mb=variable_capture_size_limit_mb,
        capture_from_installed_libraries=capture_from_installed_libraries,
        sample_rate=sample_rate,
        enable_sampling=enable_sampling,
        include_django_view_functions=include_django_view_functions,
    )

    if auto_start:
        _global_profiler.start()

    return _global_profiler


def get_function_span_profiler() -> Optional[FunctionSpanProfiler]:
    """Get the global function span profiler instance."""
    return _global_profiler


def shutdown_function_span_profiler():
    """Shutdown the global function span profiler."""
    global _global_profiler
    if _global_profiler is not None:
        _global_profiler.shutdown()
        _global_profiler = None
