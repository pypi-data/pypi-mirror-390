"""
Query analyzer for DVT execution routing.

This module analyzes SQL queries to extract source references and build
execution plans for the ExecutionRouter.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from dvt.compute.base import QueryExecutionPlan, SourceInfo, ExecutionStrategy
from dvt.contracts.graph.manifest import Manifest

from dbt_common.events.functions import fire_event
from dbt_common.events.types import Note
from dbt_common.exceptions import DbtRuntimeError


@dataclass
class QueryAnalysis:
    """
    Simple analysis result for UnifiedAdapter.

    This provides a lightweight analysis of which profiles are referenced
    in a query, used by UnifiedAdapter for routing decisions.
    """

    profiles_referenced: List[str]
    sources: List[SourceInfo]
    is_multi_profile: bool

    def __post_init__(self):
        """Calculate derived properties."""
        self.is_multi_profile = len(set(self.profiles_referenced)) > 1


class QueryAnalyzer:
    """
    Analyzes SQL queries to extract source dependencies.

    This analyzer:
    - Parses Jinja source() calls to find source references
    - Looks up source metadata from manifest
    - Estimates data sizes for execution planning
    - Builds SourceInfo objects for ExecutionRouter
    """

    def __init__(self, manifest: Optional[Manifest] = None):
        """
        Initialize QueryAnalyzer.

        Args:
            manifest: Optional manifest with source definitions
        """
        self.manifest = manifest

    def analyze(self, sql: str) -> QueryAnalysis:
        """
        Simple analysis for UnifiedAdapter routing.

        This method provides a lightweight analysis suitable for the UnifiedAdapter's
        routing logic. It extracts profile references without full manifest resolution.

        Args:
            sql: SQL query to analyze

        Returns:
            QueryAnalysis with profiles_referenced list

        Example:
            >>> analyzer = QueryAnalyzer()
            >>> analysis = analyzer.analyze('''
            ...     SELECT * FROM postgres_prod.customers c
            ...     JOIN mysql_legacy.orders o ON c.id = o.customer_id
            ... ''')
            >>> analysis.profiles_referenced
            ['postgres_prod', 'mysql_legacy']
            >>> analysis.is_multi_profile
            True
        """
        # Extract profile references from SQL
        # Look for patterns like: profile_name.table_name or profile_name.schema.table
        profiles = self._extract_profile_references(sql)

        # If manifest is available, also analyze source() calls
        sources = []
        if self.manifest:
            source_infos = self.analyze_model_sql(sql)
            sources.extend(source_infos)
            # Add profiles from sources
            for source_info in source_infos:
                profiles.add(source_info.profile_name)

        return QueryAnalysis(
            profiles_referenced=sorted(list(profiles)),
            sources=sources,
            is_multi_profile=len(profiles) > 1,
        )

    def build_execution_plan(self, sql: str, analysis: QueryAnalysis) -> QueryExecutionPlan:
        """
        Build execution plan from query analysis.

        Args:
            sql: SQL query
            analysis: QueryAnalysis from analyze()

        Returns:
            QueryExecutionPlan ready for ExecutionRouter

        Example:
            >>> analyzer = QueryAnalyzer()
            >>> analysis = analyzer.analyze(sql)
            >>> plan = analyzer.build_execution_plan(sql, analysis)
            >>> plan.is_homogeneous
            False
        """
        # Determine if homogeneous (single profile)
        is_homogeneous = len(analysis.profiles_referenced) <= 1

        # Calculate data size estimate
        total_size_mb = sum(s.estimated_size_mb or 0 for s in analysis.sources)
        total_rows = sum(s.estimated_rows or 0 for s in analysis.sources)

        # Create execution plan
        plan = QueryExecutionPlan(
            strategy=ExecutionStrategy.AUTO,
            sources=analysis.sources,
            is_homogeneous=is_homogeneous,
            estimated_data_size_mb=total_size_mb if total_size_mb > 0 else 0.0,
            estimated_rows=total_rows if total_rows > 0 else 0,
        )

        # Set pushdown target if homogeneous
        if is_homogeneous and analysis.profiles_referenced:
            plan.pushdown_target = analysis.profiles_referenced[0]

        return plan

    def _extract_profile_references(self, sql: str) -> Set[str]:
        """
        Extract profile references from SQL.

        Looks for patterns like:
        - profile_name.table_name
        - profile_name.schema.table_name

        Args:
            sql: SQL query

        Returns:
            Set of profile names
        """
        profiles: Set[str] = set()

        # Pattern to match qualified table names: identifier.identifier or identifier.identifier.identifier
        # This is a simple heuristic - matches [word].[word] patterns
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?\b'

        matches = re.finditer(pattern, sql)
        for match in matches:
            # First identifier is potentially a profile name
            potential_profile = match.group(1)
            # Filter out common SQL keywords
            if potential_profile.upper() not in {
                'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
                'OUTER', 'CROSS', 'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS'
            }:
                profiles.add(potential_profile)

        return profiles

    def analyze_model_sql(self, sql: str, model_node: Optional[Any] = None) -> List[SourceInfo]:
        """
        Analyze SQL to extract source references.

        Args:
            sql: SQL query (may contain Jinja)
            model_node: Optional model node for context

        Returns:
            List of SourceInfo objects
        """
        # Extract source references from SQL
        source_refs = self._extract_source_references(sql)

        # Build SourceInfo for each reference
        source_infos: List[SourceInfo] = []
        for source_name, table_name in source_refs:
            source_info = self._build_source_info(source_name, table_name)
            if source_info:
                source_infos.append(source_info)

        return source_infos

    def _extract_source_references(self, sql: str) -> Set[Tuple[str, str]]:
        """
        Extract source() references from SQL.

        Looks for patterns like:
        - {{ source('schema_name', 'table_name') }}
        - {{source("schema_name", "table_name")}}
        - {{ source( 'schema_name' , 'table_name' ) }}

        Args:
            sql: SQL query with Jinja

        Returns:
            Set of (source_name, table_name) tuples
        """
        sources: Set[Tuple[str, str]] = set()

        # Pattern to match source() calls
        # Handles single or double quotes, optional whitespace
        pattern = r"{{\s*source\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*}}"

        matches = re.finditer(pattern, sql, re.IGNORECASE)
        for match in matches:
            source_name = match.group(1)
            table_name = match.group(2)
            sources.add((source_name, table_name))

        return sources

    def _build_source_info(self, source_name: str, table_name: str) -> Optional[SourceInfo]:
        """
        Build SourceInfo from source reference.

        Args:
            source_name: Source schema name
            table_name: Table name

        Returns:
            SourceInfo or None if source not found
        """
        # Resolve source in manifest
        source = self.manifest.resolve_source(
            source_name=source_name,
            table_name=table_name,
            current_project=None,
            node_package=None,
        )

        if not source or not hasattr(source, "unique_id"):
            fire_event(
                Note(msg=f"Warning: Source '{source_name}.{table_name}' not found in manifest")
            )
            return None

        # Extract profile name (DVT-specific)
        profile_name = getattr(source, "profile", None)
        if not profile_name:
            # No profile specified - use default target profile
            fire_event(
                Note(
                    msg=f"Source '{source_name}.{table_name}' has no profile, "
                    "will use default target"
                )
            )
            profile_name = "default"

        # Determine adapter type
        # TODO: Look up adapter type from profile
        adapter_type = "unknown"

        # Estimate data size
        # TODO: Implement actual size estimation
        # For now, use placeholder values
        estimated_size_mb = None
        estimated_rows = None

        # Build SourceInfo
        source_info = SourceInfo(
            source_name=f"{source_name}.{table_name}",
            profile_name=profile_name,
            adapter_type=adapter_type,
            database=getattr(source, "database", None),
            schema=getattr(source, "schema", source_name),
            identifier=getattr(source, "identifier", table_name),
            estimated_size_mb=estimated_size_mb,
            estimated_rows=estimated_rows,
        )

        return source_info

    def build_execution_plan_for_model(
        self, sql: str, model_node: Optional[Any] = None
    ) -> QueryExecutionPlan:
        """
        Build complete execution plan for a model.

        This is a convenience method that:
        1. Analyzes SQL to extract sources
        2. Builds SourceInfo objects
        3. Creates QueryExecutionPlan

        Args:
            sql: SQL query
            model_node: Optional model node

        Returns:
            QueryExecutionPlan ready for strategy selection
        """
        # Analyze sources
        sources = self.analyze_model_sql(sql, model_node)

        # Calculate metrics
        unique_profiles = {s.profile_name for s in sources}
        unique_adapters = {s.adapter_type for s in sources}
        is_homogeneous = len(unique_profiles) <= 1 and len(unique_adapters) <= 1

        # Estimate data size
        total_size_mb = sum(s.estimated_size_mb or 0 for s in sources)
        total_rows = sum(s.estimated_rows or 0 for s in sources)

        # Create execution plan
        from dvt.compute.base import ExecutionStrategy

        plan = QueryExecutionPlan(
            strategy=ExecutionStrategy.AUTO,
            sources=sources,
            is_homogeneous=is_homogeneous,
            estimated_data_size_mb=total_size_mb if total_size_mb > 0 else None,
            estimated_rows=total_rows if total_rows > 0 else None,
        )

        # Set pushdown target if homogeneous
        if is_homogeneous and sources:
            plan.pushdown_target = sources[0].profile_name

        return plan


def analyze_query_sources(sql: str, manifest: Manifest) -> List[SourceInfo]:
    """
    Convenience function to analyze query sources.

    Args:
        sql: SQL query
        manifest: Manifest

    Returns:
        List of SourceInfo objects
    """
    analyzer = QueryAnalyzer(manifest)
    return analyzer.analyze_model_sql(sql)
