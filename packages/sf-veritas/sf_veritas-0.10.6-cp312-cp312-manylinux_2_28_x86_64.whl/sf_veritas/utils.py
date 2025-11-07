import json
from typing import List, Tuple


def strtobool(val) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def is_json_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


def serialize_json_with_exclusions(input_dict) -> Tuple[str, List[str]]:
    serializable_data = {}
    excluded_fields = []

    for k, v in input_dict.items():
        if is_json_serializable(v):
            serializable_data[k] = v
        else:
            excluded_fields.append(k)

    json_str = json.dumps(serializable_data)
    return json_str, excluded_fields
