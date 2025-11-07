"""
Demo of LLM safety features
"""

from cachedx import safe_llm_query, safe_select, validate_sql


def main() -> None:
    """Demo LLM safety features"""
    print("🛡️ LLM Safety Features Demo")
    print("=" * 50)

    # First, let's create some test data
    from cachedx.core.duck import con, connect

    connect(":memory:")

    # Create test table
    con().execute("""
        CREATE TABLE demo_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT now()
        )
    """)

    # Insert test data
    con().execute("""
        INSERT INTO demo_users (id, name, email, active) VALUES
        (1, 'Alice', 'alice@example.com', true),
        (2, 'Bob', 'bob@example.com', false),
        (3, 'Charlie', 'charlie@example.com', true),
        (4, 'Diana', 'diana@example.com', true),
        (5, 'Eve', 'eve@example.com', false)
    """)

    print("\n1. Safe Query Execution...")

    # Test valid queries
    safe_queries = [
        "SELECT * FROM demo_users",
        "SELECT name, email FROM demo_users WHERE active = true",
        "SELECT COUNT(*) as total_users FROM demo_users",
        "SELECT active, COUNT(*) as count FROM demo_users GROUP BY active",
    ]

    for query in safe_queries:
        try:
            result = safe_select(query, limit=10)
            print(f"   ✅ '{query[:40]}...': {len(result)} rows")
        except Exception as e:
            print(f"   ❌ '{query[:40]}...': {e}")

    print("\n2. Dangerous Query Blocking...")

    # Test dangerous queries that should be blocked
    dangerous_queries = [
        "DROP TABLE demo_users",
        "DELETE FROM demo_users WHERE id = 1",
        "INSERT INTO demo_users (name) VALUES ('hacker')",
        "UPDATE demo_users SET name = 'compromised'",
        "CREATE TABLE evil_table (id INT)",
        "ALTER TABLE demo_users ADD COLUMN evil TEXT",
    ]

    for query in dangerous_queries:
        try:
            result = safe_select(query)
            print(f"   ❌ SECURITY BREACH: '{query}' was allowed!")
        except ValueError as e:
            print(f"   ✅ Blocked: '{query[:40]}...' - {str(e)[:50]}...")
        except Exception as e:
            print(f"   ⚠️  Other error: '{query[:40]}...' - {e}")

    print("\n3. Query Validation...")

    test_queries = [
        ("SELECT * FROM demo_users", True),
        ("DROP TABLE demo_users", False),
        ("", False),
        ("SHOW TABLES", False),
        ("SELECT name FROM demo_users WHERE id = ?", True),
    ]

    for query, should_be_valid in test_queries:
        is_valid, error = validate_sql(query)
        status = "✅" if is_valid == should_be_valid else "❌"
        print(f"   {status} '{query[:40]}...': valid={is_valid}, expected={should_be_valid}")
        if error:
            print(f"      Error: {error}")

    print("\n4. LLM Query Helper...")

    # Test the safe_llm_query function
    llm_test_queries = [
        "SELECT COUNT(*) FROM demo_users",
        "SELECT name FROM demo_users WHERE active = true",
        "DROP TABLE demo_users",  # Should be blocked
    ]

    for query in llm_test_queries:
        print(f"\n   Testing: {query}")
        result = safe_llm_query(query, limit=5)

        if result["success"]:
            print(f"   ✅ Success: {result['row_count']} rows in {result['execution_time_ms']}ms")
            if result["warnings"]:
                for warning in result["warnings"]:
                    print(f"   ⚠️  Warning: {warning}")
        else:
            print(f"   🚫 Blocked: {result.get('error', 'Unknown error')}")

    print("\n5. Automatic LIMIT Injection...")

    # Test that LIMIT is automatically added
    queries_without_limit = [
        "SELECT * FROM demo_users",
        "SELECT name FROM demo_users WHERE active = true",
    ]

    for query in queries_without_limit:
        result = safe_llm_query(query, limit=2)  # Very small limit for demo
        if result["success"]:
            print(f"   ✅ Query: '{query}'")
            print(f"      Auto-limited to: {result['row_count']} rows")
        else:
            print(f"   ❌ Failed: {result.get('error')}")

    print("\n✨ LLM Safety Demo Completed!")
    print("\nSafety Features Demonstrated:")
    print("- 🛡️ SELECT-only query enforcement")
    print("- 🚫 Dangerous keyword blocking")
    print("- 🔒 SQL injection prevention")
    print("- 📏 Automatic LIMIT injection")
    print("- ⚡ Query validation and error handling")
    print("- 📊 Execution timing and metadata")


if __name__ == "__main__":
    main()
