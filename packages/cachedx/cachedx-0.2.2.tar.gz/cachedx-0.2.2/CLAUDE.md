# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**cachedx** is a unified HTTP caching library with DuckDB mirroring and LLM safety features. It provides intelligent caching with automatic database mirroring, making it easy to cache API responses and query them with SQL.

**Key Features:**

- Zero-config HTTP caching with TTL/ETag support
- Dual storage architecture (HTTP cache + normalized tables)
- Auto-inference of schemas from JSON responses
- LLM-safe SQL execution with comprehensive safety layers
- Production-ready with comprehensive Pydantic validation

## Development Commands

This project uses **uv** as the package manager and requires **Python 3.12+**.

### Setup

```bash
uv sync                    # Install dependencies
```

### Testing

```bash
uv run pytest                     # Run all tests
uv run pytest tests/test_safe_sql.py -v    # Run specific test file
uv run pytest -k "test_name"      # Run specific test by name
```

### Code Quality

```bash
uv run ruff check cachedx         # Lint code
uv run ruff format cachedx        # Format code
uv run mypy cachedx               # Type checking
```

### Examples

```bash
uv run python examples/simple_cache.py      # Basic caching demo
uv run python examples/basic_demo.py        # Core features demo
uv run python examples/llm_safety_demo.py   # LLM safety features
```

## Architecture Overview

The codebase follows a **modular layered architecture** with clear separation of concerns:

### Core Layers

1. **HTTP Cache Layer** (`cachedx.httpcache`):
   - `CachedClient`: httpx.AsyncClient wrapper with intelligent caching
   - `CacheStorage`: DuckDB-backed storage with TTL and ETag support
   - `CacheConfig`/`EndpointConfig`: Pydantic configuration models
   - Cache strategies: CACHED, STATIC, REALTIME, DISABLED

2. **Mirror Layer** (`cachedx.mirror`):
   - `@hybrid_cache`: Decorator for automatic response mirroring
   - `SchemaInferrer`: Auto-inference of SQL schemas from JSON
   - `Mapping`: Pydantic models for resource schema definitions
   - Registry system for managing resource mappings

3. **Core Utilities** (`cachedx.core`):
   - `safe_select()`: LLM-safe SQL execution (SELECT-only)
   - `build_llm_context()`: Schema context generation for LLMs
   - DuckDB connection management and utilities

### Data Flow Architecture

**Dual Storage Model:**

- `_cx_cache`: HTTP cache table (exact responses with metadata)
- `cx_raw`: Raw JSON provenance table (audit trail)
- Normalized tables: Structured data for fast SQL queries

**Key Design Patterns:**

- Write-through caching (no invalidation, automatic upsert)
- Progressive disclosure (zero-config → advanced configuration)
- Comprehensive Pydantic validation throughout
- LLM safety with multi-layer SQL guards

## Important Implementation Details

### Request Processing

The `CachedClient.request()` method implements the core caching logic:

1. Generates cache key from request signature (method + path + params + vary headers)
2. For GETs: Check cache → conditional GET with ETag → store response
3. For writes: Execute request → write-through upsert to maintain consistency

### LLM Safety Layers

All LLM-generated queries go through `safe_select()` which:

- Blocks all non-SELECT statements
- Prevents dangerous keywords (DROP, DELETE, etc.)
- Auto-injects LIMIT clauses
- Validates query structure before execution

### Schema Inference

The `SchemaInferrer` analyzes JSON responses to:

- Detect data types (string, integer, timestamp, etc.)
- Generate appropriate SQL column types
- Create JSONPath mappings for nested data
- Handle arrays and nested objects

## Configuration Patterns

### HTTP Cache Configuration

```python
CacheConfig(
    endpoints={
        "/api/users": EndpointConfig(
            strategy=CacheStrategy.CACHED,
            ttl=timedelta(minutes=10),
            table_name="users"
        ),
        "/api/static/*": EndpointConfig(strategy=CacheStrategy.STATIC)
    }
)
```

### Resource Mirroring

```python
register("resource_name", Mapping(
    table="target_table",
    columns={
        "id": "$.id",
        "name": "$.name",
        "timestamp": "CAST(j->>'created_at' AS TIMESTAMP)"
    }
))
```

## Testing Architecture

Tests are organized by layer:

- `test_safe_sql.py`: LLM safety and SQL validation
- `test_httpcache.py`: HTTP caching logic and configuration
- `test_mirror.py`: Schema inference, registry, and data normalization

**Testing Patterns:**

- Use `:memory:` DuckDB for isolated tests
- Mock HTTP responses with `respx` for cache testing
- Comprehensive Pydantic validation testing
- Safety feature verification (blocking dangerous queries)

## Key Dependencies

- **httpx**: HTTP client foundation
- **DuckDB**: High-performance analytics database
- **Pydantic**: Data validation and settings management
- **orjson**: High-performance JSON serialization
- **typing-extensions**: Modern typing support

## Common Gotchas

1. **DuckDB Connection Management**: The codebase uses a singleton connection pattern in `core.duck`. Tests should call `connect(":memory:")` for isolation.

2. **Timezone Handling**: All timestamps use UTC with timezone info. The `ensure_timezone()` utility handles naive datetime conversion.

3. **View Generation**: Auto-generated views from cached JSON use simplified SQL for compatibility across DuckDB versions.

4. **Request Parameter Separation**: `CachedClient.request()` separates `build_request` parameters from `send` parameters to match httpx's API correctly.

5. **Error Handling Philosophy**: Cache failures fall back gracefully (return origin response), but LLM safety violations raise clear errors immediately.
