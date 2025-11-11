"""
Compute layer configuration for DVT.

This module handles loading and parsing compute.yml configuration files,
which define DuckDB and Spark settings for the compute layer.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from dbt_common.events.functions import fire_event
from dbt_common.events.types import Note
from dbt_common.exceptions import DbtRuntimeError


@dataclass
class DuckDBConfig:
    """DuckDB compute engine configuration."""

    memory_limit: str = "8GB"
    threads: int = 4
    temp_directory: str = "/tmp/duckdb"
    max_memory: str = "8GB"
    enable_optimizer: bool = True
    enable_profiling: bool = False
    enable_progress_bar: bool = True
    extensions: List[str] = field(
        default_factory=lambda: [
            "httpfs",
            "postgres_scanner",
            "mysql_scanner",
            "parquet",
            "json",
            "icu",
            "fts",
        ]
    )
    s3: Optional[Dict[str, Any]] = None
    postgres_scanner: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DuckDBConfig":
        """Create DuckDBConfig from dictionary."""
        return cls(
            memory_limit=data.get("memory_limit", "8GB"),
            threads=data.get("threads", 4),
            temp_directory=data.get("temp_directory", "/tmp/duckdb"),
            max_memory=data.get("max_memory", "8GB"),
            enable_optimizer=data.get("enable_optimizer", True),
            enable_profiling=data.get("enable_profiling", False),
            enable_progress_bar=data.get("enable_progress_bar", True),
            extensions=data.get(
                "extensions", cls.__dataclass_fields__["extensions"].default_factory()
            ),
            s3=data.get("s3"),
            postgres_scanner=data.get("postgres_scanner"),
        )


@dataclass
class SparkConnector:
    """Spark connector/JAR specification."""

    name: str
    version: str
    maven: str
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SparkConnector":
        """Create SparkConnector from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            maven=data["maven"],
            enabled=data.get("enabled", True),
        )


@dataclass
class SparkLocalConfig:
    """Spark local (single node) configuration."""

    master: str = "local[*]"
    app_name: str = "dvt-transformation"
    memory: str = "4g"
    driver_memory: str = "2g"
    executor_memory: str = "4g"
    executor_cores: int = 4
    default_parallelism: int = 8
    ui_port: int = 4040
    ui_enabled: bool = True
    log_level: str = "WARN"
    config: Dict[str, Any] = field(default_factory=dict)
    connectors: List[SparkConnector] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SparkLocalConfig":
        """Create SparkLocalConfig from dictionary."""
        connectors = [SparkConnector.from_dict(c) for c in data.get("connectors", [])]
        return cls(
            master=data.get("master", "local[*]"),
            app_name=data.get("app_name", "dvt-transformation"),
            memory=data.get("memory", "4g"),
            driver_memory=data.get("driver_memory", "2g"),
            executor_memory=data.get("executor_memory", "4g"),
            executor_cores=data.get("executor_cores", 4),
            default_parallelism=data.get("default_parallelism", 8),
            ui_port=data.get("ui_port", 4040),
            ui_enabled=data.get("ui_enabled", True),
            log_level=data.get("log_level", "WARN"),
            config=data.get("config", {}),
            connectors=connectors,
        )


@dataclass
class SparkClusterConfig:
    """Spark cluster (distributed) configuration."""

    master: str
    deploy_mode: str = "client"
    app_name: str = "dvt-transformation-cluster"
    executor_memory: str = "8g"
    executor_cores: int = 4
    num_executors: int = 10
    driver_memory: str = "4g"
    driver_cores: int = 2
    dynamic_allocation: Optional[Dict[str, Any]] = None
    config: Dict[str, Any] = field(default_factory=dict)
    connectors: List[SparkConnector] = field(default_factory=list)
    kerberos: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SparkClusterConfig":
        """Create SparkClusterConfig from dictionary."""
        connectors = [SparkConnector.from_dict(c) for c in data.get("connectors", [])]
        return cls(
            master=data["master"],
            deploy_mode=data.get("deploy_mode", "client"),
            app_name=data.get("app_name", "dvt-transformation-cluster"),
            executor_memory=data.get("executor_memory", "8g"),
            executor_cores=data.get("executor_cores", 4),
            num_executors=data.get("num_executors", 10),
            driver_memory=data.get("driver_memory", "4g"),
            driver_cores=data.get("driver_cores", 2),
            dynamic_allocation=data.get("dynamic_allocation"),
            config=data.get("config", {}),
            connectors=connectors,
            kerberos=data.get("kerberos"),
        )


@dataclass
class AutoSelectRule:
    """Auto-selection rule for compute engine."""

    name: str
    priority: int
    condition: Union[str, Dict[str, Any]]
    action: str
    description: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoSelectRule":
        """Create AutoSelectRule from dictionary."""
        return cls(
            name=data["name"],
            priority=data["priority"],
            condition=data["condition"],
            action=data["action"],
            description=data.get("description", ""),
        )


@dataclass
class AutoSelectConfig:
    """Auto-selection configuration."""

    enabled: bool = True
    rules: List[AutoSelectRule] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoSelectConfig":
        """Create AutoSelectConfig from dictionary."""
        rules = [AutoSelectRule.from_dict(r) for r in data.get("rules", [])]
        # Sort rules by priority (highest first)
        rules.sort(key=lambda r: r.priority, reverse=True)
        return cls(
            enabled=data.get("enabled", True),
            rules=rules,
        )


@dataclass
class ConnectorManagementConfig:
    """Connector management configuration."""

    auto_download: bool = True
    cache_dir: str = "~/.dvt/connectors"
    maven_repos: List[str] = field(
        default_factory=lambda: [
            "https://repo1.maven.org/maven2",
            "https://packages.confluent.io/maven",
            "https://maven-central.storage.googleapis.com/maven2",
        ]
    )
    verify_checksums: bool = True
    check_updates: str = "weekly"
    bundled_path: str = "${DVT_INSTALL_DIR}/connectors/jars"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConnectorManagementConfig":
        """Create ConnectorManagementConfig from dictionary."""
        return cls(
            auto_download=data.get("auto_download", True),
            cache_dir=data.get("cache_dir", "~/.dvt/connectors"),
            maven_repos=data.get(
                "maven_repos", cls.__dataclass_fields__["maven_repos"].default_factory()
            ),
            verify_checksums=data.get("verify_checksums", True),
            check_updates=data.get("check_updates", "weekly"),
            bundled_path=data.get("bundled_path", "${DVT_INSTALL_DIR}/connectors/jars"),
        )


@dataclass
class PerformanceConfig:
    """Performance monitoring configuration."""

    enable_profiling: bool = False
    log_slow_queries: bool = True
    slow_query_threshold: str = "60s"
    collect_metrics: bool = True
    metrics_output: str = "/tmp/dvt_metrics.json"
    save_execution_plans: bool = False
    execution_plan_dir: str = "~/.dvt/execution_plans"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceConfig":
        """Create PerformanceConfig from dictionary."""
        return cls(
            enable_profiling=data.get("enable_profiling", False),
            log_slow_queries=data.get("log_slow_queries", True),
            slow_query_threshold=data.get("slow_query_threshold", "60s"),
            collect_metrics=data.get("collect_metrics", True),
            metrics_output=data.get("metrics_output", "/tmp/dvt_metrics.json"),
            save_execution_plans=data.get("save_execution_plans", False),
            execution_plan_dir=data.get("execution_plan_dir", "~/.dvt/execution_plans"),
        )


@dataclass
class DevelopmentConfig:
    """Development and debugging configuration."""

    verbose_errors: bool = True
    explain_queries: bool = False
    dev_mode: bool = False
    dev_limit: int = 1000
    cache_intermediate: bool = True
    cache_dir: str = "/tmp/dvt_cache"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DevelopmentConfig":
        """Create DevelopmentConfig from dictionary."""
        return cls(
            verbose_errors=data.get("verbose_errors", True),
            explain_queries=data.get("explain_queries", False),
            dev_mode=data.get("dev_mode", False),
            dev_limit=data.get("dev_limit", 1000),
            cache_intermediate=data.get("cache_intermediate", True),
            cache_dir=data.get("cache_dir", "/tmp/dvt_cache"),
        )


@dataclass
class ComputeConfig:
    """
    Complete compute layer configuration.

    This represents the parsed compute.yml file.
    """

    default_engine: str = "auto"
    duckdb: DuckDBConfig = field(default_factory=DuckDBConfig)
    spark_local: Optional[SparkLocalConfig] = None
    spark_cluster: Optional[SparkClusterConfig] = None
    auto_select: AutoSelectConfig = field(default_factory=AutoSelectConfig)
    connector_management: ConnectorManagementConfig = field(
        default_factory=ConnectorManagementConfig
    )
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    development: DevelopmentConfig = field(default_factory=DevelopmentConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComputeConfig":
        """Create ComputeConfig from dictionary."""
        return cls(
            default_engine=data.get("default_engine", "auto"),
            duckdb=DuckDBConfig.from_dict(data.get("duckdb", {})),
            spark_local=(
                SparkLocalConfig.from_dict(data["spark_local"]) if "spark_local" in data else None
            ),
            spark_cluster=(
                SparkClusterConfig.from_dict(data["spark_cluster"])
                if "spark_cluster" in data
                else None
            ),
            auto_select=AutoSelectConfig.from_dict(data.get("auto_select", {})),
            connector_management=ConnectorManagementConfig.from_dict(
                data.get("connector_management", {})
            ),
            performance=PerformanceConfig.from_dict(data.get("performance", {})),
            development=DevelopmentConfig.from_dict(data.get("development", {})),
        )

    @classmethod
    def load_from_file(cls, file_path: Path) -> "ComputeConfig":
        """
        Load compute configuration from YAML file.

        Args:
            file_path: Path to compute.yml file

        Returns:
            ComputeConfig instance

        Raises:
            DbtRuntimeError: If file cannot be read or parsed
        """
        try:
            if not file_path.exists():
                fire_event(Note(msg=f"Compute config not found at {file_path}, using defaults"))
                return cls()

            with open(file_path, "r") as f:
                data = yaml.safe_load(f)

            if data is None:
                fire_event(Note(msg=f"Empty compute config at {file_path}, using defaults"))
                return cls()

            return cls.from_dict(data)

        except yaml.YAMLError as e:
            raise DbtRuntimeError(f"Failed to parse compute config: {e}")
        except Exception as e:
            raise DbtRuntimeError(f"Failed to load compute config from {file_path}: {e}")

    def get_engine_config(
        self, engine: str
    ) -> Union[DuckDBConfig, SparkLocalConfig, SparkClusterConfig, None]:
        """
        Get configuration for specific compute engine.

        Args:
            engine: Engine name ('duckdb', 'spark_local', 'spark_cluster')

        Returns:
            Engine configuration or None if not configured
        """
        if engine == "duckdb":
            return self.duckdb
        elif engine == "spark_local":
            return self.spark_local
        elif engine == "spark_cluster":
            return self.spark_cluster
        else:
            return None


def load_compute_config(project_dir: Optional[Path] = None) -> ComputeConfig:
    """
    Load compute configuration from standard locations.

    Searches in order:
    1. <project_root>/compute.yml
    2. ~/.dbt/compute.yml
    3. Default configuration

    Args:
        project_dir: Project directory (optional)

    Returns:
        ComputeConfig instance
    """
    # Try project directory first
    if project_dir:
        project_compute = project_dir / "compute.yml"
        if project_compute.exists():
            fire_event(Note(msg=f"Loading compute config from {project_compute}"))
            return ComputeConfig.load_from_file(project_compute)

    # Try home directory
    home_compute = Path.home() / ".dbt" / "compute.yml"
    if home_compute.exists():
        fire_event(Note(msg=f"Loading compute config from {home_compute}"))
        return ComputeConfig.load_from_file(home_compute)

    # Use defaults
    fire_event(Note(msg="No compute.yml found, using default configuration"))
    return ComputeConfig()
