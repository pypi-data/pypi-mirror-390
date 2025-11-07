# Contributing to cachedx

We love contributions! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Setup Instructions

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/yourusername/cachedx.git
   cd cachedx
   ```

2. **Install dependencies**

   ```bash
   uv sync --all-extras --dev
   ```

3. **Install pre-commit hooks**

   ```bash
   uv run pre-commit install
   ```

4. **Verify your setup**
   ```bash
   uv run pytest tests/ -v
   uv run ruff check cachedx
   uv run mypy cachedx
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the existing style
   - Add tests for new functionality
   - Update documentation if needed

3. **Run tests locally**

   ```bash
   uv run pytest tests/ -v
   uv run ruff check cachedx
   uv run ruff format cachedx
   uv run mypy cachedx
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `ci:` - CI/CD changes
- `deps:` - Dependency updates

### Pull Request Process

1. **Push your branch**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Use the PR template
   - Link to relevant issues
   - Describe your changes clearly
   - Add screenshots/examples if applicable

3. **Review Process**
   - All PRs require review before merging
   - Address reviewer feedback promptly
   - Keep your PR up to date with main branch

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_safe_sql.py -v

# Run with coverage
uv run pytest tests/ --cov=cachedx --cov-report=term

# Run specific test by name
uv run pytest -k "test_name"
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Use `pytest` fixtures for setup
- Mock external dependencies with `respx`

Example test structure:

```python
import pytest
from cachedx import CachedClient

@pytest.mark.asyncio
async def test_cache_functionality():
    client = CachedClient()
    # Test implementation
    assert result == expected
```

## Code Style

We use several tools to maintain code quality:

### Formatting and Linting

- **Ruff**: Linting and formatting
- **MyPy**: Type checking
- **Bandit**: Security analysis

### Pre-commit Hooks

Pre-commit hooks automatically run before each commit:

- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Security scanning (bandit)
- Various file checks

## Architecture Guidelines

### Code Organization

- `cachedx/core/`: Core utilities and DuckDB management
- `cachedx/httpcache/`: HTTP caching layer
- `cachedx/mirror/`: Database mirroring functionality
- `tests/`: All test files

### Design Principles

- **Progressive disclosure**: Zero-config → advanced configuration
- **Type safety**: Comprehensive Pydantic validation
- **LLM safety**: Multi-layer SQL guards
- **Performance**: Efficient caching and database operations

### Adding New Features

1. **Follow existing patterns**
   - Look at similar functionality in the codebase
   - Use Pydantic for configuration and validation
   - Add comprehensive error handling

2. **Maintain backwards compatibility**
   - Don't break existing APIs
   - Use deprecation warnings for removed features
   - Follow semantic versioning

3. **Add comprehensive tests**
   - Unit tests for new functions/classes
   - Integration tests for end-to-end functionality
   - Error condition testing

4. **Update documentation**
   - Add docstrings to new functions
   - Update examples if needed
   - Add to CHANGELOG.md

## Documentation

### Building Docs Locally

```bash
uv run mkdocs serve
```

### Documentation Structure

- Docstrings: Use Google style format
- Examples: Include practical usage examples
- Type hints: Required for all public APIs

## Performance Considerations

- Use async/await for I/O operations
- Leverage DuckDB's performance features
- Cache expensive operations
- Profile code for bottlenecks

## Security Guidelines

- Never commit secrets or credentials
- Use `safe_select()` for all LLM-generated queries
- Validate user input thoroughly
- Follow principle of least privilege

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/yourusername/cachedx/discussions)
- **Bugs**: Create an [Issue](https://github.com/yourusername/cachedx/issues)
- **Features**: Create a [Feature Request](https://github.com/yourusername/cachedx/issues)

## Recognition

Contributors will be:

- Added to the CONTRIBUTORS.md file
- Mentioned in release notes for significant contributions
- Credited in documentation for major features

Thank you for contributing to cachedx! 🎉
