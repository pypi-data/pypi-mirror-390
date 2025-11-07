"""Data normalization and storage operations"""

from __future__ import annotations

import json
from typing import Any

import orjson

from ..core.duck import con
from ..core.util import hash_content, utc_now


def save_raw(resource: str, key: str, obj: dict[str, Any]) -> None:
    """
    Save raw JSON object to the cx_raw table for provenance.

    Args:
        resource: Resource name/type
        key: Unique identifier for the object
        obj: JSON object to store

    Examples:
        >>> save_raw("users", "123", {"id": 123, "name": "Alice"})
    """
    try:
        # Serialize with orjson for consistency and performance
        json_data = orjson.dumps(obj).decode("utf-8")

        con().execute(
            """
            INSERT OR REPLACE INTO cx_raw(key, resource, payload, fetched_at)
            VALUES (?, ?, ?::JSON, ?)
            """,
            [f"{resource}:{key}", resource, json_data, utc_now()],
        )

    except Exception as e:
        raise ValueError(f"Failed to save raw data for {resource}:{key}: {e}") from e


def upsert_from_obj(
    resource: str, obj: dict[str, Any], columns: dict[str, str], table: str, id_field: str = "id"
) -> None:
    """
    Upsert normalized data from JSON object into target table.

    Args:
        resource: Resource name (for raw storage key)
        obj: JSON object to normalize
        columns: Column mappings (name -> JSONPath/expression)
        table: Target table name
        id_field: Primary key field name

    Examples:
        >>> columns = {"id": "$.id", "name": "$.name", "email": "$.email"}
        >>> upsert_from_obj("users", {"id": 1, "name": "Alice"}, columns, "users")
    """
    if not obj or not columns:
        return

    try:
        # Extract primary key value
        id_value = _extract_value(obj, columns.get(id_field, "$.id"))
        if id_value is None:
            # Generate key from object hash if no ID
            id_value = hash_content(orjson.dumps(obj))

        # Save raw data for provenance
        save_raw(resource, str(id_value), obj)

        # Extract values for all columns
        values = {}
        for col_name, expression in columns.items():
            values[col_name] = _extract_value(obj, expression)

        # Add metadata
        values["_raw"] = obj
        values["_updated_at"] = utc_now()

        # Build upsert SQL
        col_names = list(values.keys())
        placeholders = ", ".join("?" * len(col_names))

        # ON CONFLICT clause for all non-key columns
        update_cols = [col for col in col_names if col != id_field]
        update_clause = ", ".join(f"{col} = excluded.{col}" for col in update_cols)

        sql = f"""
        INSERT INTO {table} ({", ".join(col_names)})
        VALUES ({placeholders})
        ON CONFLICT ({id_field}) DO UPDATE SET {update_clause}
        """  # nosec B608

        # Execute with JSON serialization for complex types
        serialized_values = []
        for col_name in col_names:
            value = values[col_name]
            if isinstance(value, dict | list):
                serialized_values.append(json.dumps(value))
            else:
                serialized_values.append(value)

        con().execute(sql, serialized_values)

    except Exception as e:
        raise ValueError(f"Failed to upsert data to {table}: {e}") from e


def upsert_batch(
    resource: str,
    objects: list[dict[str, Any]],
    columns: dict[str, str],
    table: str,
    id_field: str = "id",
) -> int:
    """
    Batch upsert multiple objects for better performance.

    Args:
        resource: Resource name
        objects: List of JSON objects
        columns: Column mappings
        table: Target table name
        id_field: Primary key field name

    Returns:
        Number of objects processed

    Examples:
        >>> objects = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        >>> count = upsert_batch("users", objects, {"id": "$.id", "name": "$.name"}, "users")
    """
    if not objects:
        return 0

    try:
        processed = 0

        # Process in smaller chunks to avoid memory issues
        chunk_size = 100
        for i in range(0, len(objects), chunk_size):
            chunk = objects[i : i + chunk_size]

            # Prepare batch data
            batch_values = []
            for obj in chunk:
                if not isinstance(obj, dict):
                    continue

                # Extract values for this object
                row_values = {}
                for col_name, expression in columns.items():
                    row_values[col_name] = _extract_value(obj, expression)

                # Add metadata
                row_values["_raw"] = obj
                row_values["_updated_at"] = utc_now()

                # Save raw data
                id_value = row_values.get(id_field) or hash_content(orjson.dumps(obj))
                save_raw(resource, str(id_value), obj)

                batch_values.append(row_values)
                processed += 1

            if batch_values:
                _execute_batch_upsert(batch_values, table, id_field)

        return processed

    except Exception as e:
        raise ValueError(f"Failed to batch upsert to {table}: {e}") from e


def _execute_batch_upsert(batch_values: list[dict[str, Any]], table: str, id_field: str) -> None:
    """Execute batch upsert using DuckDB's INSERT ... ON CONFLICT"""
    if not batch_values:
        return

    # Get column names from first row
    col_names = list(batch_values[0].keys())

    # Build SQL
    placeholders = ", ".join("?" * len(col_names))
    update_cols = [col for col in col_names if col != id_field]
    update_clause = ", ".join(f"{col} = excluded.{col}" for col in update_cols)

    sql = f"""
    INSERT INTO {table} ({", ".join(col_names)})
    VALUES ({placeholders})
    ON CONFLICT ({id_field}) DO UPDATE SET {update_clause}
    """  # nosec B608

    # Execute for each row (DuckDB doesn't support batch parameters yet)
    for row in batch_values:
        serialized_values = []
        for col_name in col_names:
            value = row[col_name]
            if isinstance(value, dict | list):
                serialized_values.append(json.dumps(value))
            else:
                serialized_values.append(value)

        con().execute(sql, serialized_values)


def _extract_value(obj: dict[str, Any], expression: str) -> Any:
    """
    Extract value from JSON object using expression.

    Args:
        obj: JSON object
        expression: JSONPath or SQL expression

    Returns:
        Extracted value or None
    """
    if not expression:
        return None

    try:
        # Handle JSONPath expressions
        if expression.startswith("$."):
            return _extract_jsonpath(obj, expression[2:])

        # Handle DuckDB JSON extraction syntax
        if "->>" in expression and expression.startswith("j->>"):
            field = expression.split("'")[1] if "'" in expression else None
            return obj.get(field) if field else None

        # Handle CAST expressions
        if expression.upper().startswith("CAST("):
            # Extract the inner expression
            inner = expression[5:].split(" AS ")[0].strip()
            if inner.startswith("j->>"):
                field = inner.split("'")[1] if "'" in inner else None
                value = obj.get(field) if field else None

                # Simple type conversion based on CAST target
                if "TIMESTAMP" in expression.upper():
                    return _convert_to_timestamp(value)
                elif "INTEGER" in expression.upper():
                    return _convert_to_int(value)
                elif "DOUBLE" in expression.upper():
                    return _convert_to_float(value)

                return value

        # Direct field access
        return obj.get(expression)

    except Exception:
        return None


def _extract_jsonpath(obj: dict[str, Any], path: str) -> Any:
    """Extract value using JSONPath-like navigation"""
    current = obj

    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None

    return current


def _convert_to_timestamp(value: Any) -> str | None:
    """Convert value to timestamp string"""
    if value is None:
        return None

    if isinstance(value, str):
        # Try to parse and reformat for consistency
        try:
            # Just return as-is for now - DuckDB is good at parsing
            return value
        except Exception:
            return None

    return str(value)


def _convert_to_int(value: Any) -> int | None:
    """Convert value to integer"""
    if value is None:
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _convert_to_float(value: Any) -> float | None:
    """Convert value to float"""
    if value is None:
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None
