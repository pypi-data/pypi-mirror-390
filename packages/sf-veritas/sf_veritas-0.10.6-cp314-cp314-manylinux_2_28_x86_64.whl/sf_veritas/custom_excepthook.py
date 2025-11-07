import inspect

# import linecache
import logging
import re
import sys
import threading
from types import FrameType, TracebackType
from typing import List, Optional

from . import app_config
from .env_vars import (
    SAILFISH_EXCEPTION_FETCH_BEYOND_OFFENDER_DEPTH,
    SAILFISH_EXCEPTION_FETCH_LOCALS_BEYOND_OFFENDER_DEPTH,
    SF_DEBUG,
    SF_DEBUG_TRACES,
)

# from .frame_tools import get_locals
from .interceptors import ExceptionInterceptor
from .local_env_detect import sf_is_local_dev_environment
from .thread_local import (
    get_or_set_sf_trace_id,
    has_handled_exception,
    mark_exception_handled,
)
from .types import FrameInfo

REGEX_EVERYTHING_BEFORE_PYTHON_PACKAGE_NAME_WHEN_EXAMINING_FILENAME = (
    r".*\/(site|dist)-packages\/"
)
REGEX_EVERYTHING_AFTER_NEXT_SLASH = r"\/.*"

logger = logging.getLogger(__name__)

# Profiling data structure to collect function call information
call_hierarchy = []

# Lock to manage thread-safe access to profiling data
call_hierarchy_lock = threading.Lock()

_original_excepthook = sys.excepthook


def custom_thread_excepthook(args):
    sys.excepthook(args.exc_type, args.exc_value, args.exc_traceback)


def process_traceback_only(
    exc_value: Exception, exc_traceback: TracebackType, was_caught: bool = True
):
    """
    Processes only the traceback information for an exception.

    Args:
        exc_value (Exception): The exception value.
        exc_traceback (TracebackType): The traceback object for the exception.
    """
    trace = extract_trace(exc_traceback)
    except_interceptor = ExceptionInterceptor()
    _, trace_id = get_or_set_sf_trace_id()
    if SF_DEBUG:
        print(
            "process_traceback_only...SENDING DATA...do_send args=",
            (str(exc_value), trace, trace_id, was_caught),
            trace_id,
            log=False,
        )
    except_interceptor.do_send(
        (str(exc_value), trace, trace_id, was_caught, sf_is_local_dev_environment()[0]),
        trace_id,
    )


# Usage example in the custom_excepthook function:
def custom_excepthook(
    exc_type, exc_value, exc_traceback: TracebackType, raise_original: bool = True
):
    if has_handled_exception(exc_value):
        return
    mark_exception_handled(exc_value)

    if SF_DEBUG:
        print(f"custom_excepthook -> raise_original={raise_original}", log=False)

    transmit_exception(exc_type, exc_value, exc_traceback)

    if raise_original:
        _original_excepthook(exc_type, exc_value, exc_traceback)


def transmit_exception(exc_type, exc_value, exc_traceback, was_caught: bool = True):
    """
    Handles transmitting exception information based on profiling mode.

    Args:
        exc_type: The type of the exception.
        exc_value: The exception instance.
        exc_traceback: The traceback object for the exception.
    """
    if app_config._profiling_mode_enabled:
        threading.Thread(
            target=process_profiling_data,
            args=(exc_type, exc_value, exc_traceback, was_caught),
        ).start()
        return
    process_traceback_only(exc_value, exc_traceback, was_caught)


def profiling_function(frame: FrameType, event: str, arg):
    if not app_config._profiling_mode_enabled:
        return

    if event in ["call", "return"]:
        code = frame.f_code
        function_name = code.co_name
        filename = code.co_filename
        line_no = frame.f_lineno
        class_name = None

        # Try to determine if we're inside a method of a class
        if "self" in frame.f_locals:
            class_name = type(frame.f_locals["self"]).__name__

        call_info = {
            "event": event,
            "function": function_name,
            "class": class_name,
            "file": filename,
            "line_no": line_no,
        }

        # Add profiling data to call hierarchy with a lock for thread safety
        with call_hierarchy_lock:
            if len(call_hierarchy) < app_config._profiling_max_depth:
                call_hierarchy.append(call_info)


def process_profiling_data(exc_type, exc_value, exc_traceback, was_caught: bool = True):
    # Extract the traceback and process detailed information
    trace = extract_trace(exc_traceback)

    # Process profiling data
    with call_hierarchy_lock:
        if SF_DEBUG and SF_DEBUG_TRACES:
            print("=" * 40, log=False)
            print("Printing the complete call hierarchy after exception...", log=False)
            print("=" * 40, log=False)

        for entry in call_hierarchy:
            if entry["event"] == "call":
                class_name = f"{entry['class']}." if entry["class"] else ""
                if SF_DEBUG and SF_DEBUG_TRACES:
                    print(
                        f"Called: {class_name}{entry['function']} (File: {entry['file']}, Line: {entry['line_no']})",
                        log=False,
                    )
            elif entry["event"] == "return":
                if SF_DEBUG and SF_DEBUG_TRACES:
                    print(f"Return from: {entry['function']}", log=False)

        if SF_DEBUG and SF_DEBUG_TRACES:
            print("-" * 40, log=False)

        # Clear profiling data after processing
        call_hierarchy.clear()

    # Send the extracted traceback data to the exception interceptor
    except_interceptor = ExceptionInterceptor()
    _, trace_id = get_or_set_sf_trace_id()
    if SF_DEBUG:
        print(
            "process_traceback_only...SENDING DATA...do_send args=",
            (str(exc_value), trace, trace_id, was_caught),
            trace_id,
            log=False,
        )
    except_interceptor.do_send(
        (str(exc_value), trace, trace_id, was_caught, sf_is_local_dev_environment()[0]),
        trace_id,
    )


def safe_repr(value):
    try:
        return repr(value)
    except Exception:
        return f"<unrepresentable: {type(value).__name__}>"


def extract_trace(tb: Optional[TracebackType] = None) -> List[FrameInfo]:
    tb_list = []

    # Collect all traceback frames in natural order (most recent last)
    while tb is not None:
        tb_list.append(tb)
        tb = tb.tb_next

    if not tb_list:
        return []

    frame_stack = []

    # Iterate through the traceback, capturing frame information
    for tb in tb_list:
        frame = tb.tb_frame
        frame_info = inspect.getframeinfo(frame)
        filename = frame_info.filename
        function_name = frame_info.function
        line_no = frame_info.lineno
        code_context = (
            frame_info.code_context[0].strip()
            if frame_info.code_context
            else "No code context"
        )

        frame_info_obj = FrameInfo(
            file=filename,
            line=line_no,
            function=function_name,
            code=code_context,
        )

        # Capture ALL local variables at each frame - no depth or package restrictions
        frame_info_obj.locals = {k: safe_repr(v) for k, v in frame.f_locals.items()}

        frame_stack.append(frame_info_obj)

    frame_stack[-1].offender = True
    return frame_stack


def start_profiling():
    """Start profiling to collect call hierarchy information if profiling is enabled."""
    from .env_vars import SF_DEBUG

    if SF_DEBUG:
        try:
            print(
                f"[[DEBUG]] start_profiling() called, _profiling_mode_enabled={app_config._profiling_mode_enabled}",
                log=False,
            )
        except:
            print(
                f"[[DEBUG]] start_profiling() called, _profiling_mode_enabled={app_config._profiling_mode_enabled}"
            )
    if app_config._profiling_mode_enabled:
        try:
            print(
                f"[[DEBUG]] Setting sys.setprofile to profiling_function, current={sys.getprofile()}",
                log=False,
            )
        except:
            print(
                f"[[DEBUG]] Setting sys.setprofile to profiling_function, current={sys.getprofile()}"
            )
        sys.setprofile(profiling_function)
        try:
            print(
                f"[[DEBUG]] After setting, sys.getprofile()={sys.getprofile()}",
                log=False,
            )
        except:
            print(f"[[DEBUG]] After setting, sys.getprofile()={sys.getprofile()}")


def stop_profiling():
    """Stop profiling to prevent collecting more call hierarchy data."""
    sys.setprofile(None)


def should_collect_local_variables_for_stack_item(filename: str) -> bool:
    if "__all__" in app_config._site_and_dist_packages_to_collect_local_variables_on:
        return True
    return is_allowed_package(filename)


def is_installed_package(filename: str) -> bool:
    return bool(
        re.search(
            REGEX_EVERYTHING_BEFORE_PYTHON_PACKAGE_NAME_WHEN_EXAMINING_FILENAME,
            filename,
        )
    )


def get_package_name_from_site_or_dist_package(filename: str):
    site_dist_packages_removed = re.sub(
        REGEX_EVERYTHING_BEFORE_PYTHON_PACKAGE_NAME_WHEN_EXAMINING_FILENAME,
        "",
        filename,
    )
    package_installed_name = re.sub(
        REGEX_EVERYTHING_AFTER_NEXT_SLASH, "", site_dist_packages_removed
    )
    return package_installed_name


def is_allowed_package(filename: str) -> bool:
    if not is_installed_package(filename):
        return True

    package = get_package_name_from_site_or_dist_package(filename)
    return package in app_config._site_and_dist_packages_to_collect_local_variables_on
