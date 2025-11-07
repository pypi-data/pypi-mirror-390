"""
Simple HTTP caching example - minimal configuration
"""

import asyncio

from cachedx.httpcache import CachedClient


async def main() -> None:
    """Simple caching example with zero configuration"""

    # Zero configuration - uses sensible defaults
    async with CachedClient(base_url="https://api.github.com") as client:
        print("Making first request (will be cached)...")
        response1 = await client.get("/users/octocat")
        user1 = response1.json()
        print(f"User: {user1['name']} (@{user1['login']})")
        print(f"Cache: {response1.headers.get('x-cachedx', 'MISS')}")

        print("\nMaking second request (from cache)...")
        response2 = await client.get("/users/octocat")
        user2 = response2.json()
        print(f"User: {user2['name']} (@{user2['login']})")
        print(f"Cache: {response2.headers.get('x-cachedx', 'MISS')}")

        print("\nQuerying cached data with SQL...")
        # Auto-generated view from the cached response
        results = client.query("SELECT * FROM users_octocat")
        print(f"Cached data rows: {len(results)}")

        # Show cache statistics
        stats = client.stats()
        print(f"\nCache stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
