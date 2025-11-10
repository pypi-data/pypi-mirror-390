# Contributing

Thank you for considering contributing to `chty`!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Install development dependencies

```bash
git clone https://github.com/YOUR_USERNAME/chty.git
cd chty
uv pip install -e ".[dev,docs]"
```

## Development Workflow

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=chty

# Specific test
uv run pytest tests/test_codegen.py
```

### Code Quality

```bash
# Type checking
mypy chty/

# Linting
ruff check chty/

# Formatting
ruff format chty/
```

### Documentation

```bash
# Serve docs locally
uv run mkdocs serve

# Build docs
uv run mkdocs build
```

## Pull Request Process

1. Create a feature branch
2. Make your changes
3. Add tests
4. Update documentation
5. Run tests and linters
6. Submit PR

## Code Style

- Use Python 3.10+ features
- Type hints for all public APIs
- Docstrings for modules, classes, and functions
- Keep it simple and readable

## See Also

- [Architecture](architecture.md)
- [GitHub Repository](https://github.com/treygilliland/chty)
