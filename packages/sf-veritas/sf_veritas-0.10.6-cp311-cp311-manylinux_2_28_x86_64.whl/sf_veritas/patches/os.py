import os

from ..thread_local import get_context, set_context

_original_fork = os.fork


def patched_fork():
    current_context = get_context()
    pid = _original_fork()
    if pid == 0:  # Child process
        set_context(current_context)
    return pid


def patch_os():
    os.fork = patched_fork
