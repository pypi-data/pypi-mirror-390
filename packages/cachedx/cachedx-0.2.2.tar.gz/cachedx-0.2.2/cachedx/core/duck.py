"""DuckDB connection management and core utilities"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import duckdb

try:
    import duckdb
except ImportError as e:
    raise ImportError(
        "duckdb is required for cachedx. Install with: pip install 'cachedx[dev]' or pip install duckdb>=1.0.0"
    ) from e

_CONN: duckdb.DuckDBPyConnection | None = None
_LOCK = threading.Lock()

# Core tables DDL
CACHE_DDL = """
CREATE TABLE IF NOT EXISTS _cx_cache(
  key TEXT PRIMARY KEY,
  method TEXT NOT NULL,
  path TEXT NOT NULL,
  params TEXT,
  headers TEXT,
  status INTEGER NOT NULL,
  etag TEXT,
  fetched_at TIMESTAMP NOT NULL DEFAULT now(),
  expires_at TIMESTAMP,
  payload JSON NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cx_cache_path ON _cx_cache(path);
CREATE INDEX IF NOT EXISTS idx_cx_cache_expires ON _cx_cache(expires_at);
"""

RAW_DDL = """
CREATE TABLE IF NOT EXISTS cx_raw(
  key TEXT PRIMARY KEY,
  resource TEXT NOT NULL,
  payload JSON NOT NULL,
  fetched_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_cx_raw_resource ON cx_raw(resource);
"""


def connect(path: str = ":memory:") -> duckdb.DuckDBPyConnection:
    """
    Create or get a DuckDB connection with cachedx tables initialized.

    Args:
        path: Database path, defaults to in-memory

    Returns:
        DuckDB connection
    """
    global _CONN
    with _LOCK:
        if _CONN is None:
            _CONN = duckdb.connect(path)
            # Initialize core tables
            _CONN.execute(CACHE_DDL)
            _CONN.execute(RAW_DDL)
    return _CONN


def con() -> duckdb.DuckDBPyConnection:
    """
    Get the current DuckDB connection, creating one if needed.

    Returns:
        DuckDB connection
    """
    return _CONN or connect(":memory:")


def close() -> None:
    """Close the current connection"""
    global _CONN
    with _LOCK:
        if _CONN is not None:
            _CONN.close()
            _CONN = None
