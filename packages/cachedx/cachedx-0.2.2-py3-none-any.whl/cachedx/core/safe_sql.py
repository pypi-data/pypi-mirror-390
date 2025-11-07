"""SQL safety layer for LLM-generated queries"""

from __future__ import annotations

import re
from typing import Any

from .duck import con

# Pattern to match SELECT statements (case-insensitive)
_SELECT_PATTERN = re.compile(r"(?is)^\s*select\s")

# Dangerous keywords that should never appear in LLM queries
_DANGEROUS_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "CREATE",
    "ALTER",
    "TRUNCATE",
    "REPLACE",
    "MERGE",
    "COPY",
    "ATTACH",
    "DETACH",
}


def safe_select(
    sql: str, params: dict[str, Any] | list[Any] | None = None, limit: int = 200
) -> Any:
    """
    Execute a SELECT-only query safely with automatic LIMIT injection.

    This function provides multiple safety layers:
    1. Only allows SELECT statements
    2. Blocks dangerous keywords
    3. Automatically adds LIMIT if missing
    4. Returns pandas DataFrame if available, otherwise list of dicts

    Args:
        sql: SQL query string (must be SELECT)
        params: Query parameters
        limit: Maximum number of rows to return (default: 200)

    Returns:
        pandas DataFrame if pandas is available, otherwise list of dicts

    Raises:
        ValueError: If query is not a safe SELECT statement

    Examples:
        >>> df = safe_select("SELECT * FROM users WHERE active = true")
        >>> rows = safe_select("SELECT name FROM users WHERE id = ?", [123])
    """
    if not sql or not isinstance(sql, str):
        raise ValueError("SQL query must be a non-empty string")

    # Clean up the query
    clean_sql = sql.strip().rstrip(";")

    # Check if it's a SELECT statement
    if not _SELECT_PATTERN.match(clean_sql):
        raise ValueError("Only SELECT statements are allowed")

    # Check for dangerous keywords (word boundaries only)
    upper_sql = clean_sql.upper()
    for keyword in _DANGEROUS_KEYWORDS:
        # Use word boundaries to avoid matching substrings like "updated_at" containing "UPDATE"
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, upper_sql):
            raise ValueError(f"Query contains dangerous keyword: {keyword}")

    # Add LIMIT if not present (use regex to handle various whitespace patterns)
    if not re.search(r"\bLIMIT\b", upper_sql):
        clean_sql = f"{clean_sql} LIMIT {limit}"

    # Execute query
    try:
        cursor = con().execute(clean_sql, params or [])

        # Try to return pandas DataFrame if available
        try:
            import pandas  # noqa: F401

            return cursor.df()
        except ImportError:
            # Fall back to list of dicts
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row, strict=False)) for row in rows]

    except Exception as e:
        raise ValueError(f"Query execution failed: {e}") from e


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate if a SQL query is safe to execute.

    Args:
        sql: SQL query string

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> valid, error = validate_sql("SELECT * FROM users")
        >>> assert valid and not error
        >>> valid, error = validate_sql("DROP TABLE users")
        >>> assert not valid and "dangerous keyword" in error.lower()
    """
    try:
        if not sql or not isinstance(sql, str):
            return False, "SQL query must be a non-empty string"

        clean_sql = sql.strip().rstrip(";")

        if not _SELECT_PATTERN.match(clean_sql):
            return False, "Only SELECT statements are allowed"

        upper_sql = clean_sql.upper()
        for keyword in _DANGEROUS_KEYWORDS:
            # Use word boundaries to avoid matching substrings like "updated_at" containing "UPDATE"
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, upper_sql):
                return False, f"Query contains dangerous keyword: {keyword}"

        return True, ""

    except Exception as e:
        return False, f"Validation error: {e}"
