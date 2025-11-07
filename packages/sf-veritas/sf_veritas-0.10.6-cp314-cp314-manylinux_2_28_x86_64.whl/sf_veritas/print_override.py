import builtins

from .custom_print import SF_DEBUG, custom_print


def override_print():
    if hasattr(builtins, "_original_print"):
        return
    # Save the original print function
    builtins._original_print = builtins.print

    # Override the built-in print function
    builtins.print = custom_print
