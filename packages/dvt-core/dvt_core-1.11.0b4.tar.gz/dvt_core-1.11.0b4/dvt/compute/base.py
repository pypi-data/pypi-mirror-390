"""
Base compute engine abstraction.

This module defines the interface that all compute engines (DuckDB, Spark)
must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from dbt.adapters.base import BaseRelation


class ExecutionStrategy(Enum):
    """Strategy for executing a query."""

    PUSHDOWN = "pushdown"  # Execute on source database
    COMPUTE_LAYER = "compute_layer"  # Execute in DuckDB/Spark
    AUTO = "auto"  # Let DVT decide


@dataclass
class SourceInfo:
    """Information about a data source referenced in a query."""

    profile_name: str
    adapter_type: str
    relation: BaseRelation
    estimated_rows: Optional[int] = None
    estimated_size_mb: Optional[float] = None


@dataclass
class QueryExecutionPlan:
    """
    Execution plan for a query.

    This describes how DVT will execute the query (pushdown vs compute layer).
    """

    strategy: ExecutionStrategy
    compute_engine: Optional[str] = None  # 'duckdb', 'spark_local', 'spark_cluster'
    sources: List[SourceInfo] = field(default_factory=list)
    is_homogeneous: bool = True  # All sources same adapter
    estimated_data_size_mb: float = 0.0
    estimated_rows: int = 0
    pushdown_target: Optional[str] = None  # Which adapter to push down to
    reason: str = ""  # Explanation of strategy choice

    def is_pushdown_possible(self) -> bool:
        """Check if pushdown is possible."""
        return self.is_homogeneous and len(set(s.profile_name for s in self.sources)) == 1

    def get_unique_adapters(self) -> Set[str]:
        """Get set of unique adapter types."""
        return {s.adapter_type for s in self.sources}

    def get_unique_profiles(self) -> Set[str]:
        """Get set of unique profile names."""
        return {s.profile_name for s in self.sources}


@dataclass
class ComputeResult:
    """Result of compute engine execution."""

    success: bool
    rows_affected: int = 0
    execution_time_ms: float = 0.0
    strategy_used: Optional[ExecutionStrategy] = None
    compute_engine_used: Optional[str] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set execution timestamp."""
        self.metadata.setdefault("executed_at", datetime.now().isoformat())


class BaseComputeEngine(ABC):
    """
    Base class for compute engines.

    All compute engines (DuckDB, Spark) must implement this interface.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize compute engine.

        Args:
            config: Engine-specific configuration
        """
        self.config = config
        self._initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the compute engine.

        This is called once before any queries are executed.
        Should set up connections, load extensions, etc.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown the compute engine.

        Clean up resources, close connections, etc.
        """
        pass

    @abstractmethod
    def execute_query(
        self,
        sql: str,
        execution_plan: QueryExecutionPlan,
    ) -> ComputeResult:
        """
        Execute a SQL query using this compute engine.

        Args:
            sql: SQL query to execute
            execution_plan: Execution plan with source information

        Returns:
            ComputeResult with execution status and metadata
        """
        pass

    @abstractmethod
    def can_handle(self, execution_plan: QueryExecutionPlan) -> bool:
        """
        Check if this engine can handle the given execution plan.

        Args:
            execution_plan: Execution plan to check

        Returns:
            True if this engine can handle the plan
        """
        pass

    @abstractmethod
    def estimate_cost(self, execution_plan: QueryExecutionPlan) -> float:
        """
        Estimate cost of executing with this engine.

        Lower cost = better choice.

        Args:
            execution_plan: Execution plan to estimate

        Returns:
            Cost estimate (arbitrary units, relative to other engines)
        """
        pass

    @abstractmethod
    def get_engine_name(self) -> str:
        """Get name of this compute engine."""
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Test if engine is available and working.

        Returns:
            (success, error_message)
        """
        pass

    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._initialized

    def __enter__(self):
        """Context manager entry."""
        if not self._initialized:
            self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
        return False


class PushdownEngine(BaseComputeEngine):
    """
    Special compute engine for pushdown execution.

    This doesn't actually compute anything - it delegates to the
    source adapter directly.
    """

    def __init__(self, adapter_factory):
        """
        Initialize pushdown engine.

        Args:
            adapter_factory: Factory to get adapters by profile name
        """
        super().__init__(config={})
        self.adapter_factory = adapter_factory

    def initialize(self) -> None:
        """Initialize (no-op for pushdown)."""
        self._initialized = True

    def shutdown(self) -> None:
        """Shutdown (no-op for pushdown)."""
        self._initialized = False

    def execute_query(
        self,
        sql: str,
        execution_plan: QueryExecutionPlan,
    ) -> ComputeResult:
        """
        Execute query via pushdown to source adapter.

        Args:
            sql: SQL query to execute
            execution_plan: Execution plan

        Returns:
            ComputeResult
        """
        if not execution_plan.pushdown_target:
            return ComputeResult(
                success=False,
                error="Pushdown target not specified in execution plan",
            )

        try:
            start_time = datetime.now()

            # Get adapter for pushdown target
            adapter = self.adapter_factory.get_adapter(execution_plan.pushdown_target)

            # Execute on adapter
            result = adapter.execute(sql, fetch=False)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return ComputeResult(
                success=True,
                rows_affected=getattr(result, "rows_affected", 0),
                execution_time_ms=execution_time,
                strategy_used=ExecutionStrategy.PUSHDOWN,
                compute_engine_used=execution_plan.pushdown_target,
            )

        except Exception as e:
            return ComputeResult(
                success=False,
                error=str(e),
                strategy_used=ExecutionStrategy.PUSHDOWN,
            )

    def can_handle(self, execution_plan: QueryExecutionPlan) -> bool:
        """Check if pushdown is possible."""
        return execution_plan.is_pushdown_possible()

    def estimate_cost(self, execution_plan: QueryExecutionPlan) -> float:
        """Pushdown has lowest cost (no data movement)."""
        if execution_plan.is_pushdown_possible():
            return 1.0  # Lowest cost
        else:
            return float("inf")  # Impossible

    def get_engine_name(self) -> str:
        """Get engine name."""
        return "pushdown"

    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test pushdown (always available)."""
        return (True, None)
