"""
DVT Profile Registration Task

Interactive CLI for registering new database profiles.
Discovers installed adapters and walks users through credential input.
"""

import getpass
import importlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click
import yaml

from dvt.cli.flags import Flags
from dvt.events.types import Note
from dvt.task.base import BaseTask

from dbt_common.events.functions import fire_event
from dbt_common.ui import green, red, yellow, cyan


# Common adapter credential schemas
ADAPTER_SCHEMAS = {
    "postgres": {
        "fields": [
            {"name": "host", "prompt": "Host", "required": True, "default": "localhost"},
            {"name": "port", "prompt": "Port", "required": True, "default": "5432", "type": "int"},
            {"name": "user", "prompt": "Username", "required": True},
            {"name": "password", "prompt": "Password", "required": True, "secret": True},
            {"name": "dbname", "prompt": "Database name", "required": True},
            {"name": "schema", "prompt": "Schema", "required": True, "default": "public"},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
        ],
    },
    "snowflake": {
        "fields": [
            {"name": "account", "prompt": "Account identifier", "required": True},
            {"name": "user", "prompt": "Username", "required": True},
            {"name": "password", "prompt": "Password", "required": True, "secret": True},
            {"name": "role", "prompt": "Role", "required": False},
            {"name": "database", "prompt": "Database", "required": True},
            {"name": "warehouse", "prompt": "Warehouse", "required": True},
            {"name": "schema", "prompt": "Schema", "required": True},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
        ],
    },
    "bigquery": {
        "fields": [
            {"name": "method", "prompt": "Auth method (oauth/service-account)", "required": True, "default": "oauth"},
            {"name": "project", "prompt": "Project ID", "required": True},
            {"name": "dataset", "prompt": "Dataset", "required": True},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
            {"name": "keyfile", "prompt": "Path to service account JSON (for service-account method)", "required": False},
        ],
    },
    "redshift": {
        "fields": [
            {"name": "host", "prompt": "Host", "required": True},
            {"name": "port", "prompt": "Port", "required": True, "default": "5439", "type": "int"},
            {"name": "user", "prompt": "Username", "required": True},
            {"name": "password", "prompt": "Password", "required": True, "secret": True},
            {"name": "dbname", "prompt": "Database name", "required": True},
            {"name": "schema", "prompt": "Schema", "required": True},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
        ],
    },
    "mysql": {
        "fields": [
            {"name": "host", "prompt": "Host", "required": True, "default": "localhost"},
            {"name": "port", "prompt": "Port", "required": True, "default": "3306", "type": "int"},
            {"name": "username", "prompt": "Username", "required": True},
            {"name": "password", "prompt": "Password", "required": True, "secret": True},
            {"name": "database", "prompt": "Database name", "required": True},
            {"name": "schema", "prompt": "Schema", "required": True},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
        ],
    },
    "databricks": {
        "fields": [
            {"name": "host", "prompt": "Host (workspace URL)", "required": True},
            {"name": "http_path", "prompt": "HTTP Path", "required": True},
            {"name": "token", "prompt": "Personal Access Token", "required": True, "secret": True},
            {"name": "catalog", "prompt": "Catalog", "required": False},
            {"name": "schema", "prompt": "Schema", "required": True},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
        ],
    },
    "duckdb": {
        "fields": [
            {"name": "path", "prompt": "Database path (or :memory: for in-memory)", "required": True, "default": ":memory:"},
            {"name": "schema", "prompt": "Schema", "required": False, "default": "main"},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
        ],
    },
    "spark": {
        "fields": [
            {"name": "method", "prompt": "Connection method (thrift/odbc/session)", "required": True, "default": "thrift"},
            {"name": "host", "prompt": "Host", "required": True, "default": "localhost"},
            {"name": "port", "prompt": "Port", "required": True, "default": "10000", "type": "int"},
            {"name": "schema", "prompt": "Schema", "required": True, "default": "default"},
            {"name": "user", "prompt": "Username", "required": False},
            {"name": "threads", "prompt": "Number of threads", "required": False, "default": "1", "type": "int"},
        ],
    },
}


class ProfileRegisterTask(BaseTask):
    """Interactive task to register a new database profile."""

    def __init__(self, args: Flags, profile_name: Optional[str] = None) -> None:
        super().__init__(args)
        self.profile_name = profile_name
        self.profiles_dir = Path(args.PROFILES_DIR)
        self.profile_path = self.profiles_dir / "profiles.yml"

    def discover_installed_adapters(self) -> List[Tuple[str, str]]:
        """
        Discover installed dbt adapters by scanning for dbt.adapters.* packages.

        Returns:
            List of (adapter_name, package_name) tuples
        """
        adapters = []

        # Common adapter packages to check
        common_adapters = [
            ("postgres", "dbt-postgres"),
            ("snowflake", "dbt-snowflake"),
            ("bigquery", "dbt-bigquery"),
            ("redshift", "dbt-redshift"),
            ("mysql", "dbt-mysql"),
            ("databricks", "dbt-databricks"),
            ("spark", "dbt-spark"),
            ("duckdb", "dbt-duckdb"),
            ("trino", "dbt-trino"),
            ("clickhouse", "dbt-clickhouse"),
            ("oracle", "dbt-oracle"),
            ("athena", "dbt-athena-community"),
        ]

        for adapter_name, package_name in common_adapters:
            try:
                # Try to import the adapter
                importlib.import_module(f"dbt.adapters.{adapter_name}")
                adapters.append((adapter_name, package_name))
            except ImportError:
                # Adapter not installed
                pass

        return adapters

    def prompt_adapter_selection(self, adapters: List[Tuple[str, str]]) -> Optional[str]:
        """
        Prompt user to select an adapter.

        Args:
            adapters: List of (adapter_name, package_name) tuples

        Returns:
            Selected adapter name or None
        """
        fire_event(Note(msg=""))
        fire_event(Note(msg=cyan("Select database adapter:")))
        fire_event(Note(msg=""))

        for i, (adapter_name, package_name) in enumerate(adapters, 1):
            fire_event(Note(msg=f"  {cyan(str(i))}. {green(adapter_name)} ({package_name})"))

        fire_event(Note(msg=""))

        while True:
            try:
                choice = click.prompt(
                    "Enter adapter number",
                    type=int,
                    default=1,
                )

                if 1 <= choice <= len(adapters):
                    selected_adapter = adapters[choice - 1][0]
                    fire_event(Note(msg=f"Selected: {green(selected_adapter)}"))
                    return selected_adapter
                else:
                    fire_event(Note(msg=red("Invalid choice. Please try again.")))
            except (ValueError, click.Abort):
                fire_event(Note(msg=red("Invalid input. Please enter a number.")))
                return None

    def prompt_profile_name(self) -> str:
        """
        Prompt for profile name if not provided.

        Returns:
            Profile name
        """
        fire_event(Note(msg=""))
        fire_event(Note(msg=cyan("Enter a name for this profile:")))
        fire_event(Note(msg=yellow("  (e.g., 'postgres_prod', 'snowflake_dev', 'bigquery_analytics')")))
        fire_event(Note(msg=""))

        while True:
            name = click.prompt("Profile name", default="")
            if name and name.strip():
                return name.strip()
            fire_event(Note(msg=red("Profile name cannot be empty. Please try again.")))

    def prompt_credentials(self, adapter_type: str) -> Dict[str, Any]:
        """
        Prompt for credentials based on adapter type.

        Args:
            adapter_type: Adapter type (e.g., 'postgres', 'snowflake')

        Returns:
            Dictionary of credentials
        """
        schema = ADAPTER_SCHEMAS.get(adapter_type)
        if not schema:
            # Generic schema for unknown adapters
            fire_event(Note(msg=yellow(f"No schema defined for '{adapter_type}'. Using generic prompts.")))
            schema = {
                "fields": [
                    {"name": "host", "prompt": "Host", "required": False},
                    {"name": "port", "prompt": "Port", "required": False, "type": "int"},
                    {"name": "user", "prompt": "Username", "required": False},
                    {"name": "password", "prompt": "Password", "required": False, "secret": True},
                    {"name": "database", "prompt": "Database", "required": False},
                    {"name": "schema", "prompt": "Schema", "required": False},
                ]
            }

        fire_event(Note(msg=""))
        fire_event(Note(msg=cyan("Enter credentials for this profile:")))
        fire_event(Note(msg=yellow("  (Press Enter to skip optional fields)")))
        fire_event(Note(msg=""))

        credentials = {"type": adapter_type}

        for field in schema["fields"]:
            field_name = field["name"]
            prompt_text = field["prompt"]
            required = field.get("required", False)
            default = field.get("default")
            is_secret = field.get("secret", False)
            field_type = field.get("type", "str")

            # Build prompt
            if required:
                prompt_display = f"{prompt_text} (required)"
            else:
                prompt_display = f"{prompt_text} (optional)"

            # Get value
            while True:
                try:
                    if is_secret:
                        # Use getpass for secrets
                        value = getpass.getpass(f"{prompt_display}: ")
                    else:
                        # Use click.prompt for non-secrets
                        if default:
                            value = click.prompt(prompt_display, default=default)
                        else:
                            value = click.prompt(prompt_display, default="")

                    # Skip empty optional fields
                    if not value and not required:
                        break

                    # Validate required fields
                    if required and not value:
                        fire_event(Note(msg=red("This field is required. Please try again.")))
                        continue

                    # Type conversion
                    if value:
                        if field_type == "int":
                            try:
                                value = int(value)
                            except ValueError:
                                fire_event(Note(msg=red("Please enter a valid number.")))
                                continue

                        credentials[field_name] = value

                    break

                except (click.Abort, KeyboardInterrupt):
                    fire_event(Note(msg=""))
                    fire_event(Note(msg=red("Registration cancelled.")))
                    return {}

        return credentials

    def append_to_profiles_yml(self, profile_name: str, profile_config: Dict[str, Any]) -> bool:
        """
        Append profile to profiles.yml file.

        Args:
            profile_name: Name of the profile
            profile_config: Profile configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure profiles directory exists
            self.profiles_dir.mkdir(parents=True, exist_ok=True)

            # Load existing profiles or create new structure
            if self.profile_path.exists():
                with open(self.profile_path, "r") as f:
                    try:
                        profiles_data = yaml.safe_load(f) or {}
                    except yaml.YAMLError:
                        fire_event(Note(msg=red(f"Error parsing {self.profile_path}")))
                        return False
            else:
                profiles_data = {}

            # Check if profile already exists
            if profile_name in profiles_data:
                fire_event(Note(msg=""))
                fire_event(Note(msg=yellow(f"Profile '{profile_name}' already exists.")))
                overwrite = click.confirm("Do you want to overwrite it?", default=False)
                if not overwrite:
                    fire_event(Note(msg="Registration cancelled."))
                    return False

            # Add new profile
            profiles_data[profile_name] = {
                "target": "dev",  # Default target
                "outputs": {
                    "dev": profile_config
                }
            }

            # Write back to file with nice formatting
            with open(self.profile_path, "w") as f:
                yaml.dump(
                    profiles_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2,
                )

            return True

        except Exception as e:
            fire_event(Note(msg=red(f"Error writing to profiles.yml: {str(e)}")))
            return False

    def run(self) -> bool:
        """Run the interactive profile registration."""
        fire_event(Note(msg=""))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=green("DVT Profile Registration")))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Profiles will be saved to: {self.profile_path}"))
        fire_event(Note(msg=""))

        # Step 1: Discover installed adapters
        fire_event(Note(msg="Discovering installed adapters..."))
        adapters = self.discover_installed_adapters()

        if not adapters:
            fire_event(Note(msg=""))
            fire_event(Note(msg=red("No adapters found!")))
            fire_event(Note(msg=""))
            fire_event(Note(msg="Please install at least one dbt adapter first:"))
            fire_event(Note(msg="  pip install dbt-postgres"))
            fire_event(Note(msg="  pip install dbt-snowflake"))
            fire_event(Note(msg="  pip install dbt-bigquery"))
            fire_event(Note(msg="  ...etc"))
            fire_event(Note(msg=""))
            return False

        fire_event(Note(msg=f"Found {len(adapters)} installed adapter(s)"))

        # Step 2: Select adapter
        adapter_type = self.prompt_adapter_selection(adapters)
        if not adapter_type:
            return False

        # Step 3: Get profile name
        if not self.profile_name:
            self.profile_name = self.prompt_profile_name()

        # Step 4: Gather credentials
        credentials = self.prompt_credentials(adapter_type)
        if not credentials:
            return False

        # Step 5: Confirm and save
        fire_event(Note(msg=""))
        fire_event(Note(msg=cyan("Profile Summary:")))
        fire_event(Note(msg=f"  Name: {green(self.profile_name)}"))
        fire_event(Note(msg=f"  Type: {green(adapter_type)}"))
        fire_event(Note(msg="  Credentials: (provided)"))
        fire_event(Note(msg=""))

        confirm = click.confirm("Save this profile?", default=True)
        if not confirm:
            fire_event(Note(msg="Registration cancelled."))
            return False

        # Save to profiles.yml
        fire_event(Note(msg=""))
        fire_event(Note(msg="Saving profile..."))

        if self.append_to_profiles_yml(self.profile_name, credentials):
            fire_event(Note(msg=""))
            fire_event(Note(msg=green("✓ Profile registered successfully!")))
            fire_event(Note(msg=""))
            fire_event(Note(msg="Next steps:"))
            fire_event(Note(msg=f"  • Test connection: dvt profiles test {self.profile_name}"))
            fire_event(Note(msg=f"  • View profile: dvt profiles show {self.profile_name}"))
            fire_event(Note(msg=f"  • Use in project: Set target: {self.profile_name} in dbt_project.yml"))
            fire_event(Note(msg=""))
            return True
        else:
            return False

    def interpret_results(self, results) -> bool:
        return results
