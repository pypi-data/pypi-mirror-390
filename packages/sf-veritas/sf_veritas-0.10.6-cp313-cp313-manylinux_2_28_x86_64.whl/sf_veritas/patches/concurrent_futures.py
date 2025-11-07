from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from ..thread_local import get_context, set_context

_original_submit = ThreadPoolExecutor.submit


def patched_submit(self, fn, *args, **kwargs):
    current_context = get_context()

    def wrapped_fn(*fn_args, **fn_kwargs):
        set_context(current_context)
        fn(*fn_args, **fn_kwargs)

    return _original_submit(self, wrapped_fn, *args, **kwargs)


def patch_concurrent_futures():
    ThreadPoolExecutor.submit = patched_submit
    ProcessPoolExecutor.submit = patched_submit
