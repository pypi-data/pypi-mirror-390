"""Schema registry for resource mappings with comprehensive validation"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.duck import con
from ..core.util import sanitize_identifier

_registry: dict[str, Mapping] = {}


class Mapping(BaseModel):
    """
    Resource mapping configuration with comprehensive validation.

    Defines how JSON responses should be stored in normalized tables.

    Examples:
        >>> mapping = Mapping(
        ...     table="users",
        ...     columns={
        ...         "id": "$.id",
        ...         "name": "$.name",
        ...         "email": "$.email",
        ...         "created_at": "CAST(j->>'created_at' AS TIMESTAMP)"
        ...     },
        ...     ddl="CREATE TABLE users(id TEXT PRIMARY KEY, name TEXT, email TEXT, created_at TIMESTAMP)"
        ... )
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core configuration
    table: str = Field(description="Target DuckDB table name", min_length=1)

    columns: dict[str, str] = Field(
        description="Column mappings: name -> JSONPath or SQL expression using alias 'j'"
    )

    ddl: str | None = Field(default=None, description="Optional DDL statement for table creation")

    # Inference options
    auto_infer: bool = Field(
        default=True, description="Auto-infer missing columns from response data"
    )

    id_field: str = Field(default="id", description="Primary key field name", min_length=1)

    # Validation
    @field_validator("table")
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        """Validate and sanitize table name"""
        sanitized = sanitize_identifier(v)
        if not sanitized or sanitized != v:
            raise ValueError(
                f"Invalid table name '{v}'. "
                "Must be a valid SQL identifier (letters, numbers, underscores)"
            )
        return sanitized

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate column mappings"""
        if not v:
            raise ValueError("columns mapping cannot be empty")

        for col_name, expression in v.items():
            # Validate column name
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", col_name):
                raise ValueError(
                    f"Invalid column name '{col_name}'. "
                    "Must start with letter/underscore, contain only alphanumeric/underscore"
                )

            # Validate expression is not empty
            if not expression.strip():
                raise ValueError(f"Expression for column '{col_name}' cannot be empty")

        return v

    @field_validator("ddl")
    @classmethod
    def validate_ddl(cls, v: str | None) -> str | None:
        """Validate DDL statement"""
        if v is None:
            return v

        v_upper = v.upper().strip()

        if not v_upper.startswith("CREATE TABLE"):
            raise ValueError("DDL must start with CREATE TABLE")

        # Check for dangerous keywords
        dangerous = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
        for keyword in dangerous:
            if keyword in v_upper:
                raise ValueError(f"DDL cannot contain dangerous keyword: {keyword}")

        return v

    @field_validator("id_field")
    @classmethod
    def validate_id_field(cls, v: str) -> str:
        """Validate ID field name"""
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
            raise ValueError(f"Invalid id_field '{v}'. Must be a valid column name")
        return v

    # Methods
    def ensure_table(self) -> None:
        """
        Ensure the target table exists, creating it if necessary.

        Raises:
            ValueError: If table creation fails
        """
        if self.ddl:
            try:
                con().execute(self.ddl)
            except Exception as e:
                raise ValueError(f"Failed to execute DDL: {e}") from e
        else:
            # Auto-generate basic table structure
            self._create_auto_table()

    def _create_auto_table(self) -> None:
        """Create table with auto-inferred structure"""
        # Generate column definitions from mappings
        col_defs = []

        for col_name in self.columns:
            if col_name == self.id_field:
                col_defs.append(f"{col_name} TEXT PRIMARY KEY")
            else:
                # Default to TEXT for simplicity
                col_defs.append(f"{col_name} TEXT")

        # Add metadata columns
        col_defs.extend(
            [
                "_raw JSON",  # Store original JSON
                "_fetched_at TIMESTAMP DEFAULT now()",
                "_updated_at TIMESTAMP DEFAULT now()",
            ]
        )

        ddl = f"CREATE TABLE IF NOT EXISTS {self.table} ({', '.join(col_defs)})"

        try:
            con().execute(ddl)
        except Exception as e:
            raise ValueError(f"Failed to auto-create table {self.table}: {e}") from e

    def extract_values(self, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Extract column values from a JSON object using the defined mappings.

        Args:
            obj: JSON object to extract from

        Returns:
            Dictionary of column_name -> extracted_value
        """
        values = {}

        for col_name, expression in self.columns.items():
            try:
                value = self._evaluate_expression(expression, obj)
                values[col_name] = value
            except Exception:
                # On error, set to None
                values[col_name] = None

        # Always include raw JSON and timestamps
        values["_raw"] = obj

        return values

    def _evaluate_expression(self, expression: str, obj: dict[str, Any]) -> Any:
        """
        Evaluate a column expression against a JSON object.

        Args:
            expression: JSONPath or SQL expression
            obj: JSON object

        Returns:
            Extracted value
        """
        # Handle JSONPath expressions
        if expression.startswith("$."):
            return self._extract_jsonpath(expression, obj)

        # Handle SQL expressions with 'j' alias
        if "j" in expression:
            # This would need SQL execution context - simplified for now
            parts = expression.split("'")
            if len(parts) > 1:
                field = parts[1]  # Extract field from j->>'field'
                return self._extract_jsonpath(f"$.{field}", obj)
            return None

        # Direct field access
        return obj.get(expression)

    def _extract_jsonpath(self, path: str, obj: dict[str, Any]) -> Any:
        """
        Extract value using JSONPath-like syntax.

        Args:
            path: JSONPath like "$.user.name"
            obj: JSON object

        Returns:
            Extracted value or None
        """
        if not path.startswith("$."):
            return obj.get(path)

        # Navigate the nested structure
        current = obj
        for key in path[2:].split("."):
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current


def register(resource: str, mapping: Mapping) -> None:
    """
    Register a resource mapping.

    Args:
        resource: Resource name (must be valid identifier)
        mapping: Mapping configuration

    Raises:
        ValueError: If resource name is invalid or already registered
    """
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", resource):
        raise ValueError(f"Invalid resource name '{resource}'. Must be a valid identifier")

    if resource in _registry:
        raise ValueError(f"Resource '{resource}' is already registered")

    # Ensure table exists
    mapping.ensure_table()

    # Register the mapping
    _registry[resource] = mapping


def get(resource: str) -> Mapping | None:
    """
    Get a registered mapping.

    Args:
        resource: Resource name

    Returns:
        Mapping if found, None otherwise
    """
    return _registry.get(resource)


def get_required(resource: str) -> Mapping:
    """
    Get a registered mapping, raising error if not found.

    Args:
        resource: Resource name

    Returns:
        Mapping

    Raises:
        ValueError: If resource not found
    """
    mapping = _registry.get(resource)
    if mapping is None:
        raise ValueError(f"Resource '{resource}' is not registered")
    return mapping


def unregister(resource: str) -> Mapping | None:
    """
    Unregister a resource mapping.

    Args:
        resource: Resource name

    Returns:
        Unregistered mapping or None if not found
    """
    return _registry.pop(resource, None)


def list_resources() -> list[str]:
    """
    List all registered resource names.

    Returns:
        List of resource names
    """
    return list(_registry.keys())


def clear_registry() -> None:
    """Clear all registered mappings (mainly for testing)"""
    global _registry
    _registry.clear()
