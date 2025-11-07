"""Tests for SQL safety features"""

import pytest
from cachedx.core.duck import connect
from cachedx.core.safe_sql import safe_select, validate_sql


class TestSafeSQL:
    """Test SQL safety layer"""

    @pytest.fixture(autouse=True)  # type: ignore[misc]
    def setup(self) -> None:
        """Set up test database"""
        # Ensure connection exists
        connect(":memory:")

        # Create test table
        from cachedx.core.duck import con

        con().execute("""
            CREATE OR REPLACE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                active BOOLEAN DEFAULT true
            )
        """)

        # Insert test data
        con().execute("""
            INSERT INTO test_users (id, name, email, active) VALUES
            (1, 'Alice', 'alice@example.com', true),
            (2, 'Bob', 'bob@example.com', false),
            (3, 'Charlie', 'charlie@example.com', true)
        """)

    def test_valid_select(self) -> None:
        """Test valid SELECT queries"""
        result = safe_select("SELECT * FROM test_users")
        assert len(result) == 3

    def test_select_with_where(self) -> None:
        """Test SELECT with WHERE clause"""
        result = safe_select("SELECT * FROM test_users WHERE active = true")
        assert len(result) == 2

    def test_select_with_params(self) -> None:
        """Test parameterized queries"""
        result = safe_select("SELECT * FROM test_users WHERE id = ?", [1])
        assert len(result) == 1

        # Check data structure
        if isinstance(result, list):
            assert result[0]["name"] == "Alice"
        else:  # pandas DataFrame
            assert result.iloc[0]["name"] == "Alice"

    def test_automatic_limit_addition(self) -> None:
        """Test that LIMIT is automatically added"""
        result = safe_select("SELECT * FROM test_users", limit=2)
        assert len(result) <= 2

    def test_existing_limit_preserved(self) -> None:
        """Test that existing LIMIT is preserved"""
        result = safe_select("SELECT * FROM test_users LIMIT 1")
        assert len(result) == 1

    def test_dangerous_queries_blocked(self) -> None:
        """Test that dangerous queries are blocked"""
        dangerous_queries = [
            "DROP TABLE test_users",
            "DELETE FROM test_users",
            "INSERT INTO test_users (name) VALUES ('hacker')",
            "UPDATE test_users SET name = 'hacked'",
            "CREATE TABLE evil (id INT)",
            "ALTER TABLE test_users ADD COLUMN evil TEXT",
            "TRUNCATE TABLE test_users",
        ]

        for query in dangerous_queries:
            with pytest.raises(ValueError, match="dangerous keyword|Only SELECT"):
                safe_select(query)

    def test_non_select_queries_blocked(self) -> None:
        """Test that non-SELECT queries are blocked"""
        non_select_queries = [
            "SHOW TABLES",
            "DESCRIBE test_users",
            "EXPLAIN SELECT * FROM test_users",
        ]

        for query in non_select_queries:
            with pytest.raises(ValueError, match="Only SELECT"):
                safe_select(query)

    def test_validate_sql_function(self) -> None:
        """Test SQL validation function"""
        # Valid queries
        valid, error = validate_sql("SELECT * FROM test_users")
        assert valid
        assert not error

        # Invalid queries
        invalid, error = validate_sql("DROP TABLE test_users")
        assert not invalid
        assert "only select" in error.lower()

        # Non-SELECT
        invalid, error = validate_sql("SHOW TABLES")
        assert not invalid
        assert "Only SELECT" in error

    def test_empty_and_invalid_input(self) -> None:
        """Test handling of empty and invalid input"""
        with pytest.raises(ValueError, match="non-empty string"):
            safe_select("")

        with pytest.raises(ValueError, match="non-empty string"):
            safe_select(None)  # type: ignore

        # Validation function should handle gracefully
        valid, error = validate_sql("")
        assert not valid
        assert "non-empty string" in error

        valid, error = validate_sql(None)  # type: ignore
        assert not valid
        assert "non-empty string" in error
