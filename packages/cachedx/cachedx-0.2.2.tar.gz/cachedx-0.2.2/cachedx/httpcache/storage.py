"""HTTP cache storage with Pydantic models"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.duck import con
from ..core.util import ensure_timezone, utc_now
from .exceptions import StorageError


class CachedEntry(BaseModel):
    """
    A cached HTTP response entry with comprehensive validation.

    Examples:
        >>> entry = CachedEntry(
        ...     status=200,
        ...     payload={"users": [{"id": 1, "name": "Alice"}]},
        ...     etag="v1",
        ...     fetched_at=datetime.now(timezone.utc),
        ...     expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)
        ... )
        >>> entry.is_expired()
        False
    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    # Response data
    status: int = Field(description="HTTP status code", ge=100, le=599)

    payload: dict[str, Any] | list[Any] = Field(description="JSON response payload")

    # Cache metadata
    etag: str | None = Field(default=None, description="ETag header value for revalidation")

    fetched_at: datetime = Field(description="When the response was originally fetched")

    expires_at: datetime | None = Field(default=None, description="When the cached entry expires")

    # Validation
    @field_validator("fetched_at", "expires_at")
    @classmethod
    def ensure_timezone_aware(cls, v: datetime | None) -> datetime | None:
        """Ensure datetime has timezone info"""
        if v is None:
            return v
        return ensure_timezone(v)

    @field_validator("status")
    @classmethod
    def validate_status_code(cls, v: int) -> int:
        """Validate HTTP status code is in valid range"""
        if not (100 <= v <= 599):
            raise ValueError(f"Invalid HTTP status code: {v}")
        return v

    # Methods
    def is_expired(self, now: datetime | None = None) -> bool:
        """
        Check if the cached entry has expired.

        Args:
            now: Current time (defaults to utc_now())

        Returns:
            True if expired, False otherwise
        """
        if self.expires_at is None:
            return False  # Never expires

        current_time = now or utc_now()
        return self.expires_at <= current_time

    def time_until_expiry(self, now: datetime | None = None) -> timedelta | None:
        """
        Get time remaining until expiry.

        Args:
            now: Current time (defaults to utc_now())

        Returns:
            Time remaining or None if never expires
        """
        if self.expires_at is None:
            return None

        current_time = now or utc_now()
        remaining = self.expires_at - current_time
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def to_dataframe(self) -> Any:
        """
        Convert payload to pandas DataFrame if possible.

        Returns:
            pandas DataFrame

        Raises:
            ImportError: If pandas is not installed
            ValueError: If payload cannot be converted to DataFrame
        """
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                "pandas is required for DataFrame conversion. "
                "Install with: pip install 'cachedx[pandas]'"
            ) from e

        if isinstance(self.payload, list):
            return pd.DataFrame(self.payload)
        elif isinstance(self.payload, dict):
            return pd.DataFrame([self.payload])
        else:
            raise ValueError(f"Cannot convert {type(self.payload)} to DataFrame")


class CacheStorage:
    """
    Storage backend for HTTP cache entries using DuckDB.

    Manages the _cx_cache table with automatic schema management.
    """

    def __init__(self) -> None:
        """Initialize storage and ensure tables exist"""
        # Tables are created in duck.py during connection setup
        pass

    def get(self, key: str) -> CachedEntry | None:
        """
        Retrieve a cached entry by key.

        Args:
            key: Cache key

        Returns:
            CachedEntry if found, None otherwise

        Raises:
            StorageError: If database operation fails
        """
        try:
            result = (
                con()
                .execute(
                    """
                SELECT status, etag, fetched_at, expires_at, payload
                FROM _cx_cache
                WHERE key = ?
                """,
                    [key],
                )
                .fetchone()
            )

            if not result:
                return None

            status, etag, fetched_at, expires_at, payload = result

            # Parse JSON payload
            if isinstance(payload, str):
                payload = json.loads(payload)

            return CachedEntry(
                status=status,
                etag=etag,
                fetched_at=fetched_at,
                expires_at=expires_at,
                payload=payload,
            )

        except Exception as e:
            raise StorageError(f"Failed to retrieve cache entry: {e}") from e

    def set(
        self,
        key: str,
        method: str,
        path: str,
        params: dict[str, Any] | None,
        headers: dict[str, str] | None,
        status: int,
        payload: Any,
        etag: str | None,
        ttl: timedelta | None,
    ) -> None:
        """
        Store a cache entry.

        Args:
            key: Cache key
            method: HTTP method
            path: Request path
            params: Query parameters
            headers: Request headers
            status: HTTP status code
            payload: Response payload
            etag: ETag header value
            ttl: Time to live

        Raises:
            StorageError: If database operation fails
        """
        try:
            now = utc_now()
            expires_at = now + ttl if ttl else None

            con().execute(
                """
                INSERT OR REPLACE INTO _cx_cache(
                    key, method, path, params, headers, status, etag,
                    fetched_at, expires_at, payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?::JSON)
                """,
                [
                    key,
                    method,
                    path,
                    json.dumps(params, sort_keys=True) if params else None,
                    json.dumps(headers, sort_keys=True) if headers else None,
                    status,
                    etag,
                    now,
                    expires_at,
                    json.dumps(payload) if not isinstance(payload, str) else payload,
                ],
            )

        except Exception as e:
            raise StorageError(f"Failed to store cache entry: {e}") from e

    def renew(self, key: str, ttl: timedelta | None) -> bool:
        """
        Renew the expiry time of a cached entry.

        Args:
            key: Cache key
            ttl: New time to live

        Returns:
            True if entry was renewed, False if not found

        Raises:
            StorageError: If database operation fails
        """
        try:
            # First check if entry exists
            exists = (
                con().execute("SELECT 1 FROM _cx_cache WHERE key = ? LIMIT 1", [key]).fetchone()
            )

            if not exists:
                return False

            if ttl is None:
                # Remove expiry (make it never expire)
                con().execute("UPDATE _cx_cache SET expires_at = NULL WHERE key = ?", [key])
            else:
                # Set new expiry time
                new_expiry = utc_now() + ttl
                con().execute(
                    "UPDATE _cx_cache SET expires_at = ? WHERE key = ?", [new_expiry, key]
                )

            return True

        except Exception as e:
            raise StorageError(f"Failed to renew cache entry: {e}") from e

    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found

        Raises:
            StorageError: If database operation fails
        """
        try:
            result = con().execute("DELETE FROM _cx_cache WHERE key = ?", [key])
            return bool(result.rowcount > 0)

        except Exception as e:
            raise StorageError(f"Failed to delete cache entry: {e}") from e

    def clear_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed

        Raises:
            StorageError: If database operation fails
        """
        try:
            result = con().execute(
                "DELETE FROM _cx_cache WHERE expires_at IS NOT NULL AND expires_at <= ?",
                [utc_now()],
            )
            return int(result.rowcount) if result.rowcount is not None else 0

        except Exception as e:
            raise StorageError(f"Failed to clear expired entries: {e}") from e

    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics

        Raises:
            StorageError: If database operation fails
        """
        try:
            # Total entries
            total_result = con().execute("SELECT COUNT(*) FROM _cx_cache").fetchone()
            total = total_result[0] if total_result else 0

            # Expired entries
            expired_result = (
                con()
                .execute(
                    "SELECT COUNT(*) FROM _cx_cache WHERE expires_at IS NOT NULL AND expires_at <= ?",
                    [utc_now()],
                )
                .fetchone()
            )
            expired = expired_result[0] if expired_result else 0

            # Paths
            paths_result = con().execute("SELECT COUNT(DISTINCT path) FROM _cx_cache").fetchone()
            unique_paths = paths_result[0] if paths_result else 0

            return {
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired,
                "unique_paths": unique_paths,
            }

        except Exception as e:
            raise StorageError(f"Failed to get cache statistics: {e}") from e
