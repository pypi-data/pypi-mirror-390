"""Schema inference from JSON responses with intelligent type detection"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..core.util import sanitize_identifier
from .registry import Mapping


class ColumnInfo(BaseModel):
    """Information about an inferred column"""

    name: str = Field(description="Column name")
    sql_type: str = Field(description="SQL data type")
    jsonpath: str = Field(description="JSONPath expression")
    nullable: bool = Field(default=True, description="Whether column can be NULL")
    sample_values: list[Any] = Field(default_factory=list, description="Sample values seen")


class SchemaInferrer:
    """
    Infers database schemas from JSON response data.

    Features:
    - Intelligent type detection (string, integer, float, boolean, timestamp)
    - JSONPath generation for nested objects
    - Column name sanitization
    - Sample value tracking for validation
    - Configurable inference rules

    Examples:
        >>> inferrer = SchemaInferrer()
        >>> data = [{"id": 1, "name": "Alice", "active": True}]
        >>> columns = inferrer.infer_columns(data)
        >>> mapping = inferrer.create_mapping("users", columns)
    """

    def __init__(self, max_samples: int = 100, max_depth: int = 3, array_sample_limit: int = 10):
        """
        Initialize schema inferrer.

        Args:
            max_samples: Maximum objects to sample for inference
            max_depth: Maximum nesting depth to explore
            array_sample_limit: Maximum array items to sample
        """
        self.max_samples = max_samples
        self.max_depth = max_depth
        self.array_sample_limit = array_sample_limit

    def infer_columns(self, data: dict[str, Any] | list[dict[str, Any]]) -> list[ColumnInfo]:
        """
        Infer column information from JSON data.

        Args:
            data: JSON object or array of objects

        Returns:
            List of inferred column information
        """
        # Normalize to list
        if isinstance(data, dict):
            objects = [data]
        elif isinstance(data, list):
            objects = [obj for obj in data if isinstance(obj, dict)][: self.max_samples]
        else:
            return []

        if not objects:
            return []

        # Collect field information across all objects
        field_info: dict[str, dict[str, Any]] = {}

        for obj in objects:
            self._analyze_object(obj, field_info, prefix="", depth=0)

        # Convert to ColumnInfo objects
        columns = []
        for field_path, info in field_info.items():
            column = self._create_column_info(field_path, info)
            if column:
                columns.append(column)

        # Sort by name for consistency
        columns.sort(key=lambda c: c.name)
        return columns

    def _analyze_object(
        self,
        obj: dict[str, Any],
        field_info: dict[str, dict[str, Any]],
        prefix: str = "",
        depth: int = 0,
    ) -> None:
        """Recursively analyze object fields"""
        if depth > self.max_depth:
            return

        for key, value in obj.items():
            field_path = f"{prefix}.{key}" if prefix else key

            # Skip private/meta fields
            if key.startswith("_"):
                continue

            # Initialize field info
            if field_path not in field_info:
                field_info[field_path] = {
                    "types": set(),
                    "values": [],
                    "null_count": 0,
                    "total_count": 0,
                }

            info = field_info[field_path]
            info["total_count"] += 1

            if value is None:
                info["null_count"] += 1
                continue

            # Record type and sample values
            value_type = self._get_value_type(value)
            info["types"].add(value_type)

            if len(info["values"]) < 10:  # Keep sample values
                info["values"].append(value)

            # Recursively analyze nested objects
            if isinstance(value, dict) and depth < self.max_depth:
                self._analyze_object(value, field_info, field_path, depth + 1)
            elif isinstance(value, list) and depth < self.max_depth:
                # Sample array elements
                for i, item in enumerate(value[: self.array_sample_limit]):
                    if isinstance(item, dict):
                        self._analyze_object(item, field_info, f"{field_path}[{i}]", depth + 1)

    def _get_value_type(self, value: Any) -> str:
        """Determine the type category of a value"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            # Try to detect special string types
            if self._looks_like_timestamp(value):
                return "timestamp"
            elif self._looks_like_date(value):
                return "date"
            elif self._looks_like_uuid(value):
                return "uuid"
            else:
                return "string"
        elif isinstance(value, list | dict):
            return "json"
        else:
            return "unknown"

    def _looks_like_timestamp(self, value: str) -> bool:
        """Check if string looks like a timestamp"""
        if not isinstance(value, str) or len(value) < 10:
            return False

        # Common timestamp patterns
        timestamp_indicators = ["T", "Z", "+", "-", ":", "."]

        # Must contain some timestamp-like characters
        has_indicators = any(char in value for char in timestamp_indicators)
        if not has_indicators:
            return False

        # Try parsing common formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ]

        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue

        return False

    def _looks_like_date(self, value: str) -> bool:
        """Check if string looks like a date"""
        if not isinstance(value, str) or len(value) != 10:
            return False

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _looks_like_uuid(self, value: str) -> bool:
        """Check if string looks like a UUID"""
        if not isinstance(value, str) or len(value) != 36:
            return False

        # Simple UUID pattern check
        parts = value.split("-")
        return (
            len(parts) == 5
            and len(parts[0]) == 8
            and len(parts[1]) == 4
            and len(parts[2]) == 4
            and len(parts[3]) == 4
            and len(parts[4]) == 12
            and all(c.isalnum() for part in parts for c in part)
        )

    def _create_column_info(self, field_path: str, info: dict[str, Any]) -> ColumnInfo | None:
        """Create ColumnInfo from field analysis"""
        if not info["types"]:
            return None

        # Determine SQL type from observed types
        types = info["types"]
        sql_type = self._infer_sql_type(types)

        # Generate column name
        column_name = sanitize_identifier(field_path.replace(".", "_"))
        if not column_name:
            return None

        # Generate JSONPath
        jsonpath = f"$.{field_path}" if "." in field_path else f"$.{field_path}"

        # Determine nullability
        # Array element fields must always be nullable since arrays can be empty
        is_array_element = "[" in field_path and "]" in field_path
        nullable = info["null_count"] > 0 or len(types) == 0 or is_array_element

        return ColumnInfo(
            name=column_name,
            sql_type=sql_type,
            jsonpath=jsonpath,
            nullable=nullable,
            sample_values=info["values"][:5],  # Keep first 5 samples
        )

    def _infer_sql_type(self, types: set[str]) -> str:
        """Infer SQL type from observed Python types"""
        if not types:
            return "TEXT"

        # Remove null from consideration for type determination
        non_null_types = types - {"null"}
        if not non_null_types:
            return "TEXT"

        # Single type is easy
        if len(non_null_types) == 1:
            type_name = next(iter(non_null_types))
            return self._type_to_sql(type_name)

        # Multiple types - find common ground
        if "timestamp" in non_null_types:
            return "TIMESTAMP"
        elif "date" in non_null_types:
            return "DATE"
        elif "float" in non_null_types or "integer" in non_null_types and "float" in non_null_types:
            return "DOUBLE"
        elif "integer" in non_null_types:
            return "BIGINT"
        elif "boolean" in non_null_types:
            return "BOOLEAN"
        elif "json" in non_null_types:
            return "JSON"
        else:
            # Default to TEXT for mixed or unknown types
            return "TEXT"

    def _type_to_sql(self, type_name: str) -> str:
        """Convert type name to SQL type"""
        mapping = {
            "string": "TEXT",
            "integer": "BIGINT",
            "float": "DOUBLE",
            "boolean": "BOOLEAN",
            "timestamp": "TIMESTAMP",
            "date": "DATE",
            "uuid": "TEXT",  # Could be UUID type in some databases
            "json": "JSON",
            "null": "TEXT",
            "unknown": "TEXT",
        }
        return mapping.get(type_name, "TEXT")

    def create_mapping(
        self, table_name: str, columns: list[ColumnInfo], id_field: str | None = None
    ) -> Mapping:
        """
        Create a Mapping from inferred columns.

        Args:
            table_name: Target table name
            columns: Inferred column information
            id_field: Primary key field name (auto-detected if None)

        Returns:
            Configured Mapping object
        """
        if not columns:
            raise ValueError("No columns provided")

        # Build column mappings
        column_map = {}
        for col in columns:
            column_map[col.name] = col.jsonpath

        # Detect ID field if not specified
        if id_field is None:
            id_field = self._detect_id_field(columns)

        # Generate DDL
        ddl = self._generate_ddl(table_name, columns, id_field)

        return Mapping(
            table=sanitize_identifier(table_name),
            columns=column_map,
            ddl=ddl,
            id_field=id_field,
            auto_infer=True,
        )

    def _detect_id_field(self, columns: list[ColumnInfo]) -> str:
        """Detect the primary key field from columns"""
        # Look for common ID field names
        id_candidates = ["id", "uuid", "key", "pk"]

        for candidate in id_candidates:
            for col in columns:
                if col.name.lower() == candidate:
                    return col.name

        # Look for fields ending with _id
        for col in columns:
            if col.name.lower().endswith("_id"):
                return col.name

        # Default to first column
        return columns[0].name if columns else "id"

    def _generate_ddl(self, table_name: str, columns: list[ColumnInfo], id_field: str) -> str:
        """Generate CREATE TABLE DDL"""
        col_defs = []

        for col in columns:
            null_constraint = "" if col.nullable else " NOT NULL"
            primary_key = " PRIMARY KEY" if col.name == id_field else ""

            col_def = f"{col.name} {col.sql_type}{null_constraint}{primary_key}"
            col_defs.append(col_def)

        # Add metadata columns
        col_defs.extend(
            [
                "_raw JSON",
                "_fetched_at TIMESTAMP DEFAULT now()",
                "_updated_at TIMESTAMP DEFAULT now()",
            ]
        )

        newline = "\n"
        indent = "  "
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({newline}{indent}{f',{newline}{indent}'.join(col_defs)}{newline})"


def infer_from_response(data: dict[str, Any] | list[dict[str, Any]], table_name: str) -> Mapping:
    """
    Convenience function to infer a mapping from response data.

    Args:
        data: JSON response data
        table_name: Target table name

    Returns:
        Inferred Mapping

    Examples:
        >>> response = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        >>> mapping = infer_from_response(response, "users")
        >>> mapping.table
        'users'
    """
    inferrer = SchemaInferrer()
    columns = inferrer.infer_columns(data)
    return inferrer.create_mapping(table_name, columns)
