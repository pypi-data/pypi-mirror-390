import inspect
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

import requests
import tldextract
from requests.adapters import HTTPAdapter
from requests.sessions import Session

from . import app_config
from .constants import SAILFISH_TRACING_HEADER
from .env_vars import PRINT_CONFIGURATION_STATUSES, SF_DEBUG
from .package_metadata import PACKAGE_NAME
from .regular_data_transmitter import (
    DomainsToNotPassHeaderToTransmitter,
    NetworkHopsTransmitter,
    NetworkRequestTransmitter,
)
from .thread_local import (
    activate_reentrancy_guards_exception,
    activate_reentrancy_guards_logging,
    activate_reentrancy_guards_print,
    get_or_set_sf_trace_id,
    is_network_recording_suppressed,
)
from .utils import strtobool

DOMAINS_TO_NOT_PROPAGATE_HEADER_TO_DEFAULT = [
    "identitytoolkit.googleapis.com",
]
DOMAINS_TO_NOT_PROPAGATE_HEADER_TO_ENVIRONMENT = [
    domain
    for domain in os.getenv("DOMAINS_TO_NOT_PROPAGATE_HEADER_TO_ENVIRONMENT", "").split(
        ","
    )
    if domain
]

NON_CUSTOMER_CODE_PATHS = (
    "site-packages",
    "dist-packages",
    "venv",
    "/lib/python",
    "\\lib\\python",
    PACKAGE_NAME,
)
_TRIPARTITE_TRACE_ID_REGEX = re.compile(r"^([^/]+/[^/]+)/[^/]+$")

# This filename is used as a heuristic to locate the user's entry point in the stack trace.
# It's commonly the main application file in smaller or single-file projects.
DEFAULT_CUSTOMER_ENTRY_FILENAME = "app.py"


logger = logging.getLogger(__name__)


class RequestInterceptor(HTTPAdapter):
    def __init__(self, domains_to_not_propagate_headers_to: List[str]):
        super().__init__()
        self.header_name_tracing = SAILFISH_TRACING_HEADER
        self.header_name_reentryancy_guard_logging_preactive = (
            "reentrancy_guard_logging_preactive"
        )
        self.header_name_reentryancy_guard_print_preactive = (
            "reentrancy_guard_print_preactive"
        )
        self.header_name_reentryancy_guard_exception_preactive = (
            "reentrancy_guard_exception_preactive"
        )
        self.domains_to_not_propagate_headers_to = domains_to_not_propagate_headers_to
        self.network_hop_transmitter = NetworkHopsTransmitter()

    def check_and_activate_reentrancy_guards(self, headers: Dict[str, Any]) -> None:
        reentryancy_guard_logging_preactive = strtobool(
            headers.get(self.header_name_reentryancy_guard_logging_preactive, "false")
        )
        if reentryancy_guard_logging_preactive:
            activate_reentrancy_guards_logging()
        reentryancy_guard_print_preactive = strtobool(
            headers.get(self.header_name_reentryancy_guard_print_preactive, "false")
        )
        if reentryancy_guard_print_preactive:
            activate_reentrancy_guards_print()
        reentryancy_guard_exception_preactive = strtobool(
            headers.get(self.header_name_reentryancy_guard_exception_preactive, "false")
        )
        if reentryancy_guard_exception_preactive:
            activate_reentrancy_guards_exception()

    def capture_request_details(self):
        """
        Identifies the first user-defined frame by walking the call stack manually
        and skipping frames that belong to known non-customer paths.

        Returns:
            frame_data (dict): Dictionary with line, column, and function name.
            filename (str): The path to the file that initiated the call.
        """

        frame = inspect.currentframe()
        if frame is None:
            if SF_DEBUG:
                print("capture_request_details: no current frame", log=False)
            return None, None

        frame = frame.f_back  # Skip this function's own frame

        while frame:
            filename = frame.f_code.co_filename

            # Inline check to skip known non-customer paths
            skip = False
            for keyword in NON_CUSTOMER_CODE_PATHS:
                if keyword in filename:
                    skip = True
                    break

            if not skip:
                lineno = frame.f_lineno
                func_name = frame.f_code.co_name
                if SF_DEBUG:
                    print(
                        f"Network request initiated at {filename}:{lineno} in {func_name}()",
                        log=False,
                    )
                return {
                    "line": str(lineno),
                    "column": "0",
                    "name": func_name,
                }, filename

            frame = frame.f_back

        if SF_DEBUG:
            print(
                "capture_request_details: no user code found in call stack", log=False
            )
        return None, None

    def send_network_hops(self):
        frame_data, entrypoint = self.capture_request_details()
        if frame_data and entrypoint:
            _, session_id = get_or_set_sf_trace_id(
                is_associated_with_inbound_request=True
            )
            self.network_hop_transmitter.do_send(
                (
                    session_id,
                    frame_data["line"],
                    frame_data["column"],
                    frame_data["name"],
                    entrypoint,
                )
            )

    def activate_preactive_headers(self, headers: Dict[str, Any]) -> None:
        headers[self.header_name_reentryancy_guard_logging_preactive] = "true"
        headers[self.header_name_reentryancy_guard_print_preactive] = "true"
        headers[self.header_name_reentryancy_guard_exception_preactive] = "true"

    def add_headers(self, request, **kwargs):
        if SF_DEBUG:
            print("RequestInterceptor: add_headers", log=False)

        self.send_network_hops()
        self.check_and_activate_reentrancy_guards(request.headers)

        _, sf_trace_id = get_or_set_sf_trace_id()
        request_domain = self.extract_domain(request.url)
        if request_domain not in self.domains_to_not_propagate_headers_to:
            request.headers[self.header_name_tracing] = sf_trace_id

        if SF_DEBUG:
            print(f"RequestInterceptor: Header value: {sf_trace_id}", log=False)

        self.activate_preactive_headers(request.headers)
        super().add_headers(request, **kwargs)

    def process_request_and_get_sf_trace_id_from_header(self, headers: dict):
        if SF_DEBUG:
            print(
                "[[process_request_and_get_sf_trace_id_from_header]] headers=",
                headers,
                log=False,
            )
        self.send_network_hops()
        self.check_and_activate_reentrancy_guards(headers)

        trace_id = headers.get(self.header_name_tracing)
        if SF_DEBUG:
            print(
                f"[[process_request_and_get_sf_trace_id_from_header]]; trace_id={trace_id}",
                log=False,
            )
        _, trace_id = get_or_set_sf_trace_id(trace_id)
        return trace_id

    def propagate_header(self, headers: dict, header_value: str):
        if SF_DEBUG:
            print("RequestInterceptor: propagate_header", log=False)

        if header_value:
            match = _TRIPARTITE_TRACE_ID_REGEX.match(header_value)
            if match:
                header_value = f"{match.group(1)}/{uuid4()}"

        headers[self.header_name_tracing] = header_value
        self.activate_preactive_headers(headers)

        if SF_DEBUG:
            print("RequestInterceptor: headers", headers, log=False)

        return header_value

    @staticmethod
    def extract_domain(url: str) -> str:
        extracted = tldextract.extract(url)
        if extracted.subdomain:
            return remove_prefix(
                f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}", "www."
            )
        return remove_prefix(f"{extracted.domain}.{extracted.suffix}", "www.")


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


# Track if domains mutation has been sent (to avoid duplicate sends)
_domains_mutation_sent = False

def get_domains_to_not_propagate_headers_to(
    domains_to_not_propagate_headers_to: Optional[List[str]] = None,
) -> List[str]:
    global _domains_mutation_sent

    if domains_to_not_propagate_headers_to is None:
        domains_to_not_propagate_headers_to = []
    domains_to_not_propagate_headers_to_nondefault_unfiltered = (
        DOMAINS_TO_NOT_PROPAGATE_HEADER_TO_ENVIRONMENT
        + domains_to_not_propagate_headers_to
    )
    domains_to_not_propagate_headers_to_nondefault = [
        domain
        for domain in domains_to_not_propagate_headers_to_nondefault_unfiltered
        if domain
    ]

    # Only send domains mutation once (not for every patched library)
    if domains_to_not_propagate_headers_to_nondefault and not _domains_mutation_sent:
        _domains_mutation_sent = True
        domains_to_not_pass_header_to_transmitter = (
            DomainsToNotPassHeaderToTransmitter()
        )
        domains_to_not_pass_header_to_transmitter.do_send(
            (domains_to_not_propagate_headers_to_nondefault,)
        )

    domains_to_not_propagate_headers_to_all = (
        domains_to_not_propagate_headers_to_nondefault
        + domains_to_not_propagate_headers_to
    )
    return [
        remove_prefix(domain, "www.")
        for domain in domains_to_not_propagate_headers_to_all
    ]


def patch_requests(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    domains_to_not_propagate_headers_to_final = get_domains_to_not_propagate_headers_to(
        domains_to_not_propagate_headers_to
    )
    if PRINT_CONFIGURATION_STATUSES:
        print("patching requests", log=False)
    original_request = Session.request

    def custom_request(self, method, url, **kwargs):
        if SF_DEBUG:
            print("[[custom_request]]", log=False)
            start_time = time.time() * 1000  # Start timing

        headers = (
            kwargs.pop("headers", {}) or {}
        )  # Ensure headers dict is always initialized
        trace_id_set, trace_id_alternative = get_or_set_sf_trace_id()
        if SF_DEBUG:
            print(
                f"[[custom_request]] trace_id_set={str(trace_id_set)}, trace_id_alternative={str(trace_id_alternative)}",
                log=False,
            )

        interceptor = RequestInterceptor(domains_to_not_propagate_headers_to_final)
        trace_id = interceptor.process_request_and_get_sf_trace_id_from_header(headers)
        if SF_DEBUG:
            print(
                f"[[custom_request] trace_id={trace_id}, OR trace_id_alternative={trace_id_alternative}",
                log=False,
            )

        updated_trace_id = interceptor.propagate_header(headers, trace_id)
        kwargs["headers"] = headers

        # 1) actually perform the request
        timestamp_start = int(time.time() * 1000)
        response = original_request(self, method, url, **kwargs)
        timestamp_end = int(time.time() * 1000)

        # 2) decide whether to fire off a NetworkRequest mutation
        # domain = interceptor.extract_domain(url)
        if (
            not is_network_recording_suppressed()
            # and domain not in domains_to_not_propagate_headers_to_final
        ):
            # split the tripartite trace‐header into [session, page_visit, request]
            parts = updated_trace_id.split("/")
            recording_session_id = parts[0]
            page_visit_id = parts[1] if len(parts) > 1 else None
            request_id = parts[2] if len(parts) > 2 else None

            # 3) fire your transmitter
            tx = NetworkRequestTransmitter()
            tx.do_send(
                (
                    request_id,
                    page_visit_id,
                    recording_session_id,
                    app_config._service_uuid,  # matches your `service_uuid` field
                    timestamp_start,
                    timestamp_end,
                    response.status_code,
                    response.ok,
                    None if response.ok else response.text[:255],
                    url,
                    method.upper()
                )
            )

        return response

    # Patch requests library
    Session.request = custom_request
    requests.Session.request = custom_request

    if PRINT_CONFIGURATION_STATUSES:
        print("patching requests...DONE", log=False)

    # Patch urllib3 (used internally by requests)
    try:
        import urllib3

        original_urlopen = urllib3.connectionpool.HTTPConnectionPool.urlopen

        def patched_urlopen(self, method, url, body=None, headers=None, **kwargs):
            headers = headers or {}
            interceptor = RequestInterceptor(domains_to_not_propagate_headers_to_final)
            trace_id = interceptor.process_request_and_get_sf_trace_id_from_header(
                headers
            )
            interceptor.propagate_header(headers, trace_id)
            return original_urlopen(
                self, method, url, body=body, headers=headers, **kwargs
            )

        urllib3.connectionpool.HTTPConnectionPool.urlopen = patched_urlopen
        if PRINT_CONFIGURATION_STATUSES:
            print("patching urllib3...DONE", log=False)
    except ImportError:
        if PRINT_CONFIGURATION_STATUSES:
            print("urllib3 not found, skipping patch", log=False)

    # Patch http.client (used by many standard library HTTP calls)
    try:
        import http.client

        original_http_client_request = http.client.HTTPConnection.request

        def patched_http_client_request(
            self, method, url, body=None, headers=None, **kwargs
        ):
            headers = headers or {}
            interceptor = RequestInterceptor(domains_to_not_propagate_headers_to_final)
            trace_id = interceptor.process_request_and_get_sf_trace_id_from_header(
                headers
            )
            interceptor.propagate_header(headers, trace_id)
            return original_http_client_request(
                self, method, url, body=body, headers=headers, **kwargs
            )

        http.client.HTTPConnection.request = patched_http_client_request
        if PRINT_CONFIGURATION_STATUSES:
            print("patching http.client...DONE", log=False)
    except ImportError:
        if PRINT_CONFIGURATION_STATUSES:
            print("http.client not found, skipping patch", log=False)
