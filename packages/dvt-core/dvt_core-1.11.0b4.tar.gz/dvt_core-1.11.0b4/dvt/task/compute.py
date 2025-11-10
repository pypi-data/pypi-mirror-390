"""
DVT Compute Tasks

This module implements compute layer management commands:
- show: Show compute configuration
- engines: List available compute engines
- test: Test compute engines
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from dvt.cli.flags import Flags
from dvt.config.compute_config import ComputeConfig, load_compute_config
from dvt.events.types import Note
from dvt.task.base import BaseTask

from dbt_common.events.functions import fire_event
from dbt_common.ui import green, red, yellow


class ComputeShowTask(BaseTask):
    """Task to show compute layer configuration."""

    def __init__(self, args: Flags) -> None:
        super().__init__(args)
        self.project_dir = args.PROJECT_DIR

    def run(self) -> bool:
        """Show compute layer configuration."""
        fire_event(Note(msg=""))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg="DVT Compute Configuration"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Project directory: {self.project_dir}"))
        fire_event(Note(msg=""))

        # Load compute config
        try:
            compute_config = load_compute_config(Path(self.project_dir))
        except Exception as e:
            fire_event(Note(msg=red(f"Error loading compute config: {e}")))
            fire_event(Note(msg=""))
            fire_event(Note(msg="Using default configuration"))
            compute_config = ComputeConfig()

        # Show configuration
        fire_event(Note(msg="General Settings:"))
        fire_event(Note(msg=f"  Default engine: {green(compute_config.default_engine)}"))
        fire_event(Note(msg=f"  Data threshold: {compute_config.data_threshold_mb} MB"))
        fire_event(Note(msg=""))

        # Show DuckDB config
        fire_event(Note(msg="DuckDB Configuration:"))
        fire_event(Note(msg=f"  Enabled: {green('Yes') if compute_config.duckdb.enabled else red('No')}"))
        fire_event(Note(msg=f"  Memory limit: {compute_config.duckdb.memory_limit}"))
        fire_event(Note(msg=f"  Threads: {compute_config.duckdb.threads}"))
        if compute_config.duckdb.extensions:
            fire_event(Note(msg=f"  Extensions: {', '.join(compute_config.duckdb.extensions)}"))
        fire_event(Note(msg=""))

        # Show Spark config
        fire_event(Note(msg="Spark Configuration:"))
        fire_event(Note(msg=f"  Local mode enabled: {green('Yes') if compute_config.spark_local.enabled else red('No')}"))
        fire_event(Note(msg=f"  Cluster mode enabled: {green('Yes') if compute_config.spark_cluster.enabled else red('No')}"))
        fire_event(Note(msg=""))

        if compute_config.spark_local.enabled:
            fire_event(Note(msg="  Spark Local Settings:"))
            fire_event(Note(msg=f"    Master: {compute_config.spark_local.master}"))
            fire_event(Note(msg=f"    Driver memory: {compute_config.spark_local.driver_memory}"))
            fire_event(Note(msg=f"    Executor memory: {compute_config.spark_local.executor_memory}"))
            fire_event(Note(msg=""))

        if compute_config.spark_cluster.enabled:
            fire_event(Note(msg="  Spark Cluster Settings:"))
            fire_event(Note(msg=f"    Master: {compute_config.spark_cluster.master or yellow('Not configured')}"))
            fire_event(Note(msg=f"    Deploy mode: {compute_config.spark_cluster.deploy_mode}"))
            fire_event(Note(msg=""))

        # Show auto-select config
        fire_event(Note(msg="Auto-Select Configuration:"))
        fire_event(Note(msg=f"  Enabled: {green('Yes') if compute_config.auto_select.enabled else red('No')}"))
        if compute_config.auto_select.enabled and compute_config.auto_select.rules:
            fire_event(Note(msg=f"  Rules: {len(compute_config.auto_select.rules)} configured"))
            fire_event(Note(msg=""))
            for i, rule in enumerate(compute_config.auto_select.rules, 1):
                fire_event(Note(msg=f"  Rule {i}: {rule.name}"))
                fire_event(Note(msg=f"    Priority: {rule.priority}"))
                fire_event(Note(msg=f"    Action: {rule.action}"))
                fire_event(Note(msg=f"    Description: {rule.description}"))
                fire_event(Note(msg=""))
        else:
            fire_event(Note(msg="  No auto-select rules configured"))
            fire_event(Note(msg=""))

        fire_event(Note(msg=f"Use 'dvt compute engines' to see available engines"))
        fire_event(Note(msg=f"Use 'dvt compute test' to test compute engines"))
        fire_event(Note(msg=""))

        return True

    def interpret_results(self, results) -> bool:
        return results


class ComputeEnginesTask(BaseTask):
    """Task to list available compute engines."""

    def __init__(self, args: Flags) -> None:
        super().__init__(args)
        self.project_dir = args.PROJECT_DIR

    def run(self) -> bool:
        """List available compute engines."""
        fire_event(Note(msg=""))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg="Available Compute Engines"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=""))

        # Load compute config
        try:
            compute_config = load_compute_config(Path(self.project_dir))
        except Exception:
            compute_config = ComputeConfig()

        # List engines with status
        engines = [
            {
                "name": "pushdown",
                "description": "Execute queries directly on source database",
                "enabled": True,
                "type": "native",
            },
            {
                "name": "duckdb",
                "description": "Lightweight in-process analytical database",
                "enabled": compute_config.duckdb.enabled,
                "type": "compute",
            },
            {
                "name": "spark_local",
                "description": "Apache Spark in local mode",
                "enabled": compute_config.spark_local.enabled,
                "type": "compute",
            },
            {
                "name": "spark_cluster",
                "description": "Apache Spark on cluster",
                "enabled": compute_config.spark_cluster.enabled,
                "type": "compute",
            },
        ]

        fire_event(Note(msg="Engine List:"))
        fire_event(Note(msg=""))

        for engine in engines:
            status = green("✓ Enabled") if engine["enabled"] else red("✗ Disabled")
            fire_event(Note(msg=f"  {green(engine['name'])} [{engine['type']}]"))
            fire_event(Note(msg=f"    Status: {status}"))
            fire_event(Note(msg=f"    Description: {engine['description']}"))
            fire_event(Note(msg=""))

        fire_event(Note(msg=f"Default engine: {green(compute_config.default_engine)}"))
        fire_event(Note(msg=""))
        fire_event(Note(msg="Use 'dvt compute test <engine>' to test a specific engine"))
        fire_event(Note(msg=""))

        return True

    def interpret_results(self, results) -> bool:
        return results


class ComputeTestTask(BaseTask):
    """Task to test compute engines."""

    def __init__(self, args: Flags, engine_name: Optional[str] = None) -> None:
        super().__init__(args)
        self.engine_name = engine_name
        self.project_dir = args.PROJECT_DIR

    def run(self) -> bool:
        """Test one or all compute engines."""
        fire_event(Note(msg=""))
        fire_event(Note(msg="=" * 60))
        if self.engine_name:
            fire_event(Note(msg=f"Testing Compute Engine: {self.engine_name}"))
        else:
            fire_event(Note(msg="Testing All Compute Engines"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=""))

        # Load compute config
        try:
            compute_config = load_compute_config(Path(self.project_dir))
        except Exception as e:
            fire_event(Note(msg=yellow(f"Warning: Could not load compute config: {e}")))
            compute_config = ComputeConfig()

        # Determine which engines to test
        if self.engine_name:
            engines_to_test = [self.engine_name]
        else:
            engines_to_test = ["pushdown", "duckdb", "spark_local", "spark_cluster"]

        # Test each engine
        results = {}
        for engine_name in engines_to_test:
            fire_event(Note(msg=f"Testing {engine_name}..."))
            result = self._test_engine(engine_name, compute_config)
            results[engine_name] = result

            if result["success"]:
                fire_event(Note(msg=green(f"  ✓ {result['message']}")))
            else:
                fire_event(Note(msg=red(f"  ✗ {result['message']}")))

            fire_event(Note(msg=""))

        # Summary
        success_count = sum(1 for r in results.values() if r["success"])
        fail_count = len(results) - success_count

        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg="Summary"))
        fire_event(Note(msg="=" * 60))
        fire_event(Note(msg=f"Total engines tested: {len(results)}"))
        fire_event(Note(msg=green(f"Passed: {success_count}")))
        if fail_count > 0:
            fire_event(Note(msg=red(f"Failed: {fail_count}")))

        fire_event(Note(msg=""))
        for engine_name, result in results.items():
            status = green("✓") if result["success"] else red("✗")
            fire_event(Note(msg=f"  {status} {engine_name}"))

        fire_event(Note(msg=""))

        return fail_count == 0

    def _test_engine(self, engine_name: str, compute_config: ComputeConfig) -> Dict[str, any]:
        """Test a specific compute engine."""
        try:
            if engine_name == "pushdown":
                return {
                    "success": True,
                    "message": "Pushdown is always available (uses source database)",
                }

            elif engine_name == "duckdb":
                if not compute_config.duckdb.enabled:
                    return {
                        "success": False,
                        "message": "DuckDB is disabled in configuration",
                    }

                # Try to import and initialize DuckDB
                try:
                    import duckdb

                    # Test connection
                    conn = duckdb.connect(":memory:")
                    conn.execute("SELECT 1").fetchone()
                    conn.close()

                    return {
                        "success": True,
                        "message": f"DuckDB available (version {duckdb.__version__})",
                    }
                except ImportError:
                    return {
                        "success": False,
                        "message": "DuckDB not installed (pip install duckdb)",
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"DuckDB error: {str(e)}",
                    }

            elif engine_name == "spark_local":
                if not compute_config.spark_local.enabled:
                    return {
                        "success": False,
                        "message": "Spark local mode is disabled in configuration",
                    }

                # Try to import PySpark
                try:
                    from pyspark import __version__ as spark_version
                    from pyspark.sql import SparkSession

                    # Try to create a local Spark session
                    spark = (
                        SparkSession.builder.master("local[1]")
                        .appName("DVT-Test")
                        .config("spark.ui.enabled", "false")
                        .getOrCreate()
                    )

                    # Test basic operation
                    df = spark.createDataFrame([(1,)], ["test"])
                    result = df.count()
                    spark.stop()

                    return {
                        "success": True,
                        "message": f"Spark local mode available (version {spark_version})",
                    }
                except ImportError:
                    return {
                        "success": False,
                        "message": "PySpark not installed (pip install pyspark)",
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"Spark local error: {str(e)}",
                    }

            elif engine_name == "spark_cluster":
                if not compute_config.spark_cluster.enabled:
                    return {
                        "success": False,
                        "message": "Spark cluster mode is disabled in configuration",
                    }

                if not compute_config.spark_cluster.master:
                    return {
                        "success": False,
                        "message": "Spark cluster master not configured",
                    }

                # For cluster mode, just check if PySpark is available
                # Actual cluster connection would require network access
                try:
                    from pyspark import __version__ as spark_version

                    return {
                        "success": True,
                        "message": f"PySpark available for cluster mode (version {spark_version}). Cluster connection not tested.",
                    }
                except ImportError:
                    return {
                        "success": False,
                        "message": "PySpark not installed (pip install pyspark)",
                    }

            else:
                return {
                    "success": False,
                    "message": f"Unknown engine: {engine_name}",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Test error: {str(e)}",
            }

    def interpret_results(self, results) -> bool:
        return results
