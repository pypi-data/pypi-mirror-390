"""Configuration models with comprehensive Pydantic validation"""

from __future__ import annotations

import re
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .exceptions import ConfigurationError


class CacheStrategy(str, Enum):
    """
    Cache strategy for endpoints.

    - STATIC: Cache forever, never expires (good for metadata)
    - CACHED: Cache with TTL, supports ETag revalidation
    - REALTIME: Always fetch, but store responses for querying
    - DISABLED: No caching at all
    """

    STATIC = "static"
    CACHED = "cached"
    REALTIME = "realtime"
    DISABLED = "disabled"


class EndpointConfig(BaseModel):
    """
    Configuration for a specific endpoint pattern with comprehensive validation.

    Examples:
        >>> config = EndpointConfig(
        ...     strategy=CacheStrategy.CACHED,
        ...     ttl=timedelta(minutes=5),
        ...     table_name="users"
        ... )
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Core caching behavior
    strategy: CacheStrategy = Field(
        default=CacheStrategy.CACHED, description="Caching strategy for this endpoint"
    )

    ttl: timedelta | None = Field(
        default_factory=lambda: timedelta(minutes=5), description="Time to live for cached entries"
    )

    # Table/view configuration
    table_name: str | None = Field(
        default=None, description="Custom table name for auto-generated views"
    )

    view_sql: str | None = Field(
        default=None, description="Custom SQL for creating views from cached data"
    )

    # Request behavior
    flatten: bool = Field(default=True, description="Create flattened views for array responses")

    vary_headers: list[str] = Field(
        default_factory=lambda: ["accept-language"],
        description="Headers to include in cache key (for Vary support)",
    )

    # Validation
    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, v: timedelta | None) -> timedelta | None:
        """Validate TTL is positive and reasonable"""
        if v is None:
            return v

        if v.total_seconds() <= 0:
            raise ValueError("TTL must be positive")

        if v.total_seconds() > 86400 * 365:  # 1 year
            raise ValueError("TTL cannot exceed 1 year")

        return v

    @field_validator("table_name")
    @classmethod
    def validate_table_name(cls, v: str | None) -> str | None:
        """Validate table name is a valid SQL identifier"""
        if v is None:
            return v

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
            raise ValueError(
                f"Invalid table name '{v}'. "
                "Must start with letter/underscore, contain only alphanumeric/underscore"
            )

        return v

    @field_validator("view_sql")
    @classmethod
    def validate_view_sql(cls, v: str | None) -> str | None:
        """Validate custom view SQL"""
        if v is None:
            return v

        v_upper = v.upper().strip()

        if not (v_upper.startswith("CREATE") or v_upper.startswith("SELECT")):
            raise ValueError("view_sql must start with CREATE or SELECT")

        # Check for dangerous keywords
        dangerous = ["DROP", "DELETE", "TRUNCATE", "INSERT", "UPDATE"]
        for keyword in dangerous:
            if keyword in v_upper:
                raise ValueError(f"view_sql cannot contain {keyword}")

        return v

    @model_validator(mode="after")
    def validate_strategy_consistency(self) -> Self:
        """Ensure strategy and TTL are consistent"""
        if self.strategy == CacheStrategy.CACHED and self.ttl is None:
            raise ValueError("CACHED strategy requires ttl to be set")

        if self.strategy == CacheStrategy.STATIC and self.ttl is not None:
            # Allow but warn - static doesn't use TTL
            pass

        return self


class CacheConfig(BaseModel):
    """
    Global cache configuration with comprehensive validation.

    Examples:
        >>> config = CacheConfig(
        ...     db_path="./cache.duckdb",
        ...     default_ttl=timedelta(minutes=10),
        ...     endpoints={
        ...         "/api/users": EndpointConfig(strategy=CacheStrategy.CACHED),
        ...         "/api/static/*": EndpointConfig(strategy=CacheStrategy.STATIC)
        ...     }
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    # Endpoint-specific configurations
    endpoints: dict[str, EndpointConfig] = Field(
        default_factory=dict, description="Per-endpoint cache configurations (supports wildcards)"
    )

    # Global defaults
    default_strategy: CacheStrategy = Field(
        default=CacheStrategy.CACHED,
        description="Default strategy for endpoints not explicitly configured",
    )

    default_ttl: timedelta = Field(
        default_factory=lambda: timedelta(minutes=5), description="Default TTL for cached entries"
    )

    # Storage configuration
    db_path: str = Field(default=":memory:", description="DuckDB database path or :memory:")

    # Operational settings
    enable_logging: bool = Field(default=False, description="Enable cache hit/miss logging")

    auto_refresh: bool = Field(
        default=False, description="Enable automatic cache refresh in background"
    )

    refresh_interval: timedelta = Field(
        default_factory=lambda: timedelta(minutes=1), description="Interval for automatic refresh"
    )

    # Validation
    @field_validator("db_path")
    @classmethod
    def validate_db_path(cls, v: str) -> str:
        """Validate database path"""
        if not v:
            raise ValueError("db_path cannot be empty")

        if v != ":memory:":
            # Check if directory is writable (if it exists)
            path = Path(v)
            if path.parent.exists() and not path.parent.is_dir():
                raise ValueError(f"Parent path {path.parent} is not a directory")

        return v

    @field_validator("default_ttl", "refresh_interval")
    @classmethod
    def validate_timedelta(cls, v: timedelta) -> timedelta:
        """Ensure timedelta values are reasonable"""
        if v.total_seconds() <= 0:
            raise ValueError("Time intervals must be positive")

        if v.total_seconds() > 86400 * 30:  # 30 days
            raise ValueError("Time intervals cannot exceed 30 days")

        return v

    @field_validator("endpoints")
    @classmethod
    def validate_endpoint_patterns(cls, v: dict[str, EndpointConfig]) -> dict[str, EndpointConfig]:
        """Validate endpoint patterns"""
        for pattern in v:
            if not pattern.startswith("/"):
                raise ValueError(f"Endpoint pattern '{pattern}' must start with /")

            # Check for valid wildcard usage
            if "**" in pattern:
                raise ValueError(f"Pattern '{pattern}': use single * for wildcards, not **")

        return v

    @model_validator(mode="after")
    def validate_config_consistency(self) -> Self:
        """Validate overall configuration consistency"""
        # If auto_refresh is enabled, ensure refresh_interval is reasonable
        if self.auto_refresh and self.refresh_interval.total_seconds() < 10:
            raise ValueError(
                "refresh_interval should be at least 10 seconds when auto_refresh is enabled"
            )

        return self

    # Methods
    def get(self, path: str) -> EndpointConfig:
        """
        Get configuration for a specific endpoint path.

        Args:
            path: API endpoint path

        Returns:
            EndpointConfig for the path (exact match or wildcard match or default)
        """
        # Try exact match first
        if path in self.endpoints:
            return self.endpoints[path]

        # Try wildcard matches
        for pattern, config in self.endpoints.items():
            if self._matches_pattern(pattern, path):
                return config

        # Return default configuration
        return EndpointConfig(strategy=self.default_strategy, ttl=self.default_ttl)

    def _matches_pattern(self, pattern: str, path: str) -> bool:
        """Check if path matches a wildcard pattern"""
        if not pattern.endswith("*"):
            return False

        prefix = pattern[:-1]
        return path.startswith(prefix)

    def add_endpoint(self, pattern: str, config: EndpointConfig) -> None:
        """
        Add or update an endpoint configuration.

        Args:
            pattern: Endpoint pattern (supports wildcards)
            config: Configuration for the endpoint

        Raises:
            ConfigurationError: If pattern is invalid
        """
        if not pattern.startswith("/"):
            raise ConfigurationError(f"Endpoint pattern '{pattern}' must start with /")

        self.endpoints[pattern] = config

    def remove_endpoint(self, pattern: str) -> EndpointConfig | None:
        """Remove an endpoint configuration"""
        return self.endpoints.pop(pattern, None)

    def list_endpoints(self) -> list[str]:
        """List all configured endpoint patterns"""
        return list(self.endpoints.keys())
