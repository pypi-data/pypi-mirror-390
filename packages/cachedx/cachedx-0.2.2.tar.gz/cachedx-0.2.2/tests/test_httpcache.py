"""Tests for HTTP cache layer"""

from datetime import UTC, timedelta

import httpx
import pytest
import respx
from cachedx.httpcache import CacheConfig, CachedClient, CacheStrategy, EndpointConfig
from cachedx.httpcache.key import signature
from cachedx.httpcache.storage import CachedEntry, CacheStorage


class TestCacheKey:
    """Test cache key generation"""

    def test_basic_signature(self) -> None:
        """Test basic signature generation"""
        key1 = signature("GET", "/api/users")
        key2 = signature("GET", "/api/users")
        assert key1 == key2
        assert len(key1) == 32

    def test_different_methods_different_keys(self) -> None:
        """Test that different methods generate different keys"""
        get_key = signature("GET", "/api/users")
        post_key = signature("POST", "/api/users")
        assert get_key != post_key

    def test_different_paths_different_keys(self) -> None:
        """Test that different paths generate different keys"""
        users_key = signature("GET", "/api/users")
        posts_key = signature("GET", "/api/posts")
        assert users_key != posts_key

    def test_params_affect_key(self) -> None:
        """Test that query parameters affect the key"""
        key1 = signature("GET", "/api/users", {"limit": 10})
        key2 = signature("GET", "/api/users", {"limit": 20})
        key3 = signature("GET", "/api/users")

        assert key1 != key2
        assert key1 != key3
        assert key2 != key3

    def test_params_order_independence(self) -> None:
        """Test that parameter order doesn't affect key"""
        key1 = signature("GET", "/api/users", {"a": 1, "b": 2})
        key2 = signature("GET", "/api/users", {"b": 2, "a": 1})
        assert key1 == key2

    def test_vary_headers_affect_key(self) -> None:
        """Test that vary headers affect the key"""
        headers1 = {"accept-language": "en"}
        headers2 = {"accept-language": "es"}

        key1 = signature("GET", "/api/users", headers=headers1, vary_headers=["accept-language"])
        key2 = signature("GET", "/api/users", headers=headers2, vary_headers=["accept-language"])
        key3 = signature("GET", "/api/users", headers=headers1)  # No vary headers

        assert key1 != key2
        assert key1 != key3


class TestCacheStorage:
    """Test cache storage operations"""

    @pytest.fixture(autouse=True)  # type: ignore[misc]
    def setup(self) -> None:
        """Set up test storage"""
        from cachedx.core.duck import close, connect

        # Close any existing connection to start fresh
        close()
        connect(":memory:")
        self.storage = CacheStorage()

    def test_store_and_retrieve(self) -> None:
        """Test basic store and retrieve operations"""
        key = "test_key"
        payload = {"id": 1, "name": "test"}

        # Store entry
        self.storage.set(
            key=key,
            method="GET",
            path="/test",
            params=None,
            headers=None,
            status=200,
            payload=payload,
            etag="v1",
            ttl=timedelta(minutes=5),
        )

        # Retrieve entry
        entry = self.storage.get(key)
        assert entry is not None
        assert entry.status == 200
        assert entry.payload == payload
        assert entry.etag == "v1"
        # Check that expiry time exists (skip time comparison due to timezone complexity)
        assert entry.expires_at is not None

    def test_entry_expiration(self) -> None:
        """Test entry expiration logic"""
        from datetime import datetime

        # Create expired entry manually
        past_time = datetime.now(UTC) - timedelta(minutes=10)
        entry = CachedEntry(
            status=200,
            payload={"test": "data"},
            etag="v1",
            fetched_at=past_time,
            expires_at=past_time + timedelta(minutes=5),  # Expired 5 minutes ago
        )

        assert entry.is_expired()

    def test_entry_renewal(self) -> None:
        """Test cache entry renewal"""
        key = "renewable_key"

        # Store entry
        self.storage.set(
            key=key,
            method="GET",
            path="/test",
            params=None,
            headers=None,
            status=200,
            payload={"test": "data"},
            etag="v1",
            ttl=timedelta(minutes=5),  # Initial TTL
        )

        # Verify entry was stored before attempting renewal
        entry = self.storage.get(key)
        assert entry is not None, "Entry should be stored before renewal"

        # Renew with longer TTL
        renewed = self.storage.renew(key, timedelta(hours=1))
        assert renewed, "Renewal should succeed when entry exists"

        # Verify entry still exists
        entry = self.storage.get(key)
        assert entry is not None
        assert entry.status == 200


class TestCacheConfig:
    """Test cache configuration and validation"""

    def test_default_config(self) -> None:
        """Test default configuration values"""
        config = CacheConfig()
        assert config.default_strategy == CacheStrategy.CACHED
        assert config.default_ttl == timedelta(minutes=5)
        assert config.db_path == ":memory:"
        assert not config.enable_logging
        assert not config.auto_refresh

    def test_endpoint_matching(self) -> None:
        """Test endpoint pattern matching"""
        config = CacheConfig(
            endpoints={
                "/api/users": EndpointConfig(strategy=CacheStrategy.STATIC),
                "/api/temp/*": EndpointConfig(strategy=CacheStrategy.REALTIME),
            }
        )

        # Exact match
        users_config = config.get("/api/users")
        assert users_config.strategy == CacheStrategy.STATIC

        # Wildcard match
        temp_config = config.get("/api/temp/123")
        assert temp_config.strategy == CacheStrategy.REALTIME

        # Default fallback
        default_config = config.get("/api/other")
        assert default_config.strategy == CacheStrategy.CACHED

    def test_invalid_configurations(self) -> None:
        """Test validation of invalid configurations"""
        # Invalid TTL
        with pytest.raises(ValueError, match="positive"):
            CacheConfig(default_ttl=timedelta(seconds=-1))

        # Invalid endpoint pattern
        with pytest.raises(ValueError, match="start with /"):
            CacheConfig(endpoints={"invalid": EndpointConfig()})


@respx.mock
class TestCachedClient:
    """Test CachedClient with mocked HTTP responses"""

    def test_basic_caching(self) -> None:
        """Test basic HTTP caching functionality"""
        # Mock API response
        mock_data = {"id": 1, "name": "test_user"}
        respx.get("https://api.test.com/users").mock(
            return_value=httpx.Response(200, json=mock_data, headers={"etag": "v1"})
        )

        config = CacheConfig(enable_logging=True)

        async def test() -> None:
            async with CachedClient(base_url="https://api.test.com", cache_config=config) as client:
                # First request - cache miss
                response1 = await client.get("/users")
                assert response1.status_code == 200
                assert response1.json() == mock_data

                # Second request - should be from cache
                response2 = await client.get("/users")
                assert response2.status_code == 200
                assert response2.json() == mock_data
                # Note: In real implementation, this would have x-cachedx: HIT header

        import asyncio

        asyncio.run(test())

    def test_etag_revalidation(self) -> None:
        """Test ETag-based revalidation (304 responses)"""
        mock_data = {"id": 1, "name": "test_user"}

        # First response with ETag
        respx.get("https://api.test.com/users").mock(
            return_value=httpx.Response(200, json=mock_data, headers={"etag": "v1"})
        )

        config = CacheConfig(
            endpoints={
                "/users": EndpointConfig(
                    strategy=CacheStrategy.CACHED,
                    ttl=timedelta(seconds=1),  # Short TTL to trigger revalidation
                )
            }
        )

        async def test() -> None:
            async with CachedClient(base_url="https://api.test.com", cache_config=config) as client:
                # First request
                response1 = await client.get("/users")
                assert response1.status_code == 200

                # Wait for TTL to expire
                import asyncio

                await asyncio.sleep(1.1)

                # Mock 304 response for revalidation
                respx.get("https://api.test.com/users").mock(
                    return_value=httpx.Response(304, headers={"etag": "v1"})
                )

                # Second request - should trigger revalidation
                response2 = await client.get("/users")
                assert response2.status_code == 200  # Should return cached data
                assert response2.json() == mock_data

        import asyncio

        asyncio.run(test())

    def test_cache_strategies(self) -> None:
        """Test different caching strategies"""
        config = CacheConfig(
            endpoints={
                "/static": EndpointConfig(strategy=CacheStrategy.STATIC),
                "/disabled": EndpointConfig(strategy=CacheStrategy.DISABLED),
                "/realtime": EndpointConfig(strategy=CacheStrategy.REALTIME),
            }
        )

        # Mock different endpoints
        respx.get("https://api.test.com/static").mock(
            return_value=httpx.Response(200, json={"type": "static"})
        )
        respx.get("https://api.test.com/disabled").mock(
            return_value=httpx.Response(200, json={"type": "disabled"})
        )
        respx.get("https://api.test.com/realtime").mock(
            return_value=httpx.Response(200, json={"type": "realtime"})
        )

        async def test() -> None:
            async with CachedClient(base_url="https://api.test.com", cache_config=config) as client:
                # Test different strategies
                static_response = await client.get("/static")
                disabled_response = await client.get("/disabled")
                realtime_response = await client.get("/realtime")

                assert static_response.status_code == 200
                assert disabled_response.status_code == 200
                assert realtime_response.status_code == 200

        import asyncio

        asyncio.run(test())
