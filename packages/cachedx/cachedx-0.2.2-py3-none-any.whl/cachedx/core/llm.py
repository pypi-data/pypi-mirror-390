"""LLM integration helpers with context building and safety features"""

from __future__ import annotations

import logging
from typing import Any

from .duck import con
from .safe_sql import safe_select, validate_sql

logger = logging.getLogger(__name__)


def build_llm_context(
    include_schemas: bool = True,
    include_samples: bool = True,
    sample_limit: int = 3,
    max_context_length: int = 8000,
) -> str:
    """
    Build comprehensive context for LLM queries about cached data.

    This function generates a formatted context string that includes:
    - Available tables and views
    - Schema information for each table
    - Sample data from tables
    - Query guidelines and examples

    Args:
        include_schemas: Whether to include table schemas
        include_samples: Whether to include sample data
        sample_limit: Maximum number of sample rows per table
        max_context_length: Maximum length of context (approximate)

    Returns:
        Formatted context string for LLM

    Examples:
        >>> context = build_llm_context()
        >>> # Use with LLM:
        >>> prompt = f"Generate SQL to find active users.\n\n{context}"
    """
    try:
        context_parts = []

        # Header
        context_parts.append("# Database Schema and Context")
        context_parts.append("")
        context_parts.append("You have access to a DuckDB database with cached API responses.")
        context_parts.append(
            "Generate SELECT-only queries using the tables and columns described below."
        )
        context_parts.append("")

        # Get available tables
        tables_info = _get_tables_info()
        if not tables_info:
            context_parts.append("No tables are currently available.")
            return "\n".join(context_parts)

        context_parts.append(f"## Available Tables ({len(tables_info)} tables)")
        context_parts.append("")

        # Process each table
        for table_info in tables_info:
            table_name = table_info["table_name"]
            context_parts.append(f"### Table: `{table_name}`")

            if include_schemas:
                schema_info = _get_table_schema(table_name)
                if schema_info:
                    context_parts.append("")
                    context_parts.append("**Columns:**")
                    for col_info in schema_info:
                        col_name = col_info["column_name"]
                        col_type = col_info["data_type"]
                        nullable = "NULL" if col_info["is_nullable"] == "YES" else "NOT NULL"
                        context_parts.append(f"- `{col_name}` ({col_type}, {nullable})")
                    context_parts.append("")

            if include_samples:
                samples = _get_table_samples(table_name, sample_limit)
                if samples:
                    context_parts.append("**Sample data:**")
                    context_parts.append("```sql")

                    # Format as table
                    if samples:
                        # Get column names
                        cols = list(samples[0].keys()) if samples else []

                        # Limit columns for readability
                        display_cols = cols[:6] if len(cols) > 6 else cols

                        # Header
                        header = " | ".join(f"{col:15}" for col in display_cols)
                        context_parts.append(header)
                        context_parts.append("-" * len(header))

                        # Rows
                        for row in samples:
                            values = []
                            for col in display_cols:
                                val = row.get(col, "") if isinstance(row, dict) else ""
                                if val is None:
                                    val = "NULL"
                                elif isinstance(val, str) and len(val) > 15:
                                    val = val[:12] + "..."
                                values.append(f"{str(val):15}")
                            context_parts.append(" | ".join(values))

                    context_parts.append("```")
                    context_parts.append("")

        # Query guidelines
        context_parts.extend(
            [
                "## Query Guidelines",
                "",
                "1. **Only SELECT queries are allowed** - no INSERT, UPDATE, DELETE, etc.",
                "2. **Always include LIMIT** - queries without LIMIT will have LIMIT 200 added automatically",
                "3. **JSON columns**: Use JSON operators like `column->>'field'` to extract values",
                "4. **Raw data**: Most tables have `_raw` JSON column with original API response",
                "5. **Metadata**: Tables include `_fetched_at` and `_updated_at` timestamps",
                "",
                "## Example Queries",
                "",
                "```sql",
                "-- Basic selection with limit",
                "SELECT * FROM users LIMIT 10;",
                "",
                "-- JSON field extraction",
                "SELECT name, _raw->>'email' as email FROM users WHERE active = true;",
                "",
                "-- Time-based filtering",
                "SELECT * FROM events WHERE _fetched_at > now() - INTERVAL 1 DAY;",
                "",
                "-- Aggregation",
                "SELECT status, COUNT(*) FROM orders GROUP BY status;",
                "```",
            ]
        )

        # Join and truncate if too long
        full_context = "\n".join(context_parts)
        if len(full_context) > max_context_length:
            # Truncate but keep structure intact
            lines = full_context.split("\n")
            truncated_lines = []
            current_length = 0

            for line in lines:
                if current_length + len(line) > max_context_length - 100:
                    truncated_lines.append("... (context truncated)")
                    break
                truncated_lines.append(line)
                current_length += len(line) + 1

            full_context = "\n".join(truncated_lines)

        return full_context

    except Exception as e:
        logger.error(f"Failed to build LLM context: {e}")
        return f"Error building context: {e}"


def safe_llm_query(
    sql: str,
    params: dict[str, Any] | list[Any] | None = None,
    limit: int = 200,
    explain: bool = False,
) -> dict[str, Any]:
    """
    Execute an LLM-generated query with comprehensive safety checks and result formatting.

    Args:
        sql: SQL query string
        params: Query parameters
        limit: Maximum rows to return
        explain: Whether to include query explanation

    Returns:
        Dictionary with results, metadata, and any warnings

    Examples:
        >>> result = safe_llm_query("SELECT * FROM users WHERE active = true")
        >>> print(result['row_count'])
        >>> df = result['data']  # pandas DataFrame if available
    """
    result: dict[str, Any] = {
        "success": False,
        "data": None,
        "row_count": 0,
        "warnings": [],
        "query_used": sql,
        "execution_time_ms": 0,
    }

    try:
        import time

        start_time = time.time()

        # Validate query safety
        is_valid, error_msg = validate_sql(sql)
        if not is_valid:
            result["error"] = error_msg
            return result

        # Execute query
        data = safe_select(sql, params, limit)

        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000

        # Determine row count
        row_count = len(data) if hasattr(data, "__len__") else 0

        # Check for warnings
        warnings = []
        if row_count >= limit:
            warnings.append(
                f"Results limited to {limit} rows. Use LIMIT in query for different limits."
            )

        if row_count == 0:
            warnings.append("Query returned no results.")

        # Success
        result.update(
            {
                "success": True,
                "data": data,
                "row_count": row_count,
                "warnings": warnings,
                "execution_time_ms": int(round(execution_time, 2)),
            }
        )

        if explain:
            result["explanation"] = _explain_query_results(sql, row_count)

        return result

    except Exception as e:
        result["error"] = f"Query execution failed: {e}"
        return result


def suggest_queries(
    table_name: str | None = None, max_suggestions: int = 5
) -> list[dict[str, str]]:
    """
    Suggest useful queries based on available data.

    Args:
        table_name: Focus on specific table (None for all tables)
        max_suggestions: Maximum number of suggestions

    Returns:
        List of query suggestions with descriptions

    Examples:
        >>> suggestions = suggest_queries("users")
        >>> for s in suggestions:
        ...     print(f"{s['description']}: {s['sql']}")
    """
    suggestions: list[dict[str, str]] = []

    try:
        tables_info = _get_tables_info()
        if not tables_info:
            return suggestions

        # Filter to specific table if requested
        if table_name:
            tables_info = [t for t in tables_info if t["table_name"] == table_name]

        for table_info in tables_info[:max_suggestions]:
            table = table_info["table_name"]

            # Basic exploration queries
            suggestions.append(
                {
                    "description": f"Explore {table} structure and sample data",
                    "sql": f"SELECT * FROM {table} LIMIT 5",  # nosec B608
                    "category": "exploration",
                }
            )

            # Row count
            suggestions.append(
                {
                    "description": f"Count total rows in {table}",
                    "sql": f"SELECT COUNT(*) as row_count FROM {table}",  # nosec B608
                    "category": "summary",
                }
            )

            # Recent data
            if table_info.get("has_timestamp"):
                suggestions.append(
                    {
                        "description": f"Recent {table} entries",
                        "sql": f"SELECT * FROM {table} ORDER BY _fetched_at DESC LIMIT 10",  # nosec B608
                        "category": "temporal",
                    }
                )

            # JSON exploration
            if table_info.get("has_raw_column"):
                suggestions.append(
                    {
                        "description": f"Explore JSON structure in {table}",
                        "sql": f"SELECT json_keys(_raw) as available_fields FROM {table} LIMIT 1",  # nosec B608
                        "category": "schema",
                    }
                )

        return suggestions[:max_suggestions]

    except Exception as e:
        logger.error(f"Failed to generate query suggestions: {e}")
        return []


def _get_tables_info() -> list[dict[str, Any]]:
    """Get information about available tables"""
    try:
        result = (
            con()
            .execute("""
            SELECT
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema = 'main'
            AND table_name NOT LIKE 'information_schema.%'
            AND table_name NOT LIKE 'pg_%'
            ORDER BY table_name
        """)
            .fetchall()
        )

        tables = []
        for row in result:
            table_name = row[0]

            # Check for common columns
            columns = _get_table_schema(table_name)
            has_timestamp = any(
                col["column_name"] in ["_fetched_at", "_updated_at"] for col in columns
            )
            has_raw_column = any(col["column_name"] == "_raw" for col in columns)

            tables.append(
                {
                    "table_name": table_name,
                    "table_type": row[1],
                    "has_timestamp": has_timestamp,
                    "has_raw_column": has_raw_column,
                }
            )

        return tables

    except Exception as e:
        logger.error(f"Failed to get tables info: {e}")
        return []


def _get_table_schema(table_name: str) -> list[dict[str, Any]]:
    """Get schema information for a table"""
    try:
        result = (
            con()
            .execute(
                """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = ?
            ORDER BY ordinal_position
        """,
                [table_name],
            )
            .fetchall()
        )

        return [
            {"column_name": row[0], "data_type": row[1], "is_nullable": row[2]} for row in result
        ]

    except Exception as e:
        logger.error(f"Failed to get schema for {table_name}: {e}")
        return []


def _get_table_samples(table_name: str, limit: int = 3) -> list[dict[str, Any]]:
    """Get sample rows from a table"""
    try:
        # Get column names first
        columns = _get_table_schema(table_name)
        if not columns:
            return []

        # Limit columns for readability
        col_names = [col["column_name"] for col in columns[:8]]  # First 8 columns
        col_list = ", ".join(col_names)

        result = (
            con()
            .execute(f"""
            SELECT {col_list}
            FROM {table_name}
            LIMIT {limit}
        """)  # nosec B608
            .fetchall()
        )

        # Convert to list of dicts
        samples = []
        for row in result:
            row_dict = {}
            for i, col_name in enumerate(col_names):
                value = row[i] if i < len(row) else None
                # Truncate long values
                if isinstance(value, str) and len(value) > 100:
                    value = value[:97] + "..."
                row_dict[col_name] = value
            samples.append(row_dict)

        return samples

    except Exception as e:
        logger.error(f"Failed to get samples for {table_name}: {e}")
        return []


def _explain_query_results(sql: str, row_count: int) -> str:
    """Generate explanation for query results"""
    explanation_parts = []

    # Basic query analysis
    sql_upper = sql.upper()

    if "COUNT(*)" in sql_upper:
        explanation_parts.append("This is a count query that returns the number of rows.")
    elif "GROUP BY" in sql_upper:
        explanation_parts.append(
            "This is an aggregation query that groups results by one or more columns."
        )
    elif "JOIN" in sql_upper:
        explanation_parts.append("This query joins data from multiple tables.")
    elif "ORDER BY" in sql_upper:
        explanation_parts.append("Results are sorted by the specified columns.")
    else:
        explanation_parts.append("This is a basic selection query.")

    # Result summary
    if row_count == 0:
        explanation_parts.append("No rows matched the query criteria.")
    elif row_count == 1:
        explanation_parts.append("Query returned 1 row.")
    else:
        explanation_parts.append(f"Query returned {row_count} rows.")

    return " ".join(explanation_parts)
