"""
Data extraction utilities for DVT compute engines.

This module provides utilities to extract data from source databases using dbt adapters
and convert it to Apache Arrow format for efficient processing in compute engines.
"""

from typing import Any, Optional

import pyarrow as pa
from agate import Table as AgateTable

from dbt.adapters.protocol import AdapterProtocol
from dvt.events import fire_event
from dvt.events.types import Note


class DataExtractor:
    """
    Extract data from databases using dbt adapters and convert to Arrow format.

    This class provides the bridge between dbt adapters (which return Agate tables)
    and DVT compute engines (which use Arrow tables for efficient data transfer).

    Architecture:
        Source DB → dbt adapter.execute() → Agate Table → Arrow Table → Compute Engine
    """

    @staticmethod
    def agate_to_arrow(agate_table: AgateTable) -> pa.Table:
        """
        Convert an Agate table to an Arrow table.

        Agate is dbt's data structure for query results. Arrow provides zero-copy
        data interchange between processes.

        Args:
            agate_table: Agate table from dbt adapter execution

        Returns:
            pyarrow.Table with the same data and schema

        Example:
            >>> response, agate_table = adapter.execute("SELECT * FROM table", fetch=True)
            >>> arrow_table = DataExtractor.agate_to_arrow(agate_table)
            >>> # Now use arrow_table with DuckDB or Spark
        """
        if agate_table is None or len(agate_table.rows) == 0:
            # Empty table - create empty Arrow table with column names and types
            schema_fields = []
            for col_name, col_type in zip(agate_table.column_names, agate_table.column_types):
                arrow_type = DataExtractor._agate_type_to_arrow(col_type)
                schema_fields.append((col_name, arrow_type))

            schema = pa.schema(schema_fields)
            return pa.Table.from_pydict({col: [] for col in agate_table.column_names}, schema=schema)

        # Convert Agate rows to Python dictionaries
        columns = {col_name: [] for col_name in agate_table.column_names}

        for row in agate_table.rows:
            for col_name, value in zip(agate_table.column_names, row.values()):
                columns[col_name].append(value)

        # Convert to Arrow table (Arrow will infer types)
        arrow_table = pa.Table.from_pydict(columns)

        fire_event(
            Note(
                msg=f"Converted Agate table to Arrow: {len(agate_table.rows)} rows, "
                f"{len(agate_table.column_names)} columns"
            )
        )

        return arrow_table

    @staticmethod
    def _agate_type_to_arrow(agate_type: Any) -> pa.DataType:
        """
        Map Agate data types to Arrow data types.

        Args:
            agate_type: Agate data type instance

        Returns:
            Corresponding Arrow data type
        """
        import agate

        # Map common Agate types to Arrow types
        type_name = type(agate_type).__name__

        type_mapping = {
            "Boolean": pa.bool_(),
            "Number": pa.float64(),
            "Integer": pa.int64(),
            "Text": pa.string(),
            "Date": pa.date32(),
            "DateTime": pa.timestamp("us"),
            "TimeDelta": pa.duration("us"),
        }

        return type_mapping.get(type_name, pa.string())

    @staticmethod
    def extract_table(
        adapter: AdapterProtocol,
        sql: str,
        source_name: Optional[str] = None,
    ) -> pa.Table:
        """
        Extract data from a database using a dbt adapter.

        This is the main method for data extraction. It:
        1. Executes SQL via the dbt adapter
        2. Receives results as Agate table
        3. Converts to Arrow table
        4. Returns Arrow table for compute engine

        Args:
            adapter: dbt adapter instance for the source database
            sql: SQL query to execute (usually SELECT * FROM table)
            source_name: Optional source name for logging

        Returns:
            Arrow table with query results

        Example:
            >>> from dvt.adapters.multi_adapter_manager import MultiAdapterManager
            >>> manager = MultiAdapterManager(profiles)
            >>> adapter = manager.get_or_create_adapter("postgres_prod")
            >>> arrow_table = DataExtractor.extract_table(
            ...     adapter,
            ...     "SELECT * FROM customers WHERE active = true",
            ...     source_name="postgres_prod.customers"
            ... )
        """
        source_label = source_name or "table"

        fire_event(Note(msg=f"Extracting data from {source_label} via dbt adapter"))

        try:
            # Execute query via dbt adapter
            # The adapter.execute() method returns (response, agate_table) when fetch=True
            response, agate_table = adapter.execute(sql, fetch=True)

            if agate_table is None:
                fire_event(Note(msg=f"No data returned from {source_label}"))
                # Return empty Arrow table
                return pa.Table.from_pydict({})

            # Convert Agate → Arrow
            arrow_table = DataExtractor.agate_to_arrow(agate_table)

            fire_event(
                Note(
                    msg=f"Successfully extracted {len(arrow_table)} rows "
                    f"from {source_label}"
                )
            )

            return arrow_table

        except Exception as e:
            fire_event(
                Note(
                    msg=f"Error extracting data from {source_label}: {str(e)}"
                )
            )
            raise

    @staticmethod
    def extract_relation(
        adapter: AdapterProtocol,
        relation: Any,
        columns: Optional[list[str]] = None,
        where_clause: Optional[str] = None,
    ) -> pa.Table:
        """
        Extract data from a database relation (table/view).

        Convenience method that builds a SELECT query and extracts the data.

        Args:
            adapter: dbt adapter instance
            relation: Relation object (has database, schema, identifier)
            columns: Optional list of columns to select (default: *)
            where_clause: Optional WHERE clause for filtering

        Returns:
            Arrow table with relation data

        Example:
            >>> arrow_table = DataExtractor.extract_relation(
            ...     adapter,
            ...     relation,
            ...     columns=["id", "name", "email"],
            ...     where_clause="created_at > '2024-01-01'"
            ... )
        """
        # Build SELECT query
        column_list = "*" if not columns else ", ".join(columns)
        sql = f"SELECT {column_list} FROM {relation}"

        if where_clause:
            sql += f" WHERE {where_clause}"

        source_name = f"{relation.database}.{relation.schema}.{relation.identifier}"

        return DataExtractor.extract_table(adapter, sql, source_name)
