from enum import Enum

from .kubernetes import kubernetes


class System(Enum):
    KUBERNETES = "Kubernetes"
    UNKNOWN = "Unknown"


def running_on() -> System:
    if kubernetes():
        return System.KUBERNETES
    return System.UNKNOWN


__all__ = ["running_on"]
