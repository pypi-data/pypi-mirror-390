# DVT (Data Virtualization Tool)

**DVT** is an all-in-one ELT solution that adds comprehensive data virtualization capabilities to dbt-core foundations.

## Quick Start

### Installation

```bash
# Install DVT with all features (includes PySpark, DuckDB, and 20 JDBC connectors)
pip install dvt-core

# Verify installation
dvt --version
```

**What's included:**
- ✅ Core DVT + all dbt functionality
- ✅ DuckDB compute engine (~10MB)
- ✅ PySpark compute engine (~250MB)
- ✅ 20 JDBC connectors (~200MB) for Spark cross-database queries
- ✅ Complete documentation and examples

**Total install size:** ~450-500MB

### Create Your First Project

```bash
# Initialize new project
dvt init my_analytics_project
cd my_analytics_project

# Configure profiles in ~/.dvt/profiles.yml
# Add multiple database connections

# Test connections
dvt profiles test --all

# Run your models
dvt run
```

## What is DVT?

DVT enables you to:

- **Query across databases**: Join PostgreSQL, MySQL, Snowflake, and 20+ other databases in a single SQL query
- **Maintain dbt compatibility**: 100% backwards compatible with existing dbt projects
- **Use intelligent query routing**: Automatic optimization between pushdown and compute layer execution
- **Manage multiple connections**: Support multiple database profiles in a single project
- **Choose your compute engine**: Use DuckDB for fast analytics or Spark for distributed processing

## Key Features

### Cross-Database Queries

```sql
-- Join PostgreSQL customers with MySQL orders
select
    c.customer_id,
    c.name,
    count(o.order_id) as order_count
from {{ source('postgres_prod', 'customers') }} c
left join {{ source('mysql_legacy', 'orders') }} o
    on c.customer_id = o.customer_id
group by c.customer_id, c.name
```

DVT automatically detects heterogeneous sources and routes execution to the appropriate compute engine.

### Multi-Profile Support

Configure multiple database connections:

```yaml
# profiles.yml
postgres_prod:
  adapter: postgres
  host: prod-db.example.com
  # ...

mysql_legacy:
  adapter: mysql
  host: legacy-db.example.com
  # ...
```

Reference profiles in source definitions:

```yaml
# sources.yml
sources:
  - name: postgres_prod
    profile: postgres_prod
    tables:
      - name: customers

  - name: mysql_legacy
    profile: mysql_legacy
    tables:
      - name: orders
```

## Included JDBC Connectors

DVT bundles 20 JDBC connectors (~200MB) for Spark:

**Relational Databases:**
- PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, DB2

**Cloud Data Warehouses:**
- Snowflake, BigQuery, Redshift, Athena

**Analytics & MPP:**
- ClickHouse, Vertica, Presto, Trino

**Other:**
- H2, SQLite, Derby, Hive, InfluxDB, TimescaleDB

**Note:** Phoenix connector (149MB) exceeds PyPI limits and can be downloaded separately:
```bash
dvt connectors download --connector=phoenix
```

## DVT Commands

### Standard dbt Commands (100% Compatible)

All dbt commands work identically:

```bash
dvt run                    # Run models
dvt test                   # Run tests
dvt build                  # Run + test models
dvt compile                # Compile SQL
dvt docs generate          # Generate documentation
```

### DVT Extensions

**Profile Management:**
```bash
dvt profiles list           # List all configured profiles
dvt profiles show postgres_prod
dvt profiles test --all     # Test all profile connections
```

**Compute Layer:**
```bash
dvt compute show            # Show compute configuration
dvt compute engines         # List available engines
dvt compute test --all      # Test compute engines
```

**Enhanced Debug:**
```bash
dvt debug --all-profiles    # Test all profiles (not just target)
```

## Documentation

For complete documentation, see:

- **[Sample Project Guide](../docs/sample-project-guide.md)** - Complete walkthrough building a real DVT project
- **[DVT Architecture](../docs/DVT_ARCHITECTURE.md)** - Detailed architecture overview
- **[Migration Guide](../docs/migration-guide.md)** - Migrate from dbt to DVT
- **[CLI Reference](../docs/cli-reference.md)** - Complete command reference
- **[Connector Catalog](connectors/README.md)** - JDBC connector documentation

## Migration from dbt

DVT is 100% backwards compatible with dbt:

```bash
# Install DVT
pip install dvt-core

# Replace dbt commands with dvt
dvt run  # instead of: dbt run
```

That's it! Your existing dbt project works as-is.

## Requirements

- Python 3.10, 3.11, 3.12, or 3.13
- Database adapters for your databases (e.g., `dbt-postgres`, `dbt-snowflake`)

## License

Apache License 2.0 - Same as dbt-core

## Support

- **Repository**: https://github.com/hex/dvt-core
- **Issues**: https://github.com/hex/dvt-core/issues
- **Documentation**: See `/docs` directory in repository

## Acknowledgments

DVT is built on top of [dbt-core](https://github.com/dbt-labs/dbt-core) and maintains deep compatibility with the dbt ecosystem.
