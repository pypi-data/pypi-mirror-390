import importlib
import importlib.util
import sys
from importlib.abc import MetaPathFinder

from .custom_excepthook import custom_excepthook
from .custom_output_wrapper import get_custom_output_wrapper_django
from .env_vars import PRINT_CONFIGURATION_STATUSES


class ImportInterceptor:
    def __init__(self, module_name, callback):
        self.module_name = module_name
        self.callback = callback

    def find_spec(self, fullname, path, target=None):
        if fullname == self.module_name:
            self.callback()
            # Remove the interceptor once the callback has been called
            sys.meta_path.remove(self)
            return importlib.util.find_spec(fullname, path)
        return None


def setup_django_import_hook():
    interceptor = ImportInterceptor(
        "django.core.management", get_custom_output_wrapper_django
    )
    sys.meta_path.insert(0, interceptor)


def wrap_excepthook(old_excepthook):
    def custom_wrapper_excepthook(exc_type, exc_value, exc_traceback):
        # Call your custom exception hook
        custom_excepthook(exc_type, exc_value, exc_traceback)
        # Call the original exception hook (which might be Sentry's)
        if old_excepthook is not None:
            old_excepthook(exc_type, exc_value, exc_traceback)

    return custom_wrapper_excepthook


def set_excepthook():
    # Wrap the current excepthook
    current_excepthook = sys.excepthook
    wrapped_excepthook = wrap_excepthook(current_excepthook)
    sys.excepthook = wrapped_excepthook
    if PRINT_CONFIGURATION_STATUSES:
        print("Patched sys.excepthook for custom exception handling.")


class ExcepthookImportHook(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        print("fullname", fullname, log=False)
        if fullname in sys.modules:
            print("\t> fullname in sys.modules", log=False)
            set_excepthook()
        return None


def install_import_hook():
    sys.meta_path.insert(0, ExcepthookImportHook())
