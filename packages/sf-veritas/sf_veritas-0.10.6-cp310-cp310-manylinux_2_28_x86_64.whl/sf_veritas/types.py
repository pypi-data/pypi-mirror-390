import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FrameInfo:
    file: str
    line: int
    function: str
    code: str
    locals: Optional[Dict[str, Any]] = field(default_factory=dict)
    column: Optional[int] = None
    offender: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        frame_info_dict = {
            "file": self.file,
            "line": self.line,
            "function": self.function,
            "code": self.code,
        }
        if self.locals:
            frame_info_dict["locals"] = {k: str(v) for k, v in self.locals.items()}
        if self.offender:
            frame_info_dict["offender"] = self.offender
        if self.column is not None:
            frame_info_dict["column"] = self.column
        return frame_info_dict

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


def get_trace_from_json(data_json) -> List[FrameInfo]:
    data = json.loads(data_json)
    return [FrameInfo(**item) for item in data]


class CustomJSONEncoderForFrameInfo(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FrameInfo):
            return obj.to_dict()
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
