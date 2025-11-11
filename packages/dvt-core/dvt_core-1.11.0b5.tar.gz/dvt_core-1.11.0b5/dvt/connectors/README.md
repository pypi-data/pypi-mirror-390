# DVT Database Connectors

This directory contains the connector catalog for DVT's compute engines (DuckDB and Spark).

## Overview

DVT uses **dbt adapters** for all database connections, both for reading from source databases and writing to target databases. This provides a unified, Python-based connection mechanism that works with any database supported by the dbt ecosystem.

## No JARs Required

Unlike traditional Spark solutions that require JDBC JAR files, DVT extracts data from databases using dbt adapters and transfers it to the compute layer via Apache Arrow format. This approach:

- **Eliminates JAR dependencies** - Pure Python solution
- **Works with any dbt adapter** - 30+ databases supported out of the box
- **Provides consistent interface** - Same connection mechanism for all databases
- **Reduces package size** - No 200+ MB of JARs to download
- **Simplifies configuration** - Single `profiles.yml` for all connections

## Architecture

### Data Flow

```
Source DB → dbt adapter → Agate Table → Arrow Table →
Compute Engine (DuckDB/Spark) → Arrow Table → Target dbt adapter → Target DB
```

### Example: Cross-Database Query

```yaml
# profiles.yml
postgres_prod:
  adapter: postgres
  host: db.example.com
  port: 5432
  user: analytics
  password: "{{ env_var('POSTGRES_PASSWORD') }}"
  database: production
  schema: public

mysql_legacy:
  adapter: mysql
  host: legacy-db.example.com
  port: 3306
  user: readonly
  password: "{{ env_var('MYSQL_PASSWORD') }}"
  database: orders_db
```

```yaml
# sources.yml
sources:
  - name: postgres_source
    profile: postgres_prod
    tables:
      - name: customers

  - name: mysql_source
    profile: mysql_legacy
    tables:
      - name: orders
```

```sql
-- models/cross_db_analysis.sql
select
    c.customer_id,
    c.name,
    count(o.order_id) as order_count
from {{ source('postgres_source', 'customers') }} c
left join {{ source('mysql_source', 'orders') }} o
    on c.customer_id = o.customer_id
group by c.customer_id, c.name
```

DVT will automatically:
1. Detect heterogeneous sources (PostgreSQL + MySQL)
2. Extract data via dbt adapters (`dbt-postgres`, `dbt-mysql`)
3. Convert to Arrow format for efficient transfer
4. Load into compute engine (DuckDB or Spark)
5. Execute the query in the compute layer
6. Return unified result set

## Supported Databases

DVT works with **any database that has a dbt adapter**. This includes:

**Relational Databases:**
- PostgreSQL (`dbt-postgres`)
- MySQL (`dbt-mysql`)
- SQL Server (`dbt-sqlserver`)
- Oracle (`dbt-oracle`)

**Cloud Data Warehouses:**
- Snowflake (`dbt-snowflake`)
- BigQuery (`dbt-bigquery`)
- Redshift (`dbt-redshift`)
- Databricks (`dbt-databricks`)

**Analytics Databases:**
- DuckDB (`dbt-duckdb`)
- ClickHouse (`dbt-clickhouse`)
- Trino (`dbt-trino`)

**And many more...**

See the [dbt adapter registry](https://docs.getdbt.com/docs/supported-data-platforms) for the complete list.

## Installation

Install DVT with the dbt adapters you need:

```bash
# Install DVT core
pip install dvt-core

# Install adapters for your databases
pip install dbt-postgres dbt-mysql dbt-snowflake
```

## Configuration

Configure profiles in `~/.dvt/profiles.yml` using the same format as dbt:

```yaml
# PostgreSQL
postgres_prod:
  adapter: postgres
  host: db.example.com
  port: 5432
  user: analytics
  password: "{{ env_var('POSTGRES_PASSWORD') }}"
  database: production
  schema: public

# MySQL
mysql_legacy:
  adapter: mysql
  host: legacy-db.example.com
  port: 3306
  user: readonly
  password: "{{ env_var('MYSQL_PASSWORD') }}"
  database: orders_db

# Snowflake
snowflake_analytics:
  adapter: snowflake
  account: mycompany
  user: analytics
  password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
  database: analytics
  warehouse: compute_wh
  schema: public
```

Test your connections:

```bash
dvt profiles test --all
```

## Compute Engines

DVT supports two compute engines for cross-database queries:

### DuckDB (Default)
- In-process analytical database
- Fast for datasets < 10GB
- Zero configuration required
- Perfect for development and small-to-medium workloads

### PySpark
- Distributed compute engine
- Scales to 100GB+ datasets
- Local or cluster mode
- No JDBC JARs required - uses dbt adapters

Configure in `dvt_project.yml`:

```yaml
compute:
  default_engine: duckdb  # or 'spark'

  duckdb:
    memory_limit: '4GB'
    threads: 4

  spark:
    type: local
    master: 'local[*]'
    config:
      spark.executor.memory: '4g'
```

## How It Works

### Traditional Spark Approach (Old)
```
Spark → JDBC JARs (200+ MB) → Database
```
- Requires downloading JARs
- Different JAR for each database
- Version conflicts
- Large package size

### DVT Approach (New)
```
Database → dbt adapter → Arrow → Compute Engine
```
- Pure Python solution
- Uses existing dbt adapters
- No JARs needed
- Small package size (~10 MB core)

### Implementation Details

When DVT executes a cross-database query:

1. **Query Analysis**: DVT analyzes the SQL to identify all source databases
2. **Data Extraction**: For each source:
   - Get dbt adapter for the profile
   - Execute `SELECT * FROM table` via adapter
   - Receive results as Agate table
3. **Arrow Conversion**: Convert Agate tables to Arrow format (zero-copy)
4. **Compute Layer**:
   - **DuckDB**: Register Arrow tables directly
   - **Spark**: Convert Arrow → Pandas → Spark DataFrame
5. **Query Execution**: Execute the original query in the compute engine
6. **Results**: Return results as Arrow table

## Catalog File

The `catalog.yml` file is retained for documentation purposes and to map database types to dbt adapter names:

```yaml
postgres:
  adapter_name: postgres
  dbt_package: dbt-postgres
  description: PostgreSQL database
  connection_docs: https://docs.getdbt.com/reference/warehouse-setups/postgres-setup

mysql:
  adapter_name: mysql
  dbt_package: dbt-mysql
  description: MySQL database
  connection_docs: https://docs.getdbt.com/reference/warehouse-setups/mysql-setup
```

## Troubleshooting

### Missing Adapter Error

If you see `adapter not found` errors:

```bash
# Check installed adapters
pip list | grep dbt-

# Install missing adapter
pip install dbt-postgres
```

### Connection Failures

If connections fail:

```bash
# Test individual profile
dvt profiles test postgres_prod

# Test all profiles
dvt profiles test --all

# Check profile configuration
dvt profiles show postgres_prod
```

### Performance Issues

For large datasets:

1. Switch to Spark engine:
   ```yaml
   compute:
     default_engine: spark
   ```

2. Increase memory limits:
   ```yaml
   spark:
     config:
       spark.executor.memory: '8g'
       spark.driver.memory: '4g'
   ```

3. Use per-model configuration:
   ```sql
   {{ config(compute='spark') }}
   ```

## See Also

- [Multi-Profile Guide](../../docs/multi-profile-guide.md)
- [Compute Configuration](../../docs/compute-configuration.md)
- [DVT Architecture](../../docs/DVT_ARCHITECTURE.md)
- [dbt Adapter Documentation](https://docs.getdbt.com/docs/supported-data-platforms)
