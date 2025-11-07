from typing import Any, Dict, Optional

from .env_vars import SF_DEBUG
from .thread_local import get_or_set_sf_trace_id

# Try to import C extension for fast path
try:
    from . import _sfservice
    _SFSERVICE_AVAILABLE = True
except Exception:
    _sfservice = None
    _SFSERVICE_AVAILABLE = False

# Always have Python fallback available (lazy-loaded when needed)
collect_metadata_transmitter = None


class SailfishTransmitter(object):
    @classmethod
    def identify(
        cls,
        user_id: str,
        traits: Optional[Dict[str, Any]] = None,
        traits_json: Optional[str] = None,
        override: bool = False,
    ) -> None:
        if traits is not None or traits_json is not None:
            return cls.add_or_update_metadata(user_id, traits, traits_json, override)
        return cls.add_or_update_metadata(user_id, dict(), override=override)

    @classmethod
    def update_service_details(
        cls,
        service_identifier: Optional[str] = None,
        service_version: Optional[str] = None,
        service_additional_metadata: Optional[Dict[str, Any]] = None,
        git_sha: Optional[str] = None,
    ) -> None:
        """
        Updates service details with metadata.
        Sends mutation updateServiceDetails (Python implementation - no C extension yet).

        Args:
            service_identifier: Service identifier string
            service_version: Service version string
            service_additional_metadata: Dictionary of additional metadata
            git_sha: Git SHA hash
        """
        # Import here to avoid circular dependency
        from .regular_data_transmitter import UpdateServiceIdentifierMetadata

        transmitter = UpdateServiceIdentifierMetadata()
        transmitter.send(
            service_identifier=service_identifier,
            service_version=service_version,
            service_additional_metadata=service_additional_metadata,
            git_sha=git_sha,
        )

        if SF_DEBUG:
            print(f"[[DEBUG]] update_service_details sent: id={service_identifier}, version={service_version}, sha={git_sha}", log=False)

    @classmethod
    def add_or_update_metadata(
        cls,
        user_id: str,
        traits: Optional[Dict[str, Any]] = None,
        traits_json: Optional[str] = None,
        override: bool = False,
    ) -> None:
        """
        Sets traits and sends to the Sailfish AI backend

        Args:
            user_id: unique identifier for the user; common uses are username or email
            traits: dictionary of contents to add or update in the user's traits. Defaults to None.
            traits_json: json string of contents to add or update in the user's traits. Defaults to None.
        """
        if traits is None and traits_json is None:
            raise Exception(
                'Must pass in either traits or traits_json to "add_or_update_traits"'
            )
        if SF_DEBUG:
            print(
                "[[DEBUG - add_or_update_traits]] starting thread [[/DEBUG]]", log=False
            )

        _, trace_id = get_or_set_sf_trace_id()
        if SF_DEBUG:
            print(
                "add_or_update_metadata...SENDING DATA...args=",
                (user_id, traits, traits_json, override, trace_id),
                trace_id,
                log=False,
            )

        # Fast path: Use C extension if available
        if _SFSERVICE_AVAILABLE and _sfservice:
            try:
                excluded_fields = []

                # If traits is provided as dict, serialize it
                if traits_json is None:
                    from .utils import serialize_json_with_exclusions
                    traits_json, excluded_fields = serialize_json_with_exclusions(traits)

                # Call C extension
                _sfservice.collect_metadata(
                    session_id=str(trace_id),
                    user_id=user_id,
                    traits_json=traits_json,
                    excluded_fields=excluded_fields,
                    override=override,
                )

                if SF_DEBUG:
                    print("[[DEBUG]] collect_metadata sent via _sfservice C extension", log=False)
                return
            except Exception as e:
                if SF_DEBUG:
                    print(f"[[DEBUG]] Failed to send via C extension: {e}, falling back to Python", log=False)
                # Fall through to Python implementation

        # Fallback: Use Python implementation (lazy-load if needed)
        global collect_metadata_transmitter
        if collect_metadata_transmitter is None:
            from .interceptors import CollectMetadataTransmitter
            collect_metadata_transmitter = CollectMetadataTransmitter()

        collect_metadata_transmitter.do_send(
            (user_id, traits, traits_json, override, trace_id), trace_id
        )
