"""
Execution router for DVT.

This module analyzes queries and routes them to the optimal execution engine
(pushdown vs compute layer).
"""

from typing import Dict, List, Optional

from dvt.compute.base import (
    BaseComputeEngine,
    ComputeResult,
    ExecutionStrategy,
    QueryExecutionPlan,
    SourceInfo,
)
from dvt.config.compute_config import AutoSelectConfig, ComputeConfig
from dvt.events import fire_event
from dvt.events.types import Note

from dbt.adapters.exceptions import DbtRuntimeError


class ExecutionRouter:
    """
    Routes queries to optimal execution engine.

    Analyzes query execution plans and selects:
    - Pushdown (execute on source database)
    - DuckDB (lightweight compute layer)
    - Spark (heavy-duty compute layer)
    """

    def __init__(
        self,
        compute_config: ComputeConfig,
        available_engines: Dict[str, BaseComputeEngine],
    ):
        """
        Initialize execution router.

        Args:
            compute_config: Compute configuration
            available_engines: Dictionary of available engines by name
        """
        self.compute_config = compute_config
        self.available_engines = available_engines
        self.auto_select_config = compute_config.auto_select

    def analyze_query(
        self,
        sql: str,
        sources: List[SourceInfo],
    ) -> QueryExecutionPlan:
        """
        Analyze query and create execution plan.

        Args:
            sql: SQL query
            sources: List of source information

        Returns:
            QueryExecutionPlan
        """
        # Calculate metrics
        unique_adapters = {s.adapter_type for s in sources}
        unique_profiles = {s.profile_name for s in sources}
        is_homogeneous = len(unique_adapters) == 1 and len(unique_profiles) == 1

        # Estimate data size
        total_size_mb = sum(s.estimated_size_mb or 0 for s in sources)
        total_rows = sum(s.estimated_rows or 0 for s in sources)

        # Create initial plan
        plan = QueryExecutionPlan(
            strategy=ExecutionStrategy.AUTO,
            sources=sources,
            is_homogeneous=is_homogeneous,
            estimated_data_size_mb=total_size_mb,
            estimated_rows=total_rows,
        )

        # If homogeneous, can potentially pushdown
        if is_homogeneous and sources:
            plan.pushdown_target = sources[0].profile_name

        return plan

    def select_strategy(
        self,
        execution_plan: QueryExecutionPlan,
        requested_engine: Optional[str] = None,
        model_node: Optional[Any] = None,
    ) -> QueryExecutionPlan:
        """
        Select execution strategy for query.

        Args:
            execution_plan: Query execution plan
            requested_engine: User-requested engine (overrides auto-selection)
            model_node: Optional model node with DVT config overrides

        Returns:
            Updated execution plan with selected strategy
        """
        # Check for model-level config overrides
        model_config = self._extract_model_config(model_node) if model_node else {}

        # Model config takes precedence over requested_engine parameter
        if model_config.get("compute_engine"):
            requested_engine = model_config["compute_engine"]
        elif model_config.get("pushdown_enabled") is True:
            requested_engine = "pushdown"
        elif model_config.get("pushdown_enabled") is False:
            # Explicitly disable pushdown, force compute layer
            if not requested_engine:
                requested_engine = self.compute_config.default_engine

        # If user requested specific engine, honor it
        if requested_engine:
            if requested_engine == "pushdown":
                if execution_plan.is_pushdown_possible():
                    execution_plan.strategy = ExecutionStrategy.PUSHDOWN
                    execution_plan.compute_engine = None
                    execution_plan.reason = "User requested pushdown"
                else:
                    raise DbtRuntimeError(
                        "Pushdown requested but not possible: "
                        f"Query references {len(execution_plan.get_unique_profiles())} profiles"
                    )
            else:
                execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                execution_plan.compute_engine = requested_engine
                execution_plan.reason = f"User requested {requested_engine}"
            return execution_plan

        # Use auto-selection rules
        if self.auto_select_config.enabled:
            return self._apply_auto_select_rules(execution_plan)
        else:
            # Auto-selection disabled, use default engine
            return self._use_default_engine(execution_plan)

    def _apply_auto_select_rules(self, execution_plan: QueryExecutionPlan) -> QueryExecutionPlan:
        """
        Apply auto-selection rules to choose strategy.

        Args:
            execution_plan: Execution plan

        Returns:
            Updated execution plan
        """
        # Rules are already sorted by priority
        for rule in self.auto_select_config.rules:
            if self._evaluate_rule_condition(rule.condition, execution_plan):
                # Rule matches - apply action
                if rule.action == "use_pushdown":
                    if execution_plan.is_pushdown_possible():
                        execution_plan.strategy = ExecutionStrategy.PUSHDOWN
                        execution_plan.compute_engine = None
                        execution_plan.reason = (
                            f"Auto-select rule '{rule.name}': {rule.description}"
                        )
                        fire_event(Note(msg=f"Selected PUSHDOWN via rule '{rule.name}'"))
                        return execution_plan

                elif rule.action == "use_duckdb":
                    execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                    execution_plan.compute_engine = "duckdb"
                    execution_plan.reason = f"Auto-select rule '{rule.name}': {rule.description}"
                    fire_event(Note(msg=f"Selected DUCKDB via rule '{rule.name}'"))
                    return execution_plan

                elif rule.action == "use_spark_local":
                    execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                    execution_plan.compute_engine = "spark_local"
                    execution_plan.reason = f"Auto-select rule '{rule.name}': {rule.description}"
                    fire_event(Note(msg=f"Selected SPARK_LOCAL via rule '{rule.name}'"))
                    return execution_plan

                elif rule.action == "use_spark_cluster":
                    execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                    execution_plan.compute_engine = "spark_cluster"
                    execution_plan.reason = f"Auto-select rule '{rule.name}': {rule.description}"
                    fire_event(Note(msg=f"Selected SPARK_CLUSTER via rule '{rule.name}'"))
                    return execution_plan

        # No rule matched - use default
        return self._use_default_engine(execution_plan)

    def _evaluate_rule_condition(self, condition, execution_plan: QueryExecutionPlan) -> bool:
        """
        Evaluate a rule condition.

        Args:
            condition: Condition to evaluate (string or dict)
            execution_plan: Execution plan

        Returns:
            True if condition is met
        """
        # Simple string conditions
        if isinstance(condition, str):
            if condition == "always":
                return True
            elif condition == "model_has_compute_engine_config":
                # TODO: Check if model has explicit compute_engine config
                return False
            else:
                return False

        # Dictionary conditions
        if isinstance(condition, dict):
            condition_type = condition.get("type", "and")

            # Handle 'and' conditions
            if condition_type == "and":
                conditions = condition.get("conditions", [])
                return all(self._evaluate_single_condition(c, execution_plan) for c in conditions)

            # Handle 'or' conditions
            elif condition_type == "or":
                conditions = condition.get("conditions", [])
                return any(self._evaluate_single_condition(c, execution_plan) for c in conditions)

            # Single condition dict
            else:
                return self._evaluate_single_condition(condition, execution_plan)

        return False

    def _evaluate_single_condition(
        self, condition: Dict, execution_plan: QueryExecutionPlan
    ) -> bool:
        """Evaluate a single condition."""
        # Homogeneous sources
        if "homogeneous_sources" in condition:
            expected = condition["homogeneous_sources"]
            return execution_plan.is_homogeneous == expected

        # Same as target
        if "same_as_target" in condition:
            # TODO: Check if sources match target
            # For now, assume true if homogeneous
            return execution_plan.is_homogeneous

        # Data size estimate
        if "data_size_estimate" in condition:
            size_condition = condition["data_size_estimate"]
            if isinstance(size_condition, str):
                # Parse conditions like "< 1GB", "> 10GB"
                return self._parse_size_condition(
                    size_condition, execution_plan.estimated_data_size_mb
                )

        # Row count estimate
        if "row_count_estimate" in condition:
            row_condition = condition["row_count_estimate"]
            if isinstance(row_condition, str):
                # Parse conditions like "> 100000000"
                return self._parse_row_condition(row_condition, execution_plan.estimated_rows)

        # Heterogeneous sources
        if "heterogeneous_sources" in condition:
            expected = condition["heterogeneous_sources"]
            return (not execution_plan.is_homogeneous) == expected

        # Adapter count
        if "adapter_count" in condition:
            count_condition = condition["adapter_count"]
            actual_count = len(execution_plan.get_unique_adapters())
            if isinstance(count_condition, str):
                return self._parse_comparison(count_condition, actual_count)

        return False

    def _parse_size_condition(self, condition: str, size_mb: float) -> bool:
        """Parse size condition like '< 1GB' or '> 10GB'."""
        condition = condition.strip()

        # Extract operator and value
        if condition.startswith(">="):
            op = ">="
            value_str = condition[2:].strip()
        elif condition.startswith("<="):
            op = "<="
            value_str = condition[2:].strip()
        elif condition.startswith(">"):
            op = ">"
            value_str = condition[1:].strip()
        elif condition.startswith("<"):
            op = "<"
            value_str = condition[1:].strip()
        else:
            return False

        # Parse value (handle GB, MB units)
        value_mb = self._parse_size_value(value_str)

        # Compare
        if op == ">":
            return size_mb > value_mb
        elif op == ">=":
            return size_mb >= value_mb
        elif op == "<":
            return size_mb < value_mb
        elif op == "<=":
            return size_mb <= value_mb

        return False

    def _parse_size_value(self, value_str: str) -> float:
        """Parse size value like '1GB' or '100MB' to MB."""
        value_str = value_str.strip().upper()

        if value_str.endswith("GB"):
            return float(value_str[:-2]) * 1024
        elif value_str.endswith("MB"):
            return float(value_str[:-2])
        elif value_str.endswith("KB"):
            return float(value_str[:-2]) / 1024
        else:
            # Assume MB
            return float(value_str)

    def _parse_row_condition(self, condition: str, row_count: int) -> bool:
        """Parse row condition like '> 100000000'."""
        condition = condition.strip()

        # Extract operator and value
        if condition.startswith(">="):
            op = ">="
            value = int(condition[2:].strip())
        elif condition.startswith("<="):
            op = "<="
            value = int(condition[2:].strip())
        elif condition.startswith(">"):
            op = ">"
            value = int(condition[1:].strip())
        elif condition.startswith("<"):
            op = "<"
            value = int(condition[1:].strip())
        else:
            return False

        # Compare
        if op == ">":
            return row_count > value
        elif op == ">=":
            return row_count >= value
        elif op == "<":
            return row_count < value
        elif op == "<=":
            return row_count <= value

        return False

    def _parse_comparison(self, condition: str, value: int) -> bool:
        """Parse comparison like '> 2'."""
        condition = condition.strip()

        if condition.startswith(">="):
            return value >= int(condition[2:].strip())
        elif condition.startswith("<="):
            return value <= int(condition[2:].strip())
        elif condition.startswith(">"):
            return value > int(condition[1:].strip())
        elif condition.startswith("<"):
            return value < int(condition[1:].strip())
        elif condition.startswith("=="):
            return value == int(condition[2:].strip())

        return False

    def _use_default_engine(self, execution_plan: QueryExecutionPlan) -> QueryExecutionPlan:
        """Use default engine from configuration."""
        default_engine = self.compute_config.default_engine

        if default_engine == "auto":
            # Use heuristics
            if execution_plan.is_pushdown_possible():
                execution_plan.strategy = ExecutionStrategy.PUSHDOWN
                execution_plan.compute_engine = None
                execution_plan.reason = "Default: Pushdown for homogeneous sources"
            elif execution_plan.estimated_data_size_mb < 1024:  # < 1GB
                execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                execution_plan.compute_engine = "duckdb"
                execution_plan.reason = "Default: DuckDB for small data"
            else:
                execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                execution_plan.compute_engine = "spark_local"
                execution_plan.reason = "Default: Spark for large data"
        else:
            # Use specified default
            if default_engine == "pushdown":
                if execution_plan.is_pushdown_possible():
                    execution_plan.strategy = ExecutionStrategy.PUSHDOWN
                    execution_plan.compute_engine = None
                else:
                    # Fall back to DuckDB
                    execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                    execution_plan.compute_engine = "duckdb"
                    execution_plan.reason = "Pushdown not possible, using DuckDB"
            else:
                execution_plan.strategy = ExecutionStrategy.COMPUTE_LAYER
                execution_plan.compute_engine = default_engine

            execution_plan.reason = f"Default engine: {default_engine}"

        return execution_plan

    def execute(
        self,
        sql: str,
        execution_plan: QueryExecutionPlan,
    ) -> ComputeResult:
        """
        Execute query using selected strategy.

        Args:
            sql: SQL query
            execution_plan: Execution plan with selected strategy

        Returns:
            ComputeResult
        """
        # Get engine for execution
        if execution_plan.strategy == ExecutionStrategy.PUSHDOWN:
            engine_name = "pushdown"
        else:
            engine_name = execution_plan.compute_engine or "duckdb"

        # Get engine instance
        engine = self.available_engines.get(engine_name)
        if not engine:
            return ComputeResult(
                success=False,
                error=f"Compute engine '{engine_name}' not available",
            )

        # Check if engine can handle this plan
        if not engine.can_handle(execution_plan):
            return ComputeResult(
                success=False,
                error=f"Engine '{engine_name}' cannot handle this execution plan",
            )

        # Execute
        fire_event(Note(msg=f"Executing via {engine_name}: {execution_plan.reason}"))
        return engine.execute_query(sql, execution_plan)

    def _extract_model_config(self, model_node: Any) -> Dict[str, Any]:
        """
        Extract DVT-specific config from model node.

        Args:
            model_node: Model node (ModelNode, etc.)

        Returns:
            Dictionary with DVT config fields
        """
        config_dict = {}

        if hasattr(model_node, "config"):
            model_config = model_node.config

            # Extract compute_engine
            if hasattr(model_config, "compute_engine") and model_config.compute_engine:
                config_dict["compute_engine"] = model_config.compute_engine

            # Extract pushdown_enabled
            if (
                hasattr(model_config, "pushdown_enabled")
                and model_config.pushdown_enabled is not None
            ):
                config_dict["pushdown_enabled"] = model_config.pushdown_enabled

            # Extract target_profile
            if hasattr(model_config, "target_profile") and model_config.target_profile:
                config_dict["target_profile"] = model_config.target_profile

        return config_dict
