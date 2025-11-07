import contextvars
import multiprocessing
import os
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from .. import app_config
from ..thread_local import (
    get_context,
    set_context,
    is_ld_preload_active,
    outbound_header_base_ctx,
    _get_shared_outbound_header_base,
)
from ..env_vars import SF_DEBUG

_original_thread_init = threading.Thread.__init__
_original_process_init = multiprocessing.Process.__init__
_original_executor_submit = ThreadPoolExecutor.submit
_original_process_submit = ProcessPoolExecutor.submit

# Cache LD_PRELOAD status at module level (checked once, not per-thread)
_LD_PRELOAD_MODE = is_ld_preload_active()

# Cache SF_DEBUG flag at module load to avoid repeated checks (set during initialization)
_SF_DEBUG_ENABLED = False

# PERFORMANCE: Allow disabling thread patching entirely for benchmarks
# Set SF_DISABLE_THREAD_PATCHING=1 to skip all thread wrapping overhead
_THREAD_PATCHING_DISABLED = os.getenv("SF_DISABLE_THREAD_PATCHING") == "1"


def patched_thread_init(self, *args, **kwargs):
    # PERFORMANCE: Skip context propagation when LD_PRELOAD is active
    # LD_PRELOAD mode only needs outbound headers (handled by ContextVar in ThreadPoolExecutor.submit)
    # Background library threads (urllib3, httpcore, etc.) don't need full context

    # ULTRA-FAST PATH: Check all bypass conditions in one compound expression
    # Eliminates wrapper overhead for:
    # 1. SF_DISABLE_THREAD_PATCHING=1 (benchmark mode)
    # 2. LD_PRELOAD mode (context handled by ContextVar)
    # 3. Daemon threads (connection pools, background workers)
    if _THREAD_PATCHING_DISABLED or _LD_PRELOAD_MODE or kwargs.get("daemon", False):
        # Direct call without any wrapper overhead
        return _original_thread_init(self, *args, **kwargs)

    # Slow path: Full context propagation for Python-only mode
    current_context = get_context()

    original_target = kwargs.get("target")
    if original_target:

        def wrapped_target(*targs, **tkwargs):
            set_context(current_context)
            original_target(*targs, **tkwargs)

        kwargs["target"] = wrapped_target
    elif args and callable(args[0]):
        original_target = args[0]

        def wrapped_target(*targs, **tkwargs):
            set_context(current_context)
            original_target(*targs, **tkwargs)

        args = (wrapped_target,) + args[1:]

    _original_thread_init(self, *args, **kwargs)


def patched_process_init(self, *args, **kwargs):
    """
    Patch multiprocessing.Process.__init__() to serialize and pass context data to child processes.

    Similar to Thread patching, but we serialize the outbound header base dict
    since ContextVars cannot cross process boundaries (separate memory space).

    Performance:
    - Serialize overhead: ~100-500ns per process creation
    - IPC overhead: ~10-100μs (inter-process communication)
    - ContextVar reads in child: ~10-20ns each (NO LOCK)
    """
    # Get current outbound header base (try ContextVar first, then shared registry)
    base_dict = outbound_header_base_ctx.get()
    if not base_dict:
        base_dict = _get_shared_outbound_header_base()

    if _SF_DEBUG_ENABLED:
        print(f"[Process.__init__] 📦 Serializing context for child process: {base_dict}", log=False)

    original_target = kwargs.get("target")
    if original_target:
        def wrapped_target(*targs, **tkwargs):
            # Restore outbound header base in child process's ContextVar
            if base_dict:
                try:
                    from sf_veritas.thread_local import outbound_header_base_ctx as child_ctx
                    child_ctx.set(base_dict)
                    if SF_DEBUG:
                        print(f"[Process child] ✅ Restored context in child process: {base_dict}", log=False)
                except Exception as e:
                    if SF_DEBUG:
                        print(f"[Process child] ⚠️ Failed to restore context: {e}", log=False)

            # Run original target
            original_target(*targs, **tkwargs)

        kwargs["target"] = wrapped_target
    elif args and callable(args[0]):
        original_target = args[0]

        def wrapped_target(*targs, **tkwargs):
            # Restore outbound header base in child process's ContextVar
            if base_dict:
                try:
                    from sf_veritas.thread_local import outbound_header_base_ctx as child_ctx
                    child_ctx.set(base_dict)
                    if SF_DEBUG:
                        print(f"[Process child] ✅ Restored context in child process: {base_dict}", log=False)
                except Exception as e:
                    if SF_DEBUG:
                        print(f"[Process child] ⚠️ Failed to restore context: {e}", log=False)

            # Run original target
            original_target(*targs, **tkwargs)

        args = (wrapped_target,) + args[1:]

    _original_process_init(self, *args, **kwargs)


def patched_executor_submit(self, fn, /, *args, **kwargs):
    """
    Patch ThreadPoolExecutor.submit() to copy ContextVars to worker threads.

    This ensures outbound_header_base_ctx propagates to worker threads,
    eliminating lock contention on shared registry (~10ns vs 1-6ms!).

    Performance:
    - Before: ContextVar is None on worker thread → falls back to shared registry (LOCK) → 1-6ms
    - After: ContextVar copied to worker thread → instant access (~10ns) → NO LOCK
    """
    # PERFORMANCE: In LD_PRELOAD mode, we still need ContextVar propagation
    # but it's ultra-fast (~500ns) compared to get_context() (~264μs)

    # Copy current context (includes all ContextVars)
    ctx = contextvars.copy_context()

    # DEBUG: Uncomment for troubleshooting (adds ~1-100μs per submit!)
    # if SF_DEBUG:
    #     from .. import app_config
    #     from ..thread_local import outbound_header_base_ctx
    #     if app_config._interceptors_initialized:
    #         base_in_ctx = outbound_header_base_ctx.get(None)
    #         print(f"[ThreadPoolExecutor.submit] 📋 Copying context to worker thread (ctx has {len(ctx)} vars, outbound_header_base={base_in_ctx})", log=False)

    # Wrap function to run in copied context (minimal overhead ~500ns)
    def wrapped_fn():
        return ctx.run(fn, *args, **kwargs)

    # Submit wrapped function to executor
    return _original_executor_submit(self, wrapped_fn)


def patched_process_submit(self, fn, /, *args, **kwargs):
    """
    Patch ProcessPoolExecutor.submit() to serialize and pass context data to child processes.

    NOTE: ContextVars cannot be copied directly to processes (separate memory space).
    Instead, we serialize the outbound header base dict and restore it in the child.

    Performance:
    - Serialize + IPC overhead: ~10-100μs per submit (one-time cost)
    - ContextVar reads in child: ~10-20ns each (NO LOCK)
    - Still better than lock contention on every outbound call!

    Limitations:
    - Only works if child process has sf_veritas imported and initialized
    - Adds ~10-100μs overhead per submit (vs ~500ns for threads)
    """
    # Get current outbound header base (try ContextVar first, then shared registry)
    base_dict = outbound_header_base_ctx.get()
    if not base_dict:
        base_dict = _get_shared_outbound_header_base()

    if _SF_DEBUG_ENABLED:
        print(f"[ProcessPoolExecutor.submit] 📦 Serializing context for child process: {base_dict}", log=False)

    # Wrap function to restore context in child process
    def wrapped_fn():
        # Restore outbound header base in child process's ContextVar
        if base_dict:
            try:
                from sf_veritas.thread_local import outbound_header_base_ctx as child_ctx
                child_ctx.set(base_dict)
                if SF_DEBUG:
                    print(f"[ProcessPoolExecutor child] ✅ Restored context in child process: {base_dict}", log=False)
            except Exception as e:
                if SF_DEBUG:
                    print(f"[ProcessPoolExecutor child] ⚠️ Failed to restore context: {e}", log=False)

        # Run original function
        return fn(*args, **kwargs)

    # Submit wrapped function to executor
    return _original_process_submit(self, wrapped_fn)


def patch_threading():
    global _SF_DEBUG_ENABLED
    _SF_DEBUG_ENABLED = SF_DEBUG and app_config._interceptors_initialized

    threading.Thread.__init__ = patched_thread_init
    multiprocessing.Process.__init__ = patched_process_init
    ThreadPoolExecutor.submit = patched_executor_submit
    ProcessPoolExecutor.submit = patched_process_submit

    if _SF_DEBUG_ENABLED:
        print("[patch_threading] ✅ Patched Thread.__init__, Process.__init__, ThreadPoolExecutor.submit, and ProcessPoolExecutor.submit for ContextVar propagation", log=False)
