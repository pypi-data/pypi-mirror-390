import importlib.util
import sys
import threading
import time
from importlib import abc

from ..env_vars import PRINT_CONFIGURATION_STATUSES

# Thread-local storage to avoid re-entry problems
patch_lock = threading.local()


def patch_exceptions(module):
    if hasattr(patch_lock, "active"):
        return
    patch_lock.active = True


class ExceptionPatchingFinder(abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if hasattr(patch_lock, "loading") and patch_lock.loading:
            return None
        try:
            patch_lock.loading = True
            original_spec = importlib.util.find_spec(fullname, path)
            if original_spec:
                return importlib.util.spec_from_loader(
                    fullname,
                    ExceptionPatchingLoader(original_spec.loader),
                    origin=original_spec.origin,
                )
            return None
        finally:
            patch_lock.loading = False


class ExceptionPatchingLoader(abc.Loader):
    def __init__(self, loader):
        self._original_loader = loader

    def create_module(self, spec):
        return self._original_loader.create_module(spec)

    def exec_module(self, module):
        self._original_loader.exec_module(module)
        patch_exceptions(module)


def install_import_hook():
    if PRINT_CONFIGURATION_STATUSES:
        print("EXCEPTIONS - install_import_hook", log=False)
    sys.meta_path.insert(0, ExceptionPatchingFinder())
    if PRINT_CONFIGURATION_STATUSES:
        print("EXCEPTIONS - install_import_hook...DONE", log=False)


# Initially store the current state of sys.excepthook
original_excepthook = sys.excepthook


def monitor_excepthook(interval=1):
    global original_excepthook

    while True:
        current_hook = sys.excepthook
        if current_hook != original_excepthook and PRINT_CONFIGURATION_STATUSES:
            if PRINT_CONFIGURATION_STATUSES:
                print("sys.excepthook has been modified!")
            original_excepthook = current_hook
            continue
        if PRINT_CONFIGURATION_STATUSES:
            print("No change detected in sys.excepthook.")

        # Pause for the specified interval before the next check
        time.sleep(interval)


# Function to start monitoring in a separate thread
def start_monitoring(interval=2):
    thread = threading.Thread(target=monitor_excepthook, args=(interval,))
    # thread.daemon = True  # This makes the thread exit when the main program exits
    thread.start()
