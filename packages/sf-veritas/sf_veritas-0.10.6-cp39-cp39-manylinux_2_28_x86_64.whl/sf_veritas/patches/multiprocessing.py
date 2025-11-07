import multiprocessing

from ..thread_local import get_context, set_context

_original_process_init = multiprocessing.Process.__init__


def patched_process_init(self, *args, **kwargs):
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

    _original_process_init(self, *args, **kwargs)


def patch_multiprocessing():
    multiprocessing.Process.__init__ = patched_process_init
