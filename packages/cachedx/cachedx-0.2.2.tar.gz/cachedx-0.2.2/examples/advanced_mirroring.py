"""
Advanced mirroring example with auto-inference and custom mappings
"""

import asyncio
from datetime import timedelta
from typing import Any

from cachedx.httpcache import CacheConfig, CachedClient, CacheStrategy, EndpointConfig
from cachedx.mirror import Mapping, hybrid_cache, mirror_json, register


async def main() -> None:
    """Demonstrate advanced mirroring capabilities"""

    print("Advanced Mirroring Demo")
    print("=" * 50)

    # Register custom mapping for GitHub repositories
    register(
        "repositories",
        Mapping(
            table="github_repos",
            columns={
                "id": "$.id",
                "full_name": "$.full_name",
                "description": "$.description",
                "language": "$.language",
                "stars": "$.stargazers_count",
                "forks": "$.forks_count",
                "size_kb": "$.size",
                "is_private": "$.private",
                "created_at": "CAST(j->>'created_at' AS TIMESTAMP)",
                "updated_at": "CAST(j->>'updated_at' AS TIMESTAMP)",
            },
            ddl="""
        CREATE TABLE IF NOT EXISTS github_repos (
            id BIGINT PRIMARY KEY,
            full_name TEXT NOT NULL,
            description TEXT,
            language TEXT,
            stars INTEGER DEFAULT 0,
            forks INTEGER DEFAULT 0,
            size_kb INTEGER DEFAULT 0,
            is_private BOOLEAN DEFAULT false,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            _raw JSON,
            _fetched_at TIMESTAMP DEFAULT now(),
            _updated_at TIMESTAMP DEFAULT now()
        )
        """,
        ),
    )

    # Create decorator for automatic mirroring
    @hybrid_cache(resource="repositories")
    async def fetch_user_repos(client: Any, username: str) -> Any:
        """Fetch user repositories with automatic mirroring"""
        return await client.get(f"/users/{username}/repos?per_page=10")

    # Configure client with caching
    config = CacheConfig(
        default_ttl=timedelta(minutes=15),
        enable_logging=True,
        endpoints={
            "/users/*/repos": EndpointConfig(
                strategy=CacheStrategy.CACHED,
                ttl=timedelta(minutes=30),
                flatten=True,  # Create views from array responses
            )
        },
    )

    async with CachedClient(base_url="https://api.github.com", cache_config=config) as client:
        print("\n1. Fetching repositories with auto-mirroring...")
        users = ["microsoft", "google", "facebook"]

        for username in users:
            try:
                response = await fetch_user_repos(client, username)
                repos = response.json()
                print(f"   ✓ Mirrored {len(repos)} repos for {username}")
            except Exception as e:
                print(f"   ✗ Failed to fetch repos for {username}: {e}")

        print("\n2. Querying mirrored repository data...")
        from cachedx import safe_llm_query

        queries = [
            {
                "name": "Most popular repositories",
                "sql": """
                SELECT full_name, language, stars, forks
                FROM github_repos
                WHERE stars > 1000
                ORDER BY stars DESC
                LIMIT 10
                """,
            },
            {
                "name": "Repositories by language",
                "sql": """
                SELECT
                    language,
                    COUNT(*) as repo_count,
                    AVG(stars) as avg_stars,
                    SUM(stars) as total_stars
                FROM github_repos
                WHERE language IS NOT NULL
                GROUP BY language
                ORDER BY total_stars DESC
                LIMIT 5
                """,
            },
            {
                "name": "Recent activity",
                "sql": """
                SELECT full_name, updated_at, stars
                FROM github_repos
                WHERE updated_at > '2023-01-01'
                ORDER BY updated_at DESC
                LIMIT 5
                """,
            },
        ]

        for query_info in queries:
            print(f"\n   {query_info['name']}:")
            result = safe_llm_query(query_info["sql"])

            if result["success"]:
                data = result["data"]
                print(f"   Found {result['row_count']} results")

                if hasattr(data, "to_string"):  # pandas DataFrame
                    print("   " + "\n   ".join(data.to_string().split("\n")[:6]))
                else:  # list of dicts
                    for i, row in enumerate(data[:5]):
                        print(f"     {i + 1}. {row}")
            else:
                print(f"   Error: {result.get('error')}")

        print("\n3. Auto-inference demo with sample data...")

        # Simulate some API response data with challenging edge cases
        sample_data = [
            {
                "id": 1,
                "title": "Sample Issue #1",
                "state": "open",
                "labels": ["bug", "priority-high"],
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-16T14:22:00Z",
                "user": {"login": "developer1", "id": 12345},
                "assignees": [{"login": "developer2", "id": 23456}],
            },
            {
                "id": 2,
                "title": "Sample Issue #2",
                "state": "closed",
                "labels": ["enhancement"],
                "created_at": "2024-01-10T09:15:00Z",
                "updated_at": "2024-01-14T16:45:00Z",
                "user": {"login": "developer3", "id": 34567},
                "assignees": [],  # Empty array - this was the problem case!
            },
        ]

        # Let auto-inference create the schema (this should now work!)
        print("   Auto-inferring schema from sample issue data...")
        mirror_json(sample_data, "github_issues", auto_register=True)
        print("   ✓ Auto-registered 'github_issues' resource with nullable array fields")

        # Query the auto-inferred data
        result = safe_llm_query("SELECT * FROM github_issues")
        if result["success"]:
            print(f"   Auto-inferred table has {result['row_count']} rows")

        print("\n4. LLM context for query generation...")
        from cachedx import build_llm_context

        context = build_llm_context(include_samples=True, sample_limit=1)
        print(f"   Generated {len(context)} characters of context")
        print("   Context includes schemas for:")

        # Extract table names from context
        import re

        tables = re.findall(r"### Table: `(\w+)`", context)
        for table in tables:
            print(f"     - {table}")

        print("\n✨ Advanced mirroring demo completed!")
        print("\nKey features demonstrated:")
        print("- Custom schema mappings with type casting")
        print("- Automatic mirroring with @hybrid_cache decorator")
        print("- Schema auto-inference from JSON data")
        print("- Complex SQL queries on mirrored data")
        print("- LLM context generation for query assistance")


if __name__ == "__main__":
    asyncio.run(main())
