"""
DuckDB compute engine implementation.

This module provides DVT's DuckDB compute layer for processing heterogeneous
data sources using dbt adapters for data extraction.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from dvt.compute.base import (
    BaseComputeEngine,
    ComputeResult,
    ExecutionStrategy,
    QueryExecutionPlan,
)
from dvt.compute.data_extractor import DataExtractor
from dvt.config.compute_config import DuckDBConfig
from dvt.events import fire_event
from dvt.events.types import Note

from dbt.adapters.exceptions import DbtRuntimeError

# DuckDB import - will fail gracefully if not installed
try:
    import duckdb

    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    duckdb = None


class DuckDBEngine(BaseComputeEngine):
    """
    DuckDB compute engine for DVT.

    Uses dbt adapters to extract data from source databases, converts to Arrow format,
    and registers Arrow tables in DuckDB for querying. This approach eliminates the need
    for database-specific scanners and works with any database that has a dbt adapter.

    Architecture:
        Source DB → dbt adapter → Arrow Table → DuckDB register() → Query execution
    """

    def __init__(self, config: DuckDBConfig, profile_registry: Any):
        """
        Initialize DuckDB engine.

        Args:
            config: DuckDB configuration
            profile_registry: Registry for resolving profile connections
        """
        super().__init__(config=config.__dict__)
        self.duckdb_config = config
        self.profile_registry = profile_registry
        self.connection: Optional[Any] = None  # duckdb.DuckDBPyConnection
        self._attached_profiles: set[str] = set()

    def initialize(self) -> None:
        """Initialize DuckDB connection and load extensions."""
        if not DUCKDB_AVAILABLE:
            raise DbtRuntimeError("DuckDB is not installed. Install with: pip install duckdb")

        try:
            fire_event(Note(msg="Initializing DuckDB compute engine"))

            # Create in-memory connection
            self.connection = duckdb.connect(":memory:")

            # Configure DuckDB settings
            self.connection.execute(f"SET memory_limit='{self.duckdb_config.memory_limit}'")
            self.connection.execute(f"SET threads={self.duckdb_config.threads}")
            self.connection.execute(f"SET max_memory='{self.duckdb_config.max_memory}'")
            self.connection.execute(f"SET temp_directory='{self.duckdb_config.temp_directory}'")

            # Enable/disable features
            if not self.duckdb_config.enable_optimizer:
                self.connection.execute("SET enable_optimizer=false")
            if self.duckdb_config.enable_profiling:
                self.connection.execute("SET enable_profiling=true")
            if self.duckdb_config.enable_progress_bar:
                self.connection.execute("SET enable_progress_bar=true")

            # Install and load extensions
            for ext in self.duckdb_config.extensions:
                try:
                    fire_event(Note(msg=f"Installing DuckDB extension: {ext}"))
                    self.connection.execute(f"INSTALL {ext}")
                    self.connection.execute(f"LOAD {ext}")
                except Exception as e:
                    fire_event(Note(msg=f"Failed to load extension {ext}: {e}"))

            # Configure S3 if specified
            if self.duckdb_config.s3:
                self._configure_s3()

            self._initialized = True
            fire_event(Note(msg="DuckDB engine initialized successfully"))

        except Exception as e:
            raise DbtRuntimeError(f"Failed to initialize DuckDB engine: {e}")

    def shutdown(self) -> None:
        """Shutdown DuckDB connection."""
        if self.connection:
            try:
                self.connection.close()
                fire_event(Note(msg="DuckDB engine shutdown"))
            except Exception as e:
                fire_event(Note(msg=f"Error shutting down DuckDB: {e}"))
            finally:
                self.connection = None
                self._initialized = False
                self._attached_profiles.clear()

    def execute_query(
        self,
        sql: str,
        execution_plan: QueryExecutionPlan,
    ) -> ComputeResult:
        """
        Execute SQL query in DuckDB.

        Args:
            sql: SQL query to execute
            execution_plan: Execution plan with source information

        Returns:
            ComputeResult
        """
        if not self._initialized or not self.connection:
            return ComputeResult(
                success=False,
                error="DuckDB engine not initialized",
            )

        try:
            start_time = datetime.now()

            # Attach source databases
            for source in execution_plan.sources:
                self._attach_profile(source.profile_name, source.adapter_type)

            # Execute query
            result = self.connection.execute(sql)

            # Get row count if available
            try:
                rows_affected = len(result.fetchall()) if result else 0
            except Exception:
                rows_affected = 0

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return ComputeResult(
                success=True,
                rows_affected=rows_affected,
                execution_time_ms=execution_time,
                strategy_used=ExecutionStrategy.COMPUTE_LAYER,
                compute_engine_used="duckdb",
                metadata={
                    "attached_profiles": list(self._attached_profiles),
                },
            )

        except Exception as e:
            return ComputeResult(
                success=False,
                error=str(e),
                strategy_used=ExecutionStrategy.COMPUTE_LAYER,
                compute_engine_used="duckdb",
            )

    def _attach_profile(self, profile_name: str, adapter_type: str) -> None:
        """
        Attach a profile to DuckDB for querying.

        Uses dbt adapter to extract data and register as Arrow table in DuckDB.
        This approach works with any database that has a dbt adapter.

        Args:
            profile_name: Profile name
            adapter_type: Adapter type (postgres, mysql, etc.)
        """
        # Skip if already attached
        if profile_name in self._attached_profiles:
            return

        # Get dbt adapter for this profile
        adapter = self.profile_registry.get_or_create_adapter(profile_name)
        if not adapter:
            raise DbtRuntimeError(f"Could not create adapter for profile '{profile_name}'")

        fire_event(Note(msg=f"Profile '{profile_name}' ready for data extraction"))

        # Mark as attached
        # Note: Actual data extraction happens on-demand when sources are referenced
        self._attached_profiles.add(profile_name)

    def _extract_and_register(self, profile_name: str, relation: Any, alias: str) -> None:
        """
        Extract data from a source and register it in DuckDB.

        This method is called when a source table needs to be loaded for querying.

        Args:
            profile_name: Profile name
            relation: Relation object (table/view to extract)
            alias: Alias to use when registering in DuckDB
        """
        # Get dbt adapter for this profile
        adapter = self.profile_registry.get_or_create_adapter(profile_name)

        # Extract data via dbt adapter → Arrow
        arrow_table = DataExtractor.extract_relation(adapter, relation)

        # Register Arrow table in DuckDB
        self.connection.register(alias, arrow_table)

        fire_event(
            Note(
                msg=f"Registered {relation} from {profile_name} as '{alias}' in DuckDB "
                f"({len(arrow_table)} rows)"
            )
        )

    def can_handle(self, execution_plan: QueryExecutionPlan) -> bool:
        """
        Check if DuckDB can handle this execution plan.

        DuckDB can handle most queries, but:
        - Pushdown-only queries should go to pushdown engine
        - Very large datasets (> 1TB) should use Spark

        Args:
            execution_plan: Execution plan

        Returns:
            True if DuckDB can handle it
        """
        # DuckDB can handle up to ~1TB of data efficiently
        if execution_plan.estimated_data_size_mb > 1024 * 1024:  # 1TB
            return False

        # Check if all adapters are supported
        supported_adapters = {"postgres", "mysql", "s3", "duckdb"}
        for source in execution_plan.sources:
            if source.adapter_type not in supported_adapters:
                fire_event(
                    Note(msg=f"Adapter '{source.adapter_type}' not supported by DuckDB engine")
                )
                return False

        return True

    def estimate_cost(self, execution_plan: QueryExecutionPlan) -> float:
        """
        Estimate cost of executing with DuckDB.

        DuckDB is:
        - Very fast for small data (< 1GB)
        - Still good for medium data (1-100GB)
        - Gets slower for large data (> 100GB)

        Args:
            execution_plan: Execution plan

        Returns:
            Cost estimate
        """
        data_size_gb = execution_plan.estimated_data_size_mb / 1024

        if data_size_gb < 1:
            return 10.0  # Very low cost for small data
        elif data_size_gb < 10:
            return 20.0  # Low cost for medium-small data
        elif data_size_gb < 100:
            return 50.0  # Medium cost for medium data
        else:
            return 100.0  # High cost for large data (Spark might be better)

    def get_engine_name(self) -> str:
        """Get engine name."""
        return "duckdb"

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test if DuckDB is available and working.

        Returns:
            (success, error_message)
        """
        if not DUCKDB_AVAILABLE:
            return (False, "DuckDB not installed")

        try:
            # Try to create a connection
            conn = duckdb.connect(":memory:")
            conn.execute("SELECT 1")
            conn.close()
            return (True, None)
        except Exception as e:
            return (False, str(e))
