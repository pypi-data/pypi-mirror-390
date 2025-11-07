import sys
from typing import Any, Iterable, List

from .env_vars import (
    SAILFISH_EXCEPTION_LOCALS_HIDE_DUNDER,
    SAILFISH_EXCEPTION_LOCALS_HIDE_SELF,
    SAILFISH_EXCEPTION_LOCALS_HIDE_SUNDER,
    SAILFISH_EXCEPTION_LOCALS_TYPES_TO_IGNORE,
)


def import_type(module_name: str, type_name: str):
    try:
        exec(  # pylint: disable=exec-used
            f"from {module_name} import {type_name}",
            globals(),
        )
        return globals().get(type_name, None)
    except ImportError:
        return None


def get_types_from_str(types_str: str) -> List[type]:
    types_list = []
    if types_str:
        for type_path in types_str.split(","):
            type_path_fixed = type_path.replace(" ", "")
            module_name, type_name = type_path_fixed.rsplit(".", 1)
            type_obj = import_type(module_name, type_name)
            if type_obj:
                types_list.append(type_obj)
    return types_list


EXCEPTION_LOCALS_TYPES_TO_IGNORE = get_types_from_str(
    SAILFISH_EXCEPTION_LOCALS_TYPES_TO_IGNORE
)


def get_current_frame():
    return sys._getframe(1)  # pylint: disable=protected-access


def value_type_to_be_ignored(value: Any) -> bool:
    return any(
        isinstance(value, type_obj) for type_obj in EXCEPTION_LOCALS_TYPES_TO_IGNORE
    )


def key_is_str_to_be_ignored(
    key: Any, locals_hide_self: bool, locals_hide_dunder: bool, locals_hide_sunder: bool
) -> bool:
    return (
        (locals_hide_self and key == "self")
        or (locals_hide_dunder and key.startswith("__"))
        or (locals_hide_sunder and key.startswith("_"))
    )


def filter_locals(
    iter_locals: Iterable[tuple[str, object]],
    locals_hide_self: bool,
    locals_hide_dunder: bool,
    locals_hide_sunder: bool,
) -> Iterable[tuple[str, object]]:
    for key, value in iter_locals:
        if not isinstance(key, str):
            if value_type_to_be_ignored(value):
                continue
        else:
            if key_is_str_to_be_ignored(
                key, locals_hide_self, locals_hide_dunder, locals_hide_sunder
            ):
                continue
            if value_type_to_be_ignored(value):
                continue
            if key in ("args", "field_args") and isinstance(value, list):
                value = list(
                    filter_locals(
                        enumerate(value),
                        locals_hide_self,
                        locals_hide_dunder,
                        locals_hide_sunder,
                    )
                )
            if key in ("kwargs", "field_kwargs") and isinstance(value, dict):
                value = dict(
                    filter_locals(
                        value.items(),
                        locals_hide_self,
                        locals_hide_dunder,
                        locals_hide_sunder,
                    )
                )
        yield key, value


def get_locals(
    iter_locals: Iterable[tuple[str, object]],
    locals_hide_self: bool = SAILFISH_EXCEPTION_LOCALS_HIDE_SELF,
    locals_hide_dunder: bool = SAILFISH_EXCEPTION_LOCALS_HIDE_DUNDER,
    locals_hide_sunder: bool = SAILFISH_EXCEPTION_LOCALS_HIDE_SUNDER,
) -> Iterable[tuple[str, object]]:
    """Extract locals from an iterator of key pairs."""
    if not (locals_hide_dunder or locals_hide_sunder):
        yield from iter_locals
        return
    iter_locals_filtered = filter_locals(
        iter_locals, locals_hide_self, locals_hide_dunder, locals_hide_sunder
    )
    for key, value in iter_locals_filtered:
        yield key, value
