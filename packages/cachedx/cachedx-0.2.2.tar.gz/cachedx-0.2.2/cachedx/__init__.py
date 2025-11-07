"""
cachedx - Unified HTTP caching with DuckDB mirroring and LLM helpers
"""

from .core.duck import con, connect
from .core.llm import build_llm_context, safe_llm_query, suggest_queries
from .core.safe_sql import safe_select, validate_sql

__version__ = "0.2.1"
__all__ = [
    "connect",
    "con",
    "safe_select",
    "validate_sql",
    "build_llm_context",
    "safe_llm_query",
    "suggest_queries",
]
