"""
Extended profile configuration for DVT unified profiles.

This module extends dbt's profile system to support:
- Multiple named profiles in one file (not just outputs)
- Profile references in sources
- Backward compatibility with dbt profiles
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from dbt_common.events.functions import fire_event
from dbt_common.events.types import Note
from dbt_common.exceptions import DbtRuntimeError


@dataclass
class ProfileReference:
    """
    Reference to a named profile.

    This represents a connection configuration that can be used
    as either a source or a target.
    """

    name: str
    adapter: str
    credentials: Dict[str, Any]
    threads: int = 4

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ProfileReference":
        """
        Create ProfileReference from dictionary.

        Args:
            name: Profile name
            data: Profile configuration dictionary

        Returns:
            ProfileReference instance
        """
        # Extract adapter type (could be 'adapter' or 'type' for dbt compat)
        adapter = data.get("adapter") or data.get("type")
        if not adapter:
            raise DbtRuntimeError(f"Profile '{name}' missing 'adapter' or 'type' field")

        # Extract threads
        threads = data.get("threads", 4)

        # Everything else is credentials
        credentials = {k: v for k, v in data.items() if k not in ("adapter", "type", "threads")}

        return cls(
            name=name,
            adapter=adapter,
            credentials=credentials,
            threads=threads,
        )

    def to_connection_dict(self) -> Dict[str, Any]:
        """
        Convert to connection dictionary for adapter.

        Returns:
            Dictionary with adapter type and credentials
        """
        return {
            "type": self.adapter,
            "threads": self.threads,
            **self.credentials,
        }


class UnifiedProfileConfig:
    """
    Unified profile configuration supporting both DVT and dbt formats.

    DVT format (unified profiles):
        postgres_prod:
          adapter: postgres
          host: localhost
          port: 5432
          user: myuser
          # ... more credentials

        mysql_legacy:
          adapter: mysql
          host: legacy-db
          # ... more credentials

    dbt format (backward compatible):
        my_project:
          target: dev
          outputs:
            dev:
              type: postgres
              host: localhost
              # ... more credentials
    """

    def __init__(self, profiles: Dict[str, ProfileReference], dbt_profiles: Dict[str, Any]):
        """
        Initialize UnifiedProfileConfig.

        Args:
            profiles: Named profiles dictionary
            dbt_profiles: dbt-style profiles (for backward compat)
        """
        self.profiles = profiles
        self.dbt_profiles = dbt_profiles

    def get_profile(self, name: str) -> Optional[ProfileReference]:
        """
        Get profile by name.

        Args:
            name: Profile name

        Returns:
            ProfileReference or None if not found
        """
        return self.profiles.get(name)

    def get_dbt_profile(self, name: str) -> Optional[Any]:
        """
        Get dbt-style profile by name.

        Args:
            name: Profile name

        Returns:
            DbtProfile dict or None if not found
        """
        return self.dbt_profiles.get(name)

    def has_profile(self, name: str) -> bool:
        """Check if profile exists."""
        return name in self.profiles or name in self.dbt_profiles

    def list_profiles(self) -> list[str]:
        """List all available profile names."""
        return sorted(set(list(self.profiles.keys()) + list(self.dbt_profiles.keys())))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnifiedProfileConfig":
        """
        Parse profiles from dictionary.

        Supports both DVT unified format and dbt format.

        Args:
            data: Parsed YAML dictionary

        Returns:
            UnifiedProfileConfig instance
        """
        profiles: Dict[str, ProfileReference] = {}
        dbt_profiles: Dict[str, DbtProfile] = {}

        for name, config in data.items():
            if isinstance(config, dict):
                # Check if this is dbt format (has 'target' and 'outputs')
                if "target" in config and "outputs" in config:
                    # This is a dbt-style profile - skip for now
                    # We'll handle these with dbt's Profile class
                    dbt_profiles[name] = config  # Store raw config for now
                else:
                    # Check if this has 'adapter' or 'type' field (unified format)
                    if "adapter" in config or "type" in config:
                        try:
                            profiles[name] = ProfileReference.from_dict(name, config)
                        except Exception as e:
                            fire_event(Note(msg=f"Failed to parse profile '{name}': {e}"))
                    else:
                        # Could be a nested profile reference or other structure
                        # Check if it has a 'profile' key (reference to another profile)
                        if "profile" in config:
                            # This is a reference - handle in dbt compat layer
                            pass

        return cls(profiles=profiles, dbt_profiles=dbt_profiles)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "UnifiedProfileConfig":
        """
        Load profiles from YAML file.

        Args:
            file_path: Path to profiles.yml

        Returns:
            UnifiedProfileConfig instance

        Raises:
            DbtRuntimeError: If file cannot be read or parsed
        """
        try:
            if not file_path.exists():
                fire_event(Note(msg=f"Profiles file not found at {file_path}"))
                return cls(profiles={}, dbt_profiles={})

            with open(file_path, "r") as f:
                data = yaml.safe_load(f)

            if data is None:
                fire_event(Note(msg=f"Empty profiles file at {file_path}"))
                return cls(profiles={}, dbt_profiles={})

            return cls.from_dict(data)

        except yaml.YAMLError as e:
            raise DbtRuntimeError(f"Failed to parse profiles: {e}")
        except Exception as e:
            raise DbtRuntimeError(f"Failed to load profiles from {file_path}: {e}")


def load_unified_profiles(project_dir: Optional[Path] = None) -> UnifiedProfileConfig:
    """
    Load unified profiles from standard locations.

    Searches in order:
    1. <project_root>/profiles.yml
    2. ~/.dbt/profiles.yml
    3. Empty configuration

    Args:
        project_dir: Project directory (optional)

    Returns:
        UnifiedProfileConfig instance
    """
    # Try project directory first
    if project_dir:
        project_profiles = project_dir / "profiles.yml"
        if project_profiles.exists():
            fire_event(Note(msg=f"Loading profiles from {project_profiles}"))
            return UnifiedProfileConfig.load_from_file(project_profiles)

    # Try home directory (standard dbt location)
    home_profiles = Path.home() / ".dbt" / "profiles.yml"
    if home_profiles.exists():
        fire_event(Note(msg=f"Loading profiles from {home_profiles}"))
        return UnifiedProfileConfig.load_from_file(home_profiles)

    # Empty configuration
    fire_event(Note(msg="No profiles.yml found"))
    return UnifiedProfileConfig(profiles={}, dbt_profiles={})


def resolve_profile_reference(
    profile_name: str,
    unified_profiles: UnifiedProfileConfig,
) -> Optional[Dict[str, Any]]:
    """
    Resolve a profile reference to connection configuration.

    Args:
        profile_name: Name of profile to resolve
        unified_profiles: Unified profile configuration

    Returns:
        Connection dictionary or None if not found
    """
    # Try unified profile first
    profile = unified_profiles.get_profile(profile_name)
    if profile:
        return profile.to_connection_dict()

    # Try dbt profile
    dbt_profile = unified_profiles.get_dbt_profile(profile_name)
    if dbt_profile:
        # Return raw config - will be processed by dbt's Profile class
        return dbt_profile

    return None


class ProfileRegistry:
    """
    Registry for managing profile instances during execution.

    This keeps track of all profiles referenced by sources and models,
    and ensures they're properly initialized for use by compute engines.

    Usage:
        # In CLI commands
        registry = ProfileRegistry(unified_profiles)
        profile = registry.get_or_create_profile("postgres_prod")

        # Test all profiles
        results = registry.test_all_profiles()

        # Get adapter for a profile
        adapter = registry.get_adapter("postgres_prod", mp_context)
    """

    def __init__(self, unified_profiles: UnifiedProfileConfig):
        """
        Initialize ProfileRegistry.

        Args:
            unified_profiles: Unified profile configuration
        """
        self.unified_profiles = unified_profiles
        self._initialized_profiles: Dict[str, Any] = {}
        self._adapters: Dict[str, Any] = {}

    def get_or_create_profile(self, profile_name: str) -> Optional[Any]:
        """
        Get or create profile instance.

        Args:
            profile_name: Profile name

        Returns:
            Profile instance or None if not found
        """
        # Check cache
        if profile_name in self._initialized_profiles:
            return self._initialized_profiles[profile_name]

        # Resolve profile
        profile_config = resolve_profile_reference(profile_name, self.unified_profiles)
        if not profile_config:
            return None

        # Create profile instance
        # For now, store the config. Full adapter integration happens in get_adapter()
        self._initialized_profiles[profile_name] = profile_config

        return profile_config

    def get_adapter(self, profile_name: str, mp_context: Optional[Any] = None) -> Optional[Any]:
        """
        Get adapter instance for a profile.

        This creates and caches adapter instances for profiles.
        Requires multiprocessing context for adapter initialization.

        Args:
            profile_name: Profile name
            mp_context: Multiprocessing context (required for adapter creation)

        Returns:
            Adapter instance or None if profile not found
        """
        # Check cache
        if profile_name in self._adapters:
            return self._adapters[profile_name]

        # Get profile config
        profile = self.get_or_create_profile(profile_name)
        if not profile:
            return None

        # Need mp_context to create adapters
        if not mp_context:
            raise DbtRuntimeError(
                "mp_context required to create adapter instances. "
                "Use get_or_create_profile() for config-only access."
            )

        # Create adapter using MultiAdapterManager
        from dvt.adapters.multi_adapter_manager import MultiAdapterManager

        manager = MultiAdapterManager(self.unified_profiles, mp_context)
        adapter = manager.get_or_create_adapter(profile_name)
        self._adapters[profile_name] = adapter

        return adapter

    def list_all_profiles(self) -> list[str]:
        """
        List all available profile names.

        Returns:
            List of profile names from unified profiles
        """
        return self.unified_profiles.list_profiles()

    def list_initialized_profiles(self) -> list[str]:
        """
        List profile names that have been initialized.

        Returns:
            List of cached profile names
        """
        return list(self._initialized_profiles.keys())

    def test_profile(self, profile_name: str, mp_context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Test a single profile connection.

        Args:
            profile_name: Profile name to test
            mp_context: Multiprocessing context for adapter initialization

        Returns:
            Test result dictionary with 'success', 'message', and optional 'error' keys
        """
        try:
            # Get profile config
            profile = self.get_or_create_profile(profile_name)
            if not profile:
                return {
                    "success": False,
                    "profile": profile_name,
                    "message": f"Profile '{profile_name}' not found",
                }

            # If mp_context provided, test actual connection
            if mp_context:
                adapter = self.get_adapter(profile_name, mp_context)
                if adapter:
                    # Try to connect
                    # Note: Different adapters have different connection methods
                    # For now, just verify adapter creation succeeded
                    return {
                        "success": True,
                        "profile": profile_name,
                        "adapter_type": getattr(profile, "adapter", "unknown"),
                        "message": "Profile configuration valid and adapter created",
                    }

            # Without mp_context, just verify config is loadable
            return {
                "success": True,
                "profile": profile_name,
                "adapter_type": getattr(profile, "adapter", "unknown"),
                "message": "Profile configuration valid",
            }

        except Exception as e:
            return {
                "success": False,
                "profile": profile_name,
                "message": f"Profile test failed: {str(e)}",
                "error": str(e),
            }

    def test_all_profiles(self, mp_context: Optional[Any] = None) -> Dict[str, Dict[str, Any]]:
        """
        Test all available profiles.

        Args:
            mp_context: Multiprocessing context for adapter initialization

        Returns:
            Dictionary mapping profile names to test results
        """
        results = {}
        for profile_name in self.list_all_profiles():
            results[profile_name] = self.test_profile(profile_name, mp_context)
        return results

    def clear_cache(self) -> None:
        """Clear profile and adapter instance caches."""
        self._initialized_profiles.clear()
        self._adapters.clear()
