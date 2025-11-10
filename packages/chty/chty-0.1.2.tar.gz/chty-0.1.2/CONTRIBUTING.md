# Contributing to chty

Thank you for your interest in contributing to chty! We welcome contributions from the community.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/chty.git
   cd chty
   ```
3. **Install dependencies**:
   ```bash
   uv pip install -e ".[dev,docs]"
   ```

## Making Changes

1. **Create a new branch** for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure:

   - Code follows the existing style
   - All tests pass: `uv run pytest`
   - New features include tests
   - Documentation is updated if needed

3. **Commit your changes**:

   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

4. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub from your fork to the main repository

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Keep PRs focused on a single feature or fix

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=chty

# Run specific test
uv run pytest tests/test_codegen.py
```

### Building Documentation

```bash
# Serve locally
uv run mkdocs serve

# Build static site
uv run mkdocs build
```

### Manual Testing

```bash
# Generate code
uv run python main.py generate examples/queries/*.sql -o examples/generated --db-url clickhouse://admin:admin@localhost:8123

# Validate code
uv run python main.py validate examples/generated/*.py --db-url clickhouse://admin:admin@localhost:8123
```

## Questions?

Feel free to open an issue for any questions or discussions.
