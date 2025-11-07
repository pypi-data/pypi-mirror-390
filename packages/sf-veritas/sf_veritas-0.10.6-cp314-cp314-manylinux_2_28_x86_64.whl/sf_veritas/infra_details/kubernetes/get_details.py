from typing import Any, Dict

from .get_cluster_name import get_cluster_name


def get_details() -> Dict[str, Any]:
    return {"clusterName": get_cluster_name()}
