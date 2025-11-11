"""
UnifiedAdapter for DVT - Routes between single-profile and multi-profile queries.

This adapter acts as a meta-adapter that:
1. Detects if a query involves multiple profiles (cross-database)
2. Routes single-profile queries to the appropriate dbt adapter (PUSHDOWN)
3. Routes multi-profile queries to the compute layer (COMPUTE_LAYER)
"""

from typing import Any, Optional

from dbt.adapters.base.impl import BaseAdapter
from dbt.adapters.protocol import AdapterProtocol

from dvt.adapters.multi_adapter_manager import MultiAdapterManager
from dvt.compute.query_analyzer import QueryAnalyzer
from dvt.compute.router import ExecutionRouter

from dbt_common.events.functions import fire_event
from dbt_common.events.types import Note


class UnifiedAdapter:
    """
    Unified adapter that routes queries to appropriate execution strategy.

    This is the main entry point for DVT query execution. It analyzes queries
    and decides whether to:
    - PUSHDOWN: Execute directly on source database (single profile)
    - COMPUTE_LAYER: Execute via DuckDB or Spark (multi-profile)

    Architecture:
        Query → UnifiedAdapter → QueryAnalyzer → ExecutionRouter → Result
                       ↓                               ↓
                Single-profile?              Multi-profile?
                       ↓                               ↓
                 dbt adapter                    Compute Engine
    """

    def __init__(
        self,
        multi_adapter_manager: MultiAdapterManager,
        execution_router: ExecutionRouter,
        query_analyzer: QueryAnalyzer,
        default_profile: str,
    ):
        """
        Initialize UnifiedAdapter.

        Args:
            multi_adapter_manager: Manager for multiple dbt adapters
            execution_router: Router for choosing execution strategy
            query_analyzer: Analyzer for detecting query patterns
            default_profile: Default profile name (from profiles.yml target)
        """
        self.multi_adapter_manager = multi_adapter_manager
        self.execution_router = execution_router
        self.query_analyzer = query_analyzer
        self.default_profile = default_profile

    def execute(
        self,
        sql: str,
        fetch: bool = False,
        auto_begin: bool = True,
        model_config: Optional[dict] = None,
    ) -> Any:
        """
        Execute SQL query using appropriate strategy.

        This is the main execution method that:
        1. Analyzes the query to determine profiles involved
        2. Checks model config for overrides (target, compute)
        3. Routes to appropriate execution strategy
        4. Returns results

        Args:
            sql: SQL query to execute
            fetch: Whether to fetch and return results
            auto_begin: Whether to auto-begin transaction
            model_config: Optional model configuration with target/compute overrides

        Returns:
            Query results (format depends on execution strategy)

        Example:
            >>> adapter = UnifiedAdapter(manager, router, analyzer, "postgres_prod")
            >>> # Single-profile query - pushed down to PostgreSQL
            >>> result = adapter.execute("SELECT * FROM customers", fetch=True)
            >>> # Multi-profile query - executed in compute layer
            >>> result = adapter.execute('''
            ...     SELECT c.*, o.order_count
            ...     FROM postgres_prod.customers c
            ...     JOIN mysql_legacy.orders o ON c.id = o.customer_id
            ... ''', fetch=True)
        """
        model_config = model_config or {}

        # Analyze query to determine profiles involved
        analysis = self.query_analyzer.analyze(sql)

        # Check for model-level overrides
        target_override = model_config.get("target")
        compute_override = model_config.get("compute")

        fire_event(
            Note(
                msg=f"Executing query: {len(analysis.profiles_referenced)} profiles, "
                f"target_override={target_override}, compute_override={compute_override}"
            )
        )

        # Single-profile query - use PUSHDOWN strategy
        if len(analysis.profiles_referenced) <= 1:
            profile = (
                target_override
                or (analysis.profiles_referenced[0] if analysis.profiles_referenced else None)
                or self.default_profile
            )

            fire_event(Note(msg=f"PUSHDOWN strategy: Executing on profile '{profile}'"))

            adapter = self.multi_adapter_manager.get_or_create_adapter(profile)
            return adapter.execute(sql, fetch=fetch, auto_begin=auto_begin)

        # Multi-profile query - use COMPUTE_LAYER strategy
        else:
            fire_event(
                Note(
                    msg=f"COMPUTE_LAYER strategy: {len(analysis.profiles_referenced)} profiles "
                    f"({', '.join(analysis.profiles_referenced)})"
                )
            )

            # Build execution plan
            execution_plan = self.query_analyzer.build_execution_plan(sql, analysis)

            # Store SQL in plan for execution
            execution_plan.sql = sql

            # Apply compute override if specified
            if compute_override:
                execution_plan.preferred_engine = compute_override

            # Execute via compute layer
            result = self.execution_router.execute(execution_plan)

            if fetch:
                return result.data if hasattr(result, 'data') else result
            else:
                return result

    def get_adapter_for_profile(self, profile_name: str) -> AdapterProtocol:
        """
        Get dbt adapter for a specific profile.

        This allows accessing the underlying dbt adapter for a profile,
        useful for DDL operations, connection testing, etc.

        Args:
            profile_name: Profile name

        Returns:
            dbt adapter instance

        Example:
            >>> adapter = unified_adapter.get_adapter_for_profile("postgres_prod")
            >>> adapter.execute("CREATE TABLE test (id INT)", fetch=False)
        """
        return self.multi_adapter_manager.get_or_create_adapter(profile_name)

    def get_default_adapter(self) -> AdapterProtocol:
        """
        Get dbt adapter for the default profile.

        Returns:
            dbt adapter for default profile
        """
        return self.multi_adapter_manager.get_or_create_adapter(self.default_profile)

    def test_connection(self, profile_name: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Test connection for a profile.

        Args:
            profile_name: Profile to test (default: default profile)

        Returns:
            (success, error_message) tuple
        """
        profile = profile_name or self.default_profile

        try:
            adapter = self.multi_adapter_manager.get_or_create_adapter(profile)
            # Try a simple query
            adapter.execute("SELECT 1", fetch=True)
            return (True, None)
        except Exception as e:
            return (False, str(e))

    def cleanup(self):
        """Clean up all adapters and close connections."""
        self.multi_adapter_manager.cleanup()
        self.execution_router.cleanup()


def create_unified_adapter(
    profiles: dict,
    default_profile: str,
    compute_config: Optional[dict] = None,
) -> UnifiedAdapter:
    """
    Factory function to create a fully configured UnifiedAdapter.

    This is the recommended way to create a UnifiedAdapter instance.

    Args:
        profiles: Dictionary of profile configurations
        default_profile: Default profile name
        compute_config: Optional compute configuration (DuckDB/Spark settings)

    Returns:
        Configured UnifiedAdapter instance

    Example:
        >>> profiles = {
        ...     'postgres_prod': {...},
        ...     'mysql_legacy': {...}
        ... }
        >>> adapter = create_unified_adapter(
        ...     profiles,
        ...     default_profile='postgres_prod',
        ...     compute_config={'default_engine': 'duckdb'}
        ... )
    """
    from dvt.compute.router import ExecutionRouter
    from dvt.compute.query_analyzer import QueryAnalyzer

    # Create multi-adapter manager
    manager = MultiAdapterManager(profiles)

    # Create query analyzer
    analyzer = QueryAnalyzer()

    # Create execution router
    router = ExecutionRouter(
        multi_adapter_manager=manager,
        compute_config=compute_config or {},
    )

    # Create unified adapter
    return UnifiedAdapter(
        multi_adapter_manager=manager,
        execution_router=router,
        query_analyzer=analyzer,
        default_profile=default_profile,
    )
