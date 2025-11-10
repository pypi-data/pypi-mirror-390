"""
DVT Profiles Tasks

This module implements profile management commands:
- list: List all configured profiles
- show: Show details of a specific profile
- test: Test one or all profiles
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dvt.cli.flags import Flags
from dvt.config.profiles_v2 import ProfileRegistry, load_unified_profiles
from dvt.events.types import Note
from dvt.mp_context import get_mp_context
from dvt.task.base import BaseTask

from dbt_common.events.functions import fire_event
from dbt_common.ui import green, red, yellow


class ProfilesListTask(BaseTask):
    """Task to list all configured profiles."""

    def __init__(self, args: Flags) -> None:
        super().__init__(args)
        self.profiles_dir = args.PROFILES_DIR
        self.profile_path = os.path.join(self.profiles_dir, "profiles.yml")

    def run(self) -> bool:
        """List all configured profiles."""
        fire_event(Note(msg=""))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg="DVT Profiles"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Using profiles.yml file at {self.profile_path}"))
        fire_event(Note(msg=""))

        # Load unified profiles
        project_dir = Path(self.args.PROJECT_DIR) if self.args.PROJECT_DIR else None
        unified_profiles = load_unified_profiles(project_dir)

        # Create registry
        registry = ProfileRegistry(unified_profiles)

        # Get all profiles
        all_profiles = registry.list_all_profiles()

        if not all_profiles:
            fire_event(Note(msg=red("No profiles found in profiles.yml")))
            return False

        fire_event(Note(msg=f"Found {len(all_profiles)} profile(s):\n"))

        # List each profile with adapter type
        for profile_name in all_profiles:
            profile_config = registry.get_or_create_profile(profile_name)
            if profile_config:
                adapter_type = profile_config.get("type", "unknown")
                fire_event(Note(msg=f"  • {green(profile_name)} ({adapter_type})"))
            else:
                fire_event(Note(msg=f"  • {red(profile_name)} (error loading)"))

        fire_event(Note(msg=""))
        fire_event(Note(msg=f"Use 'dvt profiles show <profile_name>' to see details"))
        fire_event(Note(msg=f"Use 'dvt profiles test [profile_name]' to test connections"))
        fire_event(Note(msg=""))

        return True

    def interpret_results(self, results) -> bool:
        return results


class ProfilesShowTask(BaseTask):
    """Task to show details of a specific profile."""

    def __init__(self, args: Flags, profile_name: str) -> None:
        super().__init__(args)
        self.profile_name = profile_name
        self.profiles_dir = args.PROFILES_DIR
        self.profile_path = os.path.join(self.profiles_dir, "profiles.yml")

    def run(self) -> bool:
        """Show details of a specific profile."""
        fire_event(Note(msg=""))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Profile: {self.profile_name}"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Using profiles.yml file at {self.profile_path}"))
        fire_event(Note(msg=""))

        # Load unified profiles
        project_dir = Path(self.args.PROJECT_DIR) if self.args.PROJECT_DIR else None
        unified_profiles = load_unified_profiles(project_dir)

        # Create registry
        registry = ProfileRegistry(unified_profiles)

        # Get profile config
        profile_config = registry.get_or_create_profile(self.profile_name)
        if not profile_config:
            fire_event(Note(msg=red(f"Profile '{self.profile_name}' not found")))
            fire_event(Note(msg=""))
            fire_event(Note(msg="Available profiles:"))
            for name in registry.list_all_profiles():
                fire_event(Note(msg=f"  • {name}"))
            fire_event(Note(msg=""))
            return False

        # Display profile details
        adapter_type = profile_config.get("type", "unknown")
        fire_event(Note(msg=f"Adapter Type: {green(adapter_type)}"))
        fire_event(Note(msg=""))
        fire_event(Note(msg="Configuration:"))

        # Show all config (except sensitive fields)
        sensitive_fields = {"password", "token", "private_key", "api_key", "secret"}
        for key, value in sorted(profile_config.items()):
            if key.lower() in sensitive_fields:
                fire_event(Note(msg=f"  {key}: {yellow('***REDACTED***')}"))
            else:
                fire_event(Note(msg=f"  {key}: {value}"))

        fire_event(Note(msg=""))
        fire_event(
            Note(msg=f"Use 'dvt profiles test {self.profile_name}' to test this connection")
        )
        fire_event(Note(msg=""))

        return True

    def interpret_results(self, results) -> bool:
        return results


class ProfilesTestTask(BaseTask):
    """Task to test one or all profiles."""

    def __init__(self, args: Flags, profile_name: Optional[str] = None) -> None:
        super().__init__(args)
        self.profile_name = profile_name
        self.profiles_dir = args.PROFILES_DIR
        self.profile_path = os.path.join(self.profiles_dir, "profiles.yml")

    def run(self) -> bool:
        """Test one or all profiles."""
        from dvt.config import Profile
        from dvt.config.renderer import ProfileRenderer

        from dbt.adapters.factory import get_adapter, register_adapter

        fire_event(Note(msg=""))
        fire_event(Note(msg="=" * 60))
        if self.profile_name:
            fire_event(Note(msg=f"Testing Profile: {self.profile_name}"))
        else:
            fire_event(Note(msg="Testing All Profiles"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Using profiles.yml file at {self.profile_path}"))
        fire_event(Note(msg=""))

        # Load unified profiles
        project_dir = Path(self.args.PROJECT_DIR) if self.args.PROJECT_DIR else None
        unified_profiles = load_unified_profiles(project_dir)

        # Create registry
        registry = ProfileRegistry(unified_profiles)

        # Determine which profiles to test
        if self.profile_name:
            profiles_to_test = [self.profile_name]
        else:
            profiles_to_test = registry.list_all_profiles()

        if not profiles_to_test:
            fire_event(Note(msg=red("No profiles to test")))
            return False

        # Test each profile
        results = {}
        for profile_name in profiles_to_test:
            fire_event(Note(msg=f"Testing {profile_name}..."))

            try:
                # Get profile config
                profile_config = registry.get_or_create_profile(profile_name)
                if not profile_config:
                    fire_event(Note(msg=red(f"  ✗ Profile '{profile_name}' not found")))
                    results[profile_name] = False
                    continue

                # Show adapter type
                adapter_type = profile_config.get("type", "unknown")
                fire_event(Note(msg=f"  Adapter: {adapter_type}"))

                # Create a Profile object for testing
                profile_data = {
                    "outputs": {
                        "test": profile_config,
                    },
                    "target": "test",
                }

                renderer = ProfileRenderer({})
                test_profile = Profile.from_raw_profile_info(
                    raw_profile=profile_data,
                    profile_name=profile_name,
                    target_override="test",
                    renderer=renderer,
                )

                # Test connection
                register_adapter(test_profile, get_mp_context())
                adapter = get_adapter(test_profile)

                try:
                    with adapter.connection_named("debug"):
                        adapter.debug_query()
                    fire_event(Note(msg=green(f"  ✓ Connection successful")))
                    results[profile_name] = True
                except Exception as exc:
                    fire_event(Note(msg=red(f"  ✗ Connection failed: {str(exc)}")))
                    results[profile_name] = False

            except Exception as e:
                fire_event(Note(msg=red(f"  ✗ Error: {str(e)}")))
                results[profile_name] = False

            fire_event(Note(msg=""))

        # Summary
        success_count = sum(1 for success in results.values() if success)
        fail_count = len(results) - success_count

        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg="Summary"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Total: {len(results)}"))
        fire_event(Note(msg=green(f"Passed: {success_count}")))
        if fail_count > 0:
            fire_event(Note(msg=red(f"Failed: {fail_count}")))

        fire_event(Note(msg=""))
        for profile_name, success in results.items():
            status = green("✓") if success else red("✗")
            fire_event(Note(msg=f"  {status} {profile_name}"))

        fire_event(Note(msg=""))

        return fail_count == 0

    def interpret_results(self, results) -> bool:
        return results
