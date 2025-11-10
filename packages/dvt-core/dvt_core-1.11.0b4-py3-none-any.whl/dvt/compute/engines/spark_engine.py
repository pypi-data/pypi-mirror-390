"""
Spark compute engine implementation.

This module provides DVT's Spark compute layer for large-scale processing
of heterogeneous data sources.

DVT uses dbt adapters for data extraction, eliminating the need for JDBC JARs:
- Data extracted via dbt adapters (Python)
- Converted to Arrow format for efficient transfer
- Loaded into Spark DataFrames
- No JDBC drivers or JAR management required
"""

from datetime import datetime
from typing import Any, Optional, Tuple, Union

from dvt.compute.base import (
    BaseComputeEngine,
    ComputeResult,
    ExecutionStrategy,
    QueryExecutionPlan,
)
from dvt.config.compute_config import SparkClusterConfig, SparkLocalConfig
from dvt.events import fire_event
from dvt.events.types import Note

from dbt.adapters.exceptions import DbtRuntimeError

# PySpark import - will fail gracefully if not installed
try:
    from pyspark.sql import SparkSession

    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    SparkSession = None


class SparkEngine(BaseComputeEngine):
    """
    Spark compute engine for DVT.

    Supports both local (single-node) and cluster (distributed) modes.
    """

    def __init__(
        self,
        config: Union[SparkLocalConfig, SparkClusterConfig],
        profile_registry: Any,
        mode: str = "local",
    ):
        """
        Initialize Spark engine.

        Args:
            config: Spark configuration (local or cluster)
            profile_registry: Registry for resolving profile connections
            mode: 'local' or 'cluster'
        """
        super().__init__(config=config.__dict__)
        self.spark_config = config
        self.profile_registry = profile_registry
        self.mode = mode
        self.spark: Optional[Any] = None  # SparkSession

    def initialize(self) -> None:
        """Initialize Spark session and load connectors."""
        if not PYSPARK_AVAILABLE:
            raise DbtRuntimeError("PySpark is not installed. Install with: pip install pyspark")

        try:
            fire_event(Note(msg=f"Initializing Spark engine ({self.mode} mode)"))

            # Create Spark session builder
            builder = SparkSession.builder.appName(self.spark_config.app_name)

            # Set master
            builder = builder.master(self.spark_config.master)

            # Set memory and cores
            if hasattr(self.spark_config, "memory"):
                builder = builder.config("spark.executor.memory", self.spark_config.memory)
            if hasattr(self.spark_config, "driver_memory"):
                builder = builder.config("spark.driver.memory", self.spark_config.driver_memory)
            if hasattr(self.spark_config, "executor_cores"):
                builder = builder.config(
                    "spark.executor.cores", str(self.spark_config.executor_cores)
                )

            # Apply additional config
            for key, value in self.spark_config.config.items():
                builder = builder.config(key, value)

            # Note: No JDBC JARs needed - DVT uses dbt adapters for data extraction

            # Create session
            self.spark = builder.getOrCreate()

            # Set log level
            self.spark.sparkContext.setLogLevel(self.spark_config.log_level)

            self._initialized = True
            fire_event(Note(msg="Spark engine initialized successfully"))

        except Exception as e:
            raise DbtRuntimeError(f"Failed to initialize Spark engine: {e}")

    def shutdown(self) -> None:
        """Shutdown Spark session."""
        if self.spark:
            try:
                self.spark.stop()
                fire_event(Note(msg="Spark engine shutdown"))
            except Exception as e:
                fire_event(Note(msg=f"Error shutting down Spark: {e}"))
            finally:
                self.spark = None
                self._initialized = False

    def execute_query(
        self,
        sql: str,
        execution_plan: QueryExecutionPlan,
    ) -> ComputeResult:
        """
        Execute SQL query in Spark.

        Args:
            sql: SQL query to execute
            execution_plan: Execution plan with source information

        Returns:
            ComputeResult
        """
        if not self._initialized or not self.spark:
            return ComputeResult(
                success=False,
                error="Spark engine not initialized",
            )

        try:
            start_time = datetime.now()

            # Register source tables
            for source in execution_plan.sources:
                self._register_source(source.profile_name, source.adapter_type, source.relation)

            # Execute query
            df = self.spark.sql(sql)

            # Get row count (triggers execution)
            rows_affected = df.count()

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return ComputeResult(
                success=True,
                rows_affected=rows_affected,
                execution_time_ms=execution_time,
                strategy_used=ExecutionStrategy.COMPUTE_LAYER,
                compute_engine_used=f"spark_{self.mode}",
            )

        except Exception as e:
            return ComputeResult(
                success=False,
                error=str(e),
                strategy_used=ExecutionStrategy.COMPUTE_LAYER,
                compute_engine_used=f"spark_{self.mode}",
            )

    def _register_source(self, profile_name: str, adapter_type: str, relation: Any) -> None:
        """
        Register a source table in Spark.

        TODO: Replace with dbt adapter-based extraction:
        1. Get dbt adapter for profile
        2. Execute SELECT * FROM table via adapter
        3. Convert Agate table to Arrow
        4. Create Spark DataFrame from Arrow
        5. Register as temp view

        Args:
            profile_name: Profile name
            adapter_type: Adapter type
            relation: Relation object
        """
        # TODO: Implement dbt adapter-based extraction
        # For now, this is a placeholder
        fire_event(
            Note(
                msg=f"TODO: Extract {relation} from {profile_name} via dbt adapter (not yet implemented)"
            )
        )

    def can_handle(self, execution_plan: QueryExecutionPlan) -> bool:
        """
        Check if Spark can handle this execution plan.

        Spark can handle any database with a dbt adapter (uses adapter-based extraction).

        Args:
            execution_plan: Execution plan

        Returns:
            True if Spark can handle it
        """
        # Spark can handle any source with a dbt adapter
        # Data extracted via adapter, converted to Arrow, loaded into Spark
        return True

    def estimate_cost(self, execution_plan: QueryExecutionPlan) -> float:
        """
        Estimate cost of executing with Spark.

        Spark has higher overhead but scales better:
        - Small data (< 1GB): High cost (DuckDB is better)
        - Medium data (1-10GB): Medium cost
        - Large data (> 10GB): Low cost (Spark shines here)

        Args:
            execution_plan: Execution plan

        Returns:
            Cost estimate
        """
        data_size_gb = execution_plan.estimated_data_size_mb / 1024

        if self.mode == "local":
            # Local mode has startup overhead
            if data_size_gb < 1:
                return 80.0  # High cost for small data
            elif data_size_gb < 10:
                return 40.0  # Medium cost
            else:
                return 20.0  # Low cost for large data
        else:
            # Cluster mode has even more overhead but scales better
            if data_size_gb < 10:
                return 100.0  # Very high cost for small/medium data
            elif data_size_gb < 100:
                return 30.0  # Medium cost
            else:
                return 10.0  # Very low cost for huge data

    def get_engine_name(self) -> str:
        """Get engine name."""
        return f"spark_{self.mode}"

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test if Spark is available and working.

        Returns:
            (success, error_message)
        """
        if not PYSPARK_AVAILABLE:
            return (False, "PySpark not installed")

        try:
            # Try to create a session
            spark = (
                SparkSession.builder.master("local[1]")
                .appName("dvt-test")
                .config("spark.ui.enabled", "false")
                .getOrCreate()
            )
            spark.sql("SELECT 1").collect()
            spark.stop()
            return (True, None)
        except Exception as e:
            return (False, str(e))
