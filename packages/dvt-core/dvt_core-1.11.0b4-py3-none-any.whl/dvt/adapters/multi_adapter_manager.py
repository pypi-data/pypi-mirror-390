"""
Multi-adapter management for DVT.

This module extends dbt's single-adapter model to support multiple
adapter instances for different profiles (sources + targets).
"""

from multiprocessing.context import SpawnContext
from typing import Any, Dict, Optional

from dvt.config.profiles_v2 import (
    ProfileReference,
    ProfileRegistry,
    UnifiedProfileConfig,
)

from dbt.adapters.factory import FACTORY, get_adapter_class_by_name, load_plugin
from dbt.adapters.protocol import AdapterProtocol
from dbt_common.events.base_types import EventLevel
from dbt_common.events.functions import fire_event
from dbt_common.events.types import Note
from dbt_common.exceptions import DbtRuntimeError


class MultiAdapterManager:
    """
    Manages multiple adapter instances for different profiles.

    DVT extends dbt's single-adapter model by allowing:
    1. Multiple source connections (each with its own profile)
    2. Target connection (standard dbt output)
    3. Each profile can use a different adapter type

    Architecture:
    - Profile name -> Adapter instance mapping
    - Lazy initialization (create adapter when first referenced)
    - Cleanup management for all adapters
    - Integration with dbt's existing adapter factory
    """

    def __init__(self, unified_profiles: UnifiedProfileConfig, mp_context: SpawnContext):
        """
        Initialize MultiAdapterManager.

        Args:
            unified_profiles: Unified profile configuration
            mp_context: Multiprocessing context for adapter initialization
        """
        self.unified_profiles = unified_profiles
        self.mp_context = mp_context
        self._adapters: Dict[str, AdapterProtocol] = {}
        self._profile_to_adapter_type: Dict[str, str] = {}

    def get_or_create_adapter(
        self,
        profile_name: str,
        adapter_registered_log_level: Optional[EventLevel] = EventLevel.INFO,
    ) -> AdapterProtocol:
        """
        Get or create adapter instance for a profile.

        This is the main entry point for getting adapters by profile name.
        It handles:
        1. Checking if adapter already exists (cache)
        2. Loading profile configuration
        3. Loading adapter plugin if needed
        4. Creating and registering the adapter
        5. Caching for future use

        Args:
            profile_name: Name of the profile to get adapter for
            adapter_registered_log_level: Log level for adapter registration

        Returns:
            Adapter instance

        Raises:
            DbtRuntimeError: If profile not found or adapter creation fails
        """
        # Check cache
        if profile_name in self._adapters:
            return self._adapters[profile_name]

        # Get profile configuration
        profile = self.unified_profiles.get_profile(profile_name)
        if not profile:
            raise DbtRuntimeError(
                f"Profile '{profile_name}' not found in profiles configuration. "
                f"Available profiles: {', '.join(self.unified_profiles.list_profiles())}"
            )

        # Ensure adapter plugin is loaded
        adapter_type = profile.adapter
        try:
            load_plugin(adapter_type)
        except Exception as e:
            raise DbtRuntimeError(
                f"Failed to load adapter plugin '{adapter_type}' for profile '{profile_name}': {e}"
            )

        # Create adapter configuration
        # For DVT, we need to create a minimal AdapterRequiredConfig
        # The actual credentials will come from the profile
        adapter_config = self._create_adapter_config(profile)

        # Check if an adapter of this type already exists in dbt's FACTORY
        # If so, we can reuse it if the configuration matches
        # Otherwise, create a new instance
        try:
            existing_adapter = FACTORY.lookup_adapter(adapter_type)
            # Check if credentials match - if so, reuse
            if self._credentials_match(existing_adapter, profile):
                # Reusing existing adapter
                self._adapters[profile_name] = existing_adapter
                self._profile_to_adapter_type[profile_name] = adapter_type
                return existing_adapter
        except KeyError:
            # No existing adapter of this type
            pass

        # Create new adapter instance
        adapter_class = get_adapter_class_by_name(adapter_type)
        adapter_instance = adapter_class(adapter_config, self.mp_context)  # type: ignore[call-arg]

        # Cache the adapter
        self._adapters[profile_name] = adapter_instance
        self._profile_to_adapter_type[profile_name] = adapter_type

        return adapter_instance

    def _create_adapter_config(self, profile: ProfileReference) -> Any:
        """
        Create adapter configuration from ProfileReference.

        This converts DVT's ProfileReference to dbt's expected config format.
        We create a minimal config object that satisfies adapter requirements.

        Args:
            profile: Profile reference

        Returns:
            Configuration object for adapter initialization
        """
        # Import credentials class for this adapter type
        adapter_class = get_adapter_class_by_name(profile.adapter)
        credentials_class = adapter_class.Credentials  # type: ignore[attr-defined]

        # Create credentials instance from profile
        credentials_dict = {
            "type": profile.adapter,
            **profile.credentials,
        }
        credentials = credentials_class.from_dict(credentials_dict)  # type: ignore[attr-defined]

        # Create minimal config object
        # Note: This is a simplified config for DVT multi-adapter support
        # Full RuntimeConfig would have more fields, but adapters primarily need credentials
        class MinimalAdapterConfig:
            def __init__(self, creds, name, threads):
                self.credentials = creds
                self.project_name = name
                self.profile_name = name
                self.target_name = name
                self.threads = threads
                # Required protocol fields
                self.query_comment: Dict[str, Any] = {}
                self.cli_vars: Dict[str, Any] = {}
                self.target_path = "target"
                self.log_cache_events = False

        config = MinimalAdapterConfig(credentials, profile.name, profile.threads)
        return config

    def _credentials_match(self, adapter: AdapterProtocol, profile: ProfileReference) -> bool:
        """
        Check if adapter's credentials match the profile.

        Args:
            adapter: Existing adapter instance
            profile: Profile reference to compare

        Returns:
            True if credentials match, False otherwise
        """
        # Get adapter's credentials
        adapter_creds = adapter.config.credentials.to_dict()  # type: ignore[attr-defined]
        profile_creds = {
            "type": profile.adapter,
            **profile.credentials,
        }

        # Compare key fields (excluding transient fields like query comments)
        key_fields = ["type", "host", "port", "user", "database", "schema"]
        for field in key_fields:
            if field in adapter_creds or field in profile_creds:
                if adapter_creds.get(field) != profile_creds.get(field):
                    return False

        return True

    def get_adapter_for_source(self, source_node) -> AdapterProtocol:
        """
        Get adapter for a source node.

        Args:
            source_node: Source node with profile reference

        Returns:
            Adapter instance for the source's profile

        Raises:
            DbtRuntimeError: If source has no profile or profile not found
        """
        if not hasattr(source_node, "profile") or not source_node.profile:
            raise DbtRuntimeError(
                f"Source '{source_node.name}' has no profile reference. "
                "Sources must specify a profile in sources.yml"
            )

        return self.get_or_create_adapter(source_node.profile)

    def cleanup_all_adapters(self) -> None:
        """Clean up all managed adapters."""
        for profile_name, adapter in self._adapters.items():
            try:
                adapter.cleanup_connections()  # type: ignore[attr-defined]
                fire_event(Note(msg="Cleaned up adapter for profile '{}'".format(profile_name)))
            except Exception as e:
                fire_event(
                    Note(
                        msg="Error cleaning up adapter for profile '{}': {}".format(
                            profile_name, e
                        )
                    )
                )

        self._adapters.clear()
        self._profile_to_adapter_type.clear()

    def list_active_adapters(self) -> Dict[str, str]:
        """
        List all active adapters.

        Returns:
            Dictionary mapping profile name to adapter type
        """
        return dict(self._profile_to_adapter_type)

    def get_adapter_count(self) -> int:
        """Get number of active adapters."""
        return len(self._adapters)


def create_multi_adapter_manager(
    unified_profiles: UnifiedProfileConfig,
    mp_context: SpawnContext,
) -> MultiAdapterManager:
    """
    Create MultiAdapterManager instance.

    Args:
        unified_profiles: Unified profile configuration
        mp_context: Multiprocessing context

    Returns:
        MultiAdapterManager instance
    """
    return MultiAdapterManager(unified_profiles, mp_context)
