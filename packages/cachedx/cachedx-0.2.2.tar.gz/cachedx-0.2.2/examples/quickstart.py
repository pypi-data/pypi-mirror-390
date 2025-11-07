"""
Quickstart example for cachedx - demonstrates both HTTP cache and mirror layers
"""

import asyncio
from datetime import timedelta
from typing import Any

from cachedx.httpcache import CacheConfig, CachedClient, CacheStrategy, EndpointConfig
from cachedx.mirror import Mapping, register


async def http_cache_demo() -> None:
    """Demonstrate basic HTTP caching capabilities"""
    print("🚀 HTTP Cache Demo")
    print("=" * 50)

    # Configure caching strategies for different endpoints
    config = CacheConfig(
        default_ttl=timedelta(minutes=5),
        enable_logging=True,
        endpoints={
            "/users": EndpointConfig(
                strategy=CacheStrategy.CACHED, ttl=timedelta(minutes=10), table_name="github_users"
            ),
            "/repos/*": EndpointConfig(
                strategy=CacheStrategy.STATIC,  # Cache forever for repo info
                table_name="repositories",
            ),
        },
    )

    async with CachedClient(base_url="https://api.github.com", cache_config=config) as client:
        print("\n1. First request (cache miss)...")
        response1 = await client.get("/users")
        print(f"   Status: {response1.status_code}")
        print(f"   Cache header: {response1.headers.get('x-cachedx', 'MISS')}")

        print("\n2. Second request (cache hit)...")
        response2 = await client.get("/users")
        print(f"   Status: {response2.status_code}")
        print(f"   Cache header: {response2.headers.get('x-cachedx', 'MISS')}")

        print("\n3. Query cached data with SQL...")
        try:
            results = client.query("SELECT _raw->>'login' as login FROM github_users LIMIT 5")
            print(f"   Found {len(results)} users")
            if hasattr(results, "head"):  # pandas DataFrame
                print(results.head())
            else:  # list of dicts
                for user in results:
                    print(f"   - {user}")
        except Exception as e:
            print(f"   Query error: {e}")

        print("\n4. Cache statistics...")
        stats = client.stats()
        print(f"   Total entries: {stats.get('total_entries', 0)}")
        print(f"   Active entries: {stats.get('active_entries', 0)}")
        print(f"   Views created: {stats.get('view_count', 0)}")


async def mirror_demo() -> None:
    """Demonstrate resource mirroring with schema inference"""
    print("\n\n🪞 Mirror Demo")
    print("=" * 50)

    # Register a resource mapping with explicit schema
    register(
        "user_profiles",
        Mapping(
            table="user_profiles",
            columns={
                "id": "$.id",
                "login": "$.login",
                "name": "$.name",
                "public_repos": "$.public_repos",
                "followers": "$.followers",
                "created_at": "CAST(j->>'created_at' AS TIMESTAMP)",
            },
            ddl="""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY,
            login TEXT NOT NULL,
            name TEXT,
            public_repos INTEGER,
            followers INTEGER,
            created_at TIMESTAMP,
            _raw JSON,
            _fetched_at TIMESTAMP DEFAULT now(),
            _updated_at TIMESTAMP DEFAULT now()
        )
        """,
        ),
    )

    # Use the hybrid_cache decorator for automatic mirroring
    from cachedx.mirror import hybrid_cache

    @hybrid_cache(resource="user_profiles")
    async def get_user_profile(client: Any, username: str) -> Any:
        return await client.get(f"/users/{username}")

    config = CacheConfig(enable_logging=True)
    async with CachedClient(base_url="https://api.github.com", cache_config=config) as client:
        print("\n1. Fetch user profiles (with automatic mirroring)...")
        users = ["octocat", "torvalds", "gvanrossum"]

        for username in users:
            try:
                await get_user_profile(client, username)
                print(f"   ✓ Mirrored profile for {username}")
            except Exception as e:
                print(f"   ✗ Failed to mirror {username}: {e}")

        print("\n2. Query normalized data...")
        from cachedx import safe_select

        try:
            results = safe_select("""
                SELECT login, name, public_repos, followers
                FROM user_profiles
                ORDER BY public_repos DESC
                LIMIT 10
            """)

            print(f"   Found {len(results)} profiles:")
            if hasattr(results, "to_string"):  # pandas DataFrame
                print(results.to_string())
            else:  # list of dicts
                for profile in results:
                    print(f"   - {profile['login']}: {profile['public_repos']} repos")

        except Exception as e:
            print(f"   Query error: {e}")


async def llm_helper_demo() -> None:
    """Demonstrate LLM integration helpers"""
    print("\n\n🤖 LLM Helper Demo")
    print("=" * 50)

    from cachedx import build_llm_context, safe_llm_query, suggest_queries

    print("\n1. Building LLM context...")
    context = build_llm_context(include_samples=True, sample_limit=2)
    print(f"   Context length: {len(context)} characters")
    print("   Sample context:")
    print("   " + "\n   ".join(context.split("\n")[:10]))
    print("   ...")

    print("\n2. Safe LLM query execution...")
    test_queries = [
        "SELECT COUNT(*) as total_users FROM github_users",
        "SELECT login, name FROM user_profiles WHERE followers > 1000 LIMIT 5",
        "DROP TABLE user_profiles",  # This should be blocked
    ]

    for query in test_queries:
        print(f"\n   Query: {query}")
        result = safe_llm_query(query, limit=10)

        if result["success"]:
            print(f"   ✓ Success: {result['row_count']} rows in {result['execution_time_ms']}ms")
            if result["warnings"]:
                print(f"   ⚠ Warnings: {result['warnings']}")
        else:
            print(f"   ✗ Error: {result.get('error', 'Unknown error')}")

    print("\n3. Query suggestions...")
    suggestions = suggest_queries(max_suggestions=3)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion['description']}")
        print(f"      {suggestion['sql']}")


async def main() -> None:
    """Run all demos"""
    print("cachedx Quickstart Demo")
    print("=" * 70)

    try:
        # HTTP cache demo
        await http_cache_demo()

        # Mirror demo
        await mirror_demo()

        # LLM helper demo
        await llm_helper_demo()

        print("\n\n✨ Demo completed successfully!")
        print("\nNext steps:")
        print("- Try modifying the cache configurations")
        print("- Create your own resource mappings")
        print("- Experiment with SQL queries on cached data")
        print("- Integrate with your favorite LLM for query generation")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
