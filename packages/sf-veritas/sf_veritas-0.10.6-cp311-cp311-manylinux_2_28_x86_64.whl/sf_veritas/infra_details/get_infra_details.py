from dataclasses import dataclass
from typing import Any, Dict

from .kubernetes import get_details as get_kubernetes_details
from .running_on import System, running_on


@dataclass
class InfraDetails:
    system: System
    details: Dict[str, Any]


def get_running_on_details(system: System) -> Dict[str, Any]:
    if system == System.KUBERNETES:
        return get_kubernetes_details()
    if system == System.UNKNOWN:
        return {}


def get_infra_details() -> InfraDetails:
    system = running_on()
    details = get_running_on_details(system)
    return InfraDetails(system=system, details=details)
