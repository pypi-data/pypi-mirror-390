"""HTTP client with intelligent caching and view generation"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from typing import Any

import httpx

from ..core.duck import con
from ..core.util import table_name_from_path
from .config import CacheConfig, CacheStrategy
from .exceptions import CacheError
from .key import signature
from .storage import CacheStorage

logger = logging.getLogger(__name__)


class CachedClient(httpx.AsyncClient):
    """
    An httpx.AsyncClient with intelligent caching and automatic view generation.

    Features:
    - TTL-based caching with ETag/304 revalidation
    - Automatic view creation from JSON responses
    - Configurable per-endpoint caching strategies
    - Write-through caching for consistency
    - Background refresh support

    Examples:
        >>> config = CacheConfig(
        ...     endpoints={"/api/users": EndpointConfig(strategy=CacheStrategy.CACHED)}
        ... )
        >>> async with CachedClient(base_url="https://api.example.com", cache_config=config) as client:
        ...     response = await client.get("/api/users")  # Cache miss
        ...     response = await client.get("/api/users")  # Cache hit or 304
        ...     df = client.query("SELECT * FROM api_users LIMIT 10")
    """

    def __init__(self, *args: Any, cache_config: CacheConfig | None = None, **kwargs: Any) -> None:
        """
        Initialize CachedClient.

        Args:
            cache_config: Cache configuration (uses defaults if None)
            *args, **kwargs: Passed to httpx.AsyncClient
        """
        super().__init__(*args, **kwargs)

        self.cache_config = cache_config or CacheConfig()
        self.storage = CacheStorage()
        self._refresh_task: asyncio.Task[None] | None = None

        # Initialize database connection
        from ..core.duck import connect

        connect(self.cache_config.db_path)

        # Start auto-refresh if enabled
        if self.cache_config.auto_refresh:
            self._start_refresh_task()

    async def request(self, method: str, url: httpx.URL | str, **kwargs: Any) -> httpx.Response:
        """
        Make an HTTP request with caching.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            httpx.Response (may be from cache)
        """
        # Extract build_request parameters from kwargs
        build_params = {}
        request_params = {}

        build_request_args = {
            "content",
            "data",
            "files",
            "json",
            "params",
            "headers",
            "cookies",
            "timeout",
            "extensions",
        }

        for key, value in kwargs.items():
            if key in build_request_args:
                build_params[key] = value
            else:
                request_params[key] = value

        # Build request to get normalized components
        request = self.build_request(method, url, **build_params)
        path = request.url.raw_path.decode()

        # Get endpoint configuration
        endpoint_config = self.cache_config.get(path)

        # Generate cache key
        cache_key = signature(
            method=request.method,
            path=path,
            params=dict(request.url.params),
            headers=dict(request.headers),
            body=request.content,
            vary_headers=endpoint_config.vary_headers,
        )

        # Handle non-GET requests (writes)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            return await self._handle_write_request(
                request, endpoint_config, cache_key, **request_params
            )

        # Handle GET requests (reads)
        return await self._handle_read_request(
            request, endpoint_config, cache_key, **request_params
        )

    async def _handle_read_request(
        self, request: httpx.Request, endpoint_config: Any, cache_key: str, **kwargs: Any
    ) -> httpx.Response:
        """Handle GET requests with caching logic"""
        path = request.url.raw_path.decode()

        # Check if caching is disabled
        if endpoint_config.strategy == CacheStrategy.DISABLED:
            response = await super().send(request, **kwargs)
            self._log_cache_event("DISABLED", request.method, path)
            return response

        # Try to get from cache
        cached_entry = self.storage.get(cache_key)

        # Handle STATIC strategy
        if (
            endpoint_config.strategy == CacheStrategy.STATIC
            and cached_entry
            and not cached_entry.is_expired()
        ):
            self._log_cache_event("HIT", request.method, path)
            return self._response_from_cache(request, cached_entry)

        # Handle CACHED strategy with conditional requests
        if (
            cached_entry
            and endpoint_config.strategy == CacheStrategy.CACHED
            and not cached_entry.is_expired()
        ):
            # Try conditional GET with ETag
            if cached_entry.etag:
                request.headers["If-None-Match"] = cached_entry.etag

            try:
                response = await super().send(request, **kwargs)

                if response.status_code == 304:
                    # Not modified - renew cache and return cached version
                    self.storage.renew(cache_key, endpoint_config.ttl)
                    self._log_cache_event("REVALIDATED", request.method, path)
                    return self._response_from_cache(request, cached_entry, dict(response.headers))
                else:
                    # Modified - store new response
                    await self._store_response(response, request, endpoint_config, cache_key)
                    self._log_cache_event("MISS", request.method, path)
                    return response

            except Exception as e:
                # On network error, return cached version if available
                logger.warning(f"Network error for {path}, using cached version: {e}")
                self._log_cache_event("ERROR_FALLBACK", request.method, path)
                return self._response_from_cache(request, cached_entry)

            else:
                # No ETag - serve from cache
                self._log_cache_event("HIT", request.method, path)
                return self._response_from_cache(request, cached_entry)

        # Cache miss or REALTIME strategy - fetch from origin
        try:
            response = await super().send(request, **kwargs)

            # Store response if cacheable
            if response.status_code < 400:
                await self._store_response(response, request, endpoint_config, cache_key)

            cache_event = "MISS" if cached_entry else "MISS"
            self._log_cache_event(cache_event, request.method, path)
            return response

        except Exception as e:
            # On error, try to serve stale cache
            if cached_entry:
                logger.warning(f"Network error for {path}, serving stale cache: {e}")
                self._log_cache_event("STALE_FALLBACK", request.method, path)
                return self._response_from_cache(request, cached_entry)
            raise

    async def _handle_write_request(
        self, request: httpx.Request, endpoint_config: Any, cache_key: str, **kwargs: Any
    ) -> httpx.Response:
        """Handle POST/PUT/PATCH/DELETE requests with write-through caching"""
        path = request.url.raw_path.decode()

        # Always execute the write operation
        response = await super().send(request, **kwargs)

        # For successful writes, implement write-through caching
        if response.status_code < 400 and endpoint_config.strategy != CacheStrategy.DISABLED:
            try:
                await self._store_response(response, request, endpoint_config, cache_key)
                self._log_cache_event("WRITE_THROUGH", request.method, path)
            except Exception as e:
                logger.warning(f"Failed to store write-through cache for {path}: {e}")

        return response

    async def _store_response(
        self, response: httpx.Response, request: httpx.Request, endpoint_config: Any, cache_key: str
    ) -> None:
        """Store response in cache and create views"""
        path = request.url.raw_path.decode()

        try:
            # Parse JSON payload
            payload = response.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Not JSON - skip caching
            return

        # Store in cache
        self.storage.set(
            key=cache_key,
            method=request.method,
            path=path,
            params=dict(request.url.params),
            headers=dict(request.headers),
            status=response.status_code,
            payload=payload,
            etag=response.headers.get("etag"),
            ttl=endpoint_config.ttl,
        )

        # Create view if flattening is enabled
        if endpoint_config.flatten:
            await self._ensure_view(path, endpoint_config.table_name, payload)

    def _response_from_cache(
        self,
        request: httpx.Request,
        cached_entry: Any,
        additional_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Create an httpx.Response from cached data"""
        # Serialize payload
        content = json.dumps(cached_entry.payload).encode("utf-8")

        # Build response headers
        headers = {
            "content-type": "application/json",
            "x-cachedx": "HIT",
        }

        if cached_entry.etag:
            headers["etag"] = cached_entry.etag

        if additional_headers:
            headers.update({k.lower(): v for k, v in additional_headers.items()})

        return httpx.Response(
            status_code=cached_entry.status, headers=headers, content=content, request=request
        )

    async def _ensure_view(self, path: str, custom_table_name: str | None, payload: Any) -> str:
        """Create or update a view for the cached response data"""
        table_name = custom_table_name or table_name_from_path(path)

        try:
            # Create view SQL - simplified for better compatibility
            path_escaped = path.replace("'", "''")
            view_sql = f"""
            CREATE OR REPLACE VIEW {table_name} AS
            SELECT 1 as _idx, payload as _raw
            FROM _cx_cache
            WHERE path = '{path_escaped}' AND method = 'GET'
            ORDER BY fetched_at DESC
            LIMIT 1
            """  # nosec B608

            con().execute(view_sql)

            if self.cache_config.enable_logging:
                logger.info(f"Created/updated view: {table_name}")

            return table_name

        except Exception as e:
            logger.warning(f"Failed to create view {table_name} for {path}: {e}")
            raise CacheError(f"View creation failed: {e}") from e

    def query(self, sql: str, params: list[Any] | None = None) -> Any:
        """
        Execute a SQL query against cached data.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            pandas DataFrame if available, otherwise list of dicts
        """
        try:
            cursor = con().execute(sql, params or [])

            # Try to return pandas DataFrame
            try:
                import pandas  # noqa: F401

                return cursor.df()
            except ImportError:
                # Fall back to list of dicts
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row, strict=False)) for row in rows]

        except Exception as e:
            raise CacheError(f"Query execution failed: {e}") from e

    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        try:
            base_stats = self.storage.stats()

            # Add view information
            views_result = (
                con()
                .execute(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_type = 'VIEW' AND table_schema = 'main'
                """
                )
                .fetchall()
            )

            views = [row[0] for row in views_result]
            base_stats["views"] = views
            base_stats["view_count"] = len(views)

            return base_stats

        except Exception as e:
            logger.warning(f"Failed to get cache statistics: {e}")
            return {"error": str(e)}

    def clear_cache(self, pattern: str | None = None) -> int:
        """
        Clear cache entries.

        Args:
            pattern: Optional path pattern to match (SQL LIKE pattern)

        Returns:
            Number of entries removed
        """
        try:
            if pattern:
                result = con().execute("DELETE FROM _cx_cache WHERE path LIKE ?", [pattern])
            else:
                result = con().execute("DELETE FROM _cx_cache")

            return int(result.rowcount) if result.rowcount is not None else 0

        except Exception as e:
            raise CacheError(f"Cache clearing failed: {e}") from e

    def _log_cache_event(self, event: str, method: str, path: str) -> None:
        """Log cache events if logging is enabled"""
        if self.cache_config.enable_logging:
            logger.info(f"Cache {event}: {method} {path}")

    def _start_refresh_task(self) -> None:
        """Start background refresh task"""
        if self._refresh_task is None:
            self._refresh_task = asyncio.create_task(self._refresh_loop())

    async def _refresh_loop(self) -> None:
        """Background refresh loop"""
        while True:
            try:
                await asyncio.sleep(self.cache_config.refresh_interval.total_seconds())
                # TODO: Implement smart refresh logic
                self.storage.clear_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Refresh loop error: {e}")

    async def aclose(self) -> None:
        """Clean shutdown"""
        if self._refresh_task:
            self._refresh_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._refresh_task

        await super().aclose()
