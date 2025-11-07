import os
import uuid
from typing import Dict, List, Optional, Union

from .constants import SAILFISH_DEFAULT_GRAPHQL_ENDPOINT
from .infra_details import get_infra_details

_service_uuid = str(uuid.uuid4())
_service_identifier = None
_service_version = None
_service_display_name = None
_git_sha = None
_service_identification_received = False
_service_additional_metadata: Optional[Dict[str, Union[str, int, float, None]]] = None

_setup_interceptors_call_filename = None
_setup_interceptors_call_lineno = None

_interceptors_initialized = False

_profiling_mode_enabled: bool = False
_profiling_max_depth: int = 5

_site_and_dist_packages_to_collect_local_variables_on: Optional[List[str]] = []

_sailfish_api_key = None
_sailfish_graphql_endpoint: str = os.getenv(
    "SAILFISH_GRAPHQL_ENDPOINT", SAILFISH_DEFAULT_GRAPHQL_ENDPOINT
)

_infra_details = get_infra_details()


def _set_site_and_dist_packages_to_collect_local_variables_on(
    site_and_dist_packages_to_collect_local_variables_on: Optional[List[str]] = None,
):
    if site_and_dist_packages_to_collect_local_variables_on is None:
        _site_and_dist_packages_to_collect_local_variables_on = []
    site_and_dist_packages_to_collect_local_variables_on_final: List[str] = (
        site_and_dist_packages_to_collect_local_variables_on.copy()
    )
    for package in site_and_dist_packages_to_collect_local_variables_on:
        if "-" not in package:
            continue
        site_and_dist_packages_to_collect_local_variables_on_final.append(
            package.replace("-", "_")
        )
    _site_and_dist_packages_to_collect_local_variables_on = (
        site_and_dist_packages_to_collect_local_variables_on_final
    )
