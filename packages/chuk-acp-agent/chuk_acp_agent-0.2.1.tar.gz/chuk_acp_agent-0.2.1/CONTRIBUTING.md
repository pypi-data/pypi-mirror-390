# Contributing to chuk-acp-agent

Thank you for considering contributing to chuk-acp-agent! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Clone the repository:**

```bash
git clone https://github.com/chrishayuk/chuk-acp-agent.git
cd chuk-acp-agent
```

2. **Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in development mode:**

```bash
pip install -e ".[dev,mcp]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chuk_acp_agent

# Run specific test file
pytest tests/test_session_memory.py

# Run with verbose output
pytest -v
```

## Code Quality

We use several tools to maintain code quality:

### Ruff (linting and formatting)

```bash
# Check for issues
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/
```

### Type Checking

```bash
# Run mypy
mypy src/
```

## Project Structure

```
chuk-acp-agent/
├── src/chuk_acp_agent/    # Main package
│   ├── agent/             # Core agent abstractions
│   ├── capabilities/      # File system, terminal wrappers
│   ├── integrations/      # MCP, artifacts integration
│   └── middlewares/       # Cross-cutting concerns
├── examples/              # Example agents
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## Contributing Guidelines

### 1. Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Write docstrings for all public APIs (Google style)
- Keep lines under 100 characters
- Use ruff for formatting

### 2. Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common setup
- Test both success and error cases

### 3. Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Update examples if API changes
- Add inline comments for complex logic

### 4. Commits

- Write clear, descriptive commit messages
- Use conventional commits format:
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation only
  - `test:` Test changes
  - `refactor:` Code refactoring
  - `chore:` Maintenance tasks

Example:
```
feat: add streaming support to terminal execution

- Implement run_streaming() method
- Add async iterator for output lines
- Update documentation
```

### 5. Pull Requests

- Create a branch from `main`
- Make your changes
- Run tests and linters
- Submit PR with clear description
- Link related issues

## Adding New Features

### 1. Capabilities

To add a new capability (e.g., clipboard):

1. Create `src/chuk_acp_agent/capabilities/clipboard.py`
2. Implement wrapper using ACP protocol
3. Add to `Context` in `agent/context.py`
4. Write tests
5. Add example usage

### 2. Integrations

To add a new integration (e.g., artifacts):

1. Create `src/chuk_acp_agent/integrations/artifacts.py`
2. Implement integration logic
3. Add to `Context` or make available to agents
4. Write tests and examples

### 3. Middleware

To add middleware (e.g., tracing):

1. Create `src/chuk_acp_agent/middlewares/tracing.py`
2. Define middleware interface
3. Implement in `Agent` base class
4. Write tests and examples

## Release Process

(Maintainers only)

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v0.1.0 -m "Release 0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. Build and publish: `python -m build && twine upload dist/*`

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Contact maintainers for security issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
