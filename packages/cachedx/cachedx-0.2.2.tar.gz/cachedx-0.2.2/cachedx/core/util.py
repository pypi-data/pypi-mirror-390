"""Utility functions for cachedx"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any


def sanitize_identifier(name: str) -> str:
    """
    Sanitize a string to be a valid SQL identifier.

    Args:
        name: Input string

    Returns:
        Sanitized identifier safe for SQL

    Examples:
        >>> sanitize_identifier("api/users")
        'api_users'
        >>> sanitize_identifier("user-profiles")
        'user_profiles'
    """
    if not name:
        return "unnamed"

    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r"[^A-Za-z0-9_]", "_", name)

    # Ensure it starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != "_":
        sanitized = f"_{sanitized}"

    # Remove consecutive underscores
    sanitized = re.sub(r"_{2,}", "_", sanitized)

    # Remove trailing underscores
    sanitized = sanitized.rstrip("_")

    return sanitized or "unnamed"


def hash_content(content: bytes | str) -> str:
    """
    Create a hash of content for caching keys.

    Args:
        content: Content to hash

    Returns:
        SHA256 hash (first 16 chars)
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    return hashlib.sha256(content).hexdigest()[:16]


def utc_now() -> datetime:
    """Get current UTC datetime with timezone info"""
    return datetime.now(UTC)


def ensure_timezone(dt: datetime) -> datetime:
    """Ensure datetime has timezone info (assumes UTC if naive)"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def table_name_from_path(path: str, prefix: str = "") -> str:
    """
    Generate a table name from an API path.

    Args:
        path: API endpoint path
        prefix: Optional prefix for the table name

    Returns:
        Safe table name

    Examples:
        >>> table_name_from_path("/api/users")
        'api_users'
        >>> table_name_from_path("/api/forecasts/123", "cached")
        'cached_api_forecasts'
    """
    # Remove leading/trailing slashes and clean up
    clean_path = path.strip("/")

    # Remove query parameters and fragments
    clean_path = clean_path.split("?")[0].split("#")[0]

    # Remove numeric IDs and wildcards from the end
    parts = clean_path.split("/")
    filtered_parts = []

    for part in parts:
        # Skip numeric parts and wildcards
        if not part.isdigit() and part != "*" and part:
            filtered_parts.append(part)

    # Join with underscores and sanitize
    base_name = "_".join(filtered_parts) if filtered_parts else "data"
    table_name = sanitize_identifier(base_name)

    if prefix:
        table_name = f"{sanitize_identifier(prefix)}_{table_name}"

    return table_name


def deep_get(obj: dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get a value from a nested dictionary using a JSONPath-like syntax.

    Args:
        obj: Dictionary to search
        path: Path like "$.user.name" or "user.name"
        default: Default value if path not found

    Returns:
        Value at path or default

    Examples:
        >>> data = {"user": {"name": "Alice", "age": 30}}
        >>> deep_get(data, "$.user.name")
        'Alice'
        >>> deep_get(data, "user.age")
        30
    """
    if not isinstance(obj, dict):
        return default

    # Handle JSONPath syntax
    if path.startswith("$."):
        path = path[2:]

    # Navigate the nested structure
    current = obj
    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current
