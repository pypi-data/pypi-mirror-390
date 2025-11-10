"""
DVT Compute Engines

This package contains implementations of compute engines (DuckDB, Spark).
"""

from dvt.compute.engines.duckdb_engine import DuckDBEngine
from dvt.compute.engines.spark_engine import SparkEngine

__all__ = [
    "DuckDBEngine",
    "SparkEngine",
]
