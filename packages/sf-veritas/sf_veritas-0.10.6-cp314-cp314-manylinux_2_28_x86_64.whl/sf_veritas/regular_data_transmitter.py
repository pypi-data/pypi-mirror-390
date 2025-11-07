import threading
from typing import Any, Dict, List, Optional

import requests

from . import app_config
from .env_vars import SF_DEBUG
from .package_metadata import PACKAGE_LIBRARY_TYPE, __version__
from .request_utils import non_blocking_post, non_blocking_post_with_response
from .thread_local import suppress_network_recording
from .timeutil import TimeSync

# Try to import C extension for fast path
try:
    from . import _sfservice
    _SFSERVICE_AVAILABLE = True
except Exception:
    _sfservice = None
    _SFSERVICE_AVAILABLE = False


class BaseTransmitter:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or app_config._sailfish_api_key
        self.endpoint = app_config._sailfish_graphql_endpoint
        self.query_type = "mutation"
        self.service_identifier = app_config._service_identifier
        self.git_sha = app_config._git_sha

    @property
    def query_name(self) -> str:
        return (
            self.operation_name[0].lower() + self.operation_name[1:]
            if self.operation_name
            else ""
        )

    # TODO - Strip out everything EXCEPT for `reentrancyGuardPreactive`
    def get_default_variables(self):
        timestamp_ms = TimeSync.get_instance().get_utc_time_in_ms()
        return {
            "apiKey": self.api_key,
            "serviceUuid": app_config._service_uuid,
            "timestampMs": str(timestamp_ms),
        }

    def get_variables(
        self,
        additional_variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        additional_variables = (
            additional_variables if additional_variables is not None else {}
        )
        return {
            **additional_variables,
            **self.get_default_variables(),
        }


class ServiceIdentifier(BaseTransmitter):
    def __init__(self, api_key: str = app_config._sailfish_api_key):
        super().__init__(api_key)
        self.operation_name = "IdentifyServiceDetails"

    def do_send(self, args) -> None:
        # Service identification is now handled by _sfservice C extension in setup_interceptors()
        # This method is kept as no-op for backward compatibility
        return

    def send(self):
        """
        Sends the service identification details as a GraphQL mutation.
        This method overrides the `send` method from `DataTransmitter`.
        """

        query = f"""
        {self.query_type} {self.operation_name}(
            $apiKey: String!,
            $timestampMs: String!,
            $serviceUuid: String!,
            $serviceIdentifier: String,
            $serviceVersion: String,
            $serviceAdditionalMetadata: JSON,
            $library: String!,
            $version: String!,
            $infrastructureType: String,
            $infrastructureDetails: JSON,
            $setupInterceptorsFilePath: String,
            $setupInterceptorsLineNumber: Int,
            $gitSha: String
        ) {{
            {self.query_name}(
                apiKey: $apiKey,
                timestampMs: $timestampMs,
                serviceUuid: $serviceUuid,
                serviceIdentifier: $serviceIdentifier,
                serviceVersion: $serviceVersion,
                serviceAdditionalMetadata: $serviceAdditionalMetadata,
                library: $library,
                version: $version,
                infrastructureType: $infrastructureType,
                infrastructureDetails: $infrastructureDetails
                setupInterceptorsFilePath: $setupInterceptorsFilePath,
                setupInterceptorsLineNumber: $setupInterceptorsLineNumber
                gitSha: $gitSha
            )
        }}
        """

        try:
            if SF_DEBUG:
                print(f"Sending query: {query}", log=False)

            # Non-blocking POST request to send the GraphQL query
            variables = self.get_variables(
                {
                    "serviceIdentifier": app_config._service_identifier,
                    "gitSha": app_config._git_sha,
                    "serviceVersion": app_config._service_version,
                    "serviceAdditionalMetadata": app_config._service_additional_metadata,
                    "library": PACKAGE_LIBRARY_TYPE,
                    "version": __version__,
                    "infrastructureType": app_config._infra_details.system.value,  # or whatever string you're passing
                    "infrastructureDetails": app_config._infra_details.details,
                    "setupInterceptorsFilePath": app_config._setup_interceptors_call_filename,
                    "setupInterceptorsLineNumber": app_config._setup_interceptors_call_lineno,
                },
            )

            future = non_blocking_post_with_response(
                self.endpoint, self.operation_name, query, variables
            )
            if future is None:
                return
            response = future.result()
            if SF_DEBUG and response is None:
                print(
                    f"IdentifyServiceDetails NOT sent successfully for service: UUID={app_config._service_uuid}",
                    log=False,
                )
                return
            service_identification_received = response.get("data", {}).get(
                self.query_name, False
            )
            app_config._service_identification_received = (
                service_identification_received
            )
            if SF_DEBUG:
                print(
                    f"IdentifyServiceDetails sent successfully for service: UUID={app_config._service_uuid}; service_identification_received={str(service_identification_received)}",
                    log=False,
                )

        except Exception as e:
            # Log any exceptions that occur during sending
            if SF_DEBUG:
                print(f"Error occurred while sending service identification: {e}")


class DataTransmitter(BaseTransmitter):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or app_config._sailfish_api_key
        self.endpoint = app_config._sailfish_graphql_endpoint
        self.operation_name: Optional[str] = ""
        self.query_type = "mutation"
        self.service_identifier = ServiceIdentifier()

    def check_if_contents_should_be_ignored(
        self, contents
    ):  # pylint: disable=unused-argument
        return False

    def _send_app_identifier(self) -> None:
        return
        if SF_DEBUG:
            print(
                "_send_app_identifier...SENDING DATA...args=",
                set(),
                log=False,
            )
        self.service_identifier.do_send(set())

    def do_send(self, args) -> None:
        self._send_app_identifier()
        try:
            self.send(*args)
        except RuntimeError:
            return

    def send(self, contents, session_id: str):
        if self.check_if_contents_should_be_ignored(contents):
            return
        query = f"""
        {self.query_type} {self.operation_name}($apiKey: String!, $serviceUuid: String!, $contents: String!, $library: String!, $timestampMs: String!, $version: String!) {{
            {self.query_name}(apiKey: $apiKey, serviceUuid: $serviceUuid, contents: $contents, library: $library, timestampMs: $timestampMs, version: $version)
        }}
        """

        non_blocking_post(
            self.endpoint,
            self.operation_name,
            query,
            self.get_variables({"contents": contents}),
        )


class DomainsToNotPassHeaderToTransmitter(DataTransmitter):
    def __init__(self, api_key: str = app_config._sailfish_api_key):
        super().__init__(api_key)
        self.operation_name = "DomainsToNotPassHeaderTo"

    def send(
        self,
        domains: List[str],
    ):
        # Fast path: Use C extension if available
        if _SFSERVICE_AVAILABLE and _sfservice:
            try:
                _sfservice.domains(domains=domains)
                return
            except Exception:
                # Fall through to Python implementation
                pass

        # Fallback: Use Python implementation
        query = f"""
        {self.query_type} {self.operation_name}(
            $apiKey: String!,
            $serviceUuid: String!,
            $timestampMs: String!,
            $domains: [String!]!,
            $gitSha: String
        ) {{
            {self.query_name}(
                apiKey: $apiKey,
                serviceUuid: $serviceUuid,
                timestampMs: $timestampMs,
                domains: $domains,
                gitSha: $gitSha
            )
        }}
        """
        variables = self.get_variables(
            {
                "domains": domains,
                "gitSha": app_config._git_sha,
            },
        )

        non_blocking_post(self.endpoint, self.operation_name, query, variables)


class UpdateServiceIdentifierMetadata(DataTransmitter):
    def __init__(self, api_key: str = app_config._sailfish_api_key):
        super().__init__(api_key)
        self.operation_name = "UpdateServiceDetails"

    def send(
        self,
        service_identifier: Optional[str] = None,
        service_version: Optional[str] = None,
        service_additional_metadata: Optional[Dict[str, Any]] = None,
        git_sha: Optional[str] = None,
    ):
        """
        Sends updateServiceDetails mutation to update service metadata.

        Args:
            service_identifier: Service identifier string
            service_version: Service version string
            service_additional_metadata: Dictionary of additional metadata
            git_sha: Git SHA hash
        """
        # NOTE: C extension for update_service is not compatible with GraphQL schema
        # The C implementation expects domains[] but schema expects service metadata
        # Therefore, we always use Python implementation here

        query = f"""
        {self.query_type} {self.operation_name}(
            $apiKey: String!,
            $serviceUuid: String!,
            $timestampMs: String!,
            $serviceIdentifier: String,
            $serviceVersion: String,
            $serviceAdditionalMetadata: JSON,
            $gitSha: String
        ) {{
            {self.query_name}(
                apiKey: $apiKey,
                serviceUuid: $serviceUuid,
                timestampMs: $timestampMs,
                serviceIdentifier: $serviceIdentifier,
                serviceVersion: $serviceVersion,
                serviceAdditionalMetadata: $serviceAdditionalMetadata,
                gitSha: $gitSha
            )
        }}
        """
        variables = self.get_variables(
            {
                "serviceIdentifier": service_identifier,
                "serviceVersion": service_version,
                "serviceAdditionalMetadata": service_additional_metadata,
                "gitSha": git_sha,
            },
        )

        non_blocking_post(self.endpoint, self.operation_name, query, variables)


class NetworkHopsTransmitter(DataTransmitter):
    """
    A transmitter class responsible for sending network hop data as a GraphQL mutation.

    This class extends `DataTransmitter` and sends `collectNetworkHops` mutation requests
    to log network hop details for a given session.

    Attributes:
        operation_name (str): The GraphQL mutation name ("collectNetworkHops").

    Methods:
        send(session_id: str, line: str, column: str, name: str, entrypoint: str):
            Sends a non-blocking GraphQL mutation request to log network hops.
    """

    def __init__(self, api_key: str = app_config._sailfish_api_key):
        super().__init__(api_key)
        self.operation_name = "collectNetworkHops"

    def send(
        self,
        session_id: str,
        line: str,
        column: str,
        name: str,
        entrypoint: str,
    ):
        query = f"""
        {self.query_type} {self.operation_name}(
            $apiKey: String!,
            $sessionId: String!,
            $timestampMs: String!,
            $line: String!,
            $column: String!,
            $name: String!,
            $entrypoint: String!,
            $serviceUuid: String
        ) {{
            {self.query_name}(
                apiKey: $apiKey,
                sessionId: $sessionId,
                timestampMs: $timestampMs,
                line: $line,
                column: $column,
                name: $name,
                entrypoint: $entrypoint,
                serviceUuid: $serviceUuid
            )
        }}
        """

        variables = self.get_variables(
            {
                "sessionId": session_id,
                "line": line,
                "column": column,
                "name": name,
                "entrypoint": entrypoint,
                "serviceUuid": app_config._service_uuid,
            }
        )
        if SF_DEBUG:
            print("[[NetworkHopsTransmitter.send]] variables=", variables, log=False)
        non_blocking_post(self.endpoint, self.operation_name, query, variables)


class NetworkRequestTransmitter(DataTransmitter):
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        self.operation_name = "collectNetworkRequest"

    def send(
        self,
        request_id: str,
        page_visit_id: Optional[str],
        recording_session_id: str,
        service_uuid: str,
        timestamp_start: int,
        timestamp_end: int,
        response_code: int,
        success: bool,
        error: Optional[str],
        url: str,
        method: str,
    ):
        # build the mutation to match the new input type:
        query = f"""
        {self.query_type} {self.operation_name}($data: NetworkRequestInput!) {{
        {self.query_name}(data: $data)
        }}
        """

        # Only include fields expected by the NetworkRequestInput type
        variables = {
            "data": {
                "apiKey": self.api_key,
                "requestId": request_id,
                "pageVisitId": page_visit_id,
                "recordingSessionId": recording_session_id,
                "serviceUuid": app_config._service_uuid,
                "timestampStart": timestamp_start,
                "timestampEnd": timestamp_end,
                "responseCode": response_code,
                "success": success,
                "error": error,
                "url": url,
                "method": method,
            }
        }

        if SF_DEBUG:
            print(f"[NetworkRequestTransmitter] variables={variables}", log=False)

        non_blocking_post(self.endpoint, self.operation_name, query, variables)
