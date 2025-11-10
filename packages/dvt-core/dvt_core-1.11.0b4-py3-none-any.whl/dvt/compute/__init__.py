"""
DVT Compute Layer

This package provides the compute engine abstraction for processing
heterogeneous data sources.
"""

from dvt.compute.base import (
    BaseComputeEngine,
    ComputeResult,
    QueryExecutionPlan,
    SourceInfo,
)
from dvt.compute.query_analyzer import QueryAnalyzer, analyze_query_sources
from dvt.compute.router import ExecutionRouter, ExecutionStrategy

__all__ = [
    "BaseComputeEngine",
    "ComputeResult",
    "QueryExecutionPlan",
    "SourceInfo",
    "ExecutionRouter",
    "ExecutionStrategy",
    "QueryAnalyzer",
    "analyze_query_sources",
]
