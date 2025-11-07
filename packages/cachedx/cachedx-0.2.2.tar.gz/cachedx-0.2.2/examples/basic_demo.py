"""
Basic demo showing cachedx core functionality
"""

import asyncio

from cachedx import build_llm_context, safe_select
from cachedx.httpcache import CachedClient


async def main() -> None:
    """Basic functionality demo"""
    print("🚀 cachedx Basic Demo")
    print("=" * 50)

    # Create client with default configuration
    async with CachedClient(base_url="https://api.github.com") as client:
        print("\n1. Making API requests (automatically cached)...")

        # Make several API calls
        endpoints = ["/users/octocat", "/users/torvalds", "/users/gvanrossum"]

        for endpoint in endpoints:
            try:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    user = response.json()
                    print(f"   ✓ Fetched {user['name']} (@{user['login']})")
                else:
                    print(f"   ✗ Failed to fetch {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"   ✗ Error fetching {endpoint}: {e}")

        print("\n2. Querying cached data with SQL...")

        # Use safe_select to query the cached data
        try:
            # Find all cached user data
            result = safe_select(
                "SELECT table_name FROM information_schema.tables WHERE table_type = 'VIEW'"
            )
            print(f"   Available views: {len(result)} found")

            if result:
                for row in result:
                    view_name = (
                        row[0]
                        if isinstance(row, list | tuple)
                        else row.get("table_name", "unknown")
                    )
                    print(f"     - {view_name}")

                # Query a specific view if available
                first_view = (
                    result[0][0]
                    if isinstance(result[0], list | tuple)
                    else result[0].get("table_name")
                )
                if first_view:
                    data = safe_select(f"SELECT * FROM {first_view} LIMIT 1")  # nosec B608
                    print(f"   Sample data from {first_view}: {len(data)} rows")

        except Exception as e:
            print(f"   Error querying data: {e}")

        print("\n3. LLM Context Generation...")

        try:
            context = build_llm_context(include_samples=True, sample_limit=1)
            print(f"   Generated context: {len(context)} characters")

            # Show a sample of the context
            lines = context.split("\n")[:15]
            print("   Context preview:")
            for line in lines:
                print(f"   {line}")
            if len(context.split("\n")) > 15:
                print("   ...")

        except Exception as e:
            print(f"   Error generating LLM context: {e}")

        print("\n4. Cache Statistics...")

        try:
            stats = client.stats()
            print("   Cache Stats:")
            for key, value in stats.items():
                if key != "views":  # Don't print the full views list again
                    print(f"     {key}: {value}")

        except Exception as e:
            print(f"   Error getting stats: {e}")

    print("\n✨ Basic demo completed!")
    print("\nKey Features Demonstrated:")
    print("- ✅ Automatic HTTP caching")
    print("- ✅ View generation from cached JSON")
    print("- ✅ Safe SQL querying")
    print("- ✅ LLM context generation")
    print("- ✅ Cache statistics and monitoring")


if __name__ == "__main__":
    asyncio.run(main())
