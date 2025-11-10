.PHONY: help up down examples examples-with-db test lint format clean install bump-version

help:
	@echo "Available targets:"
	@echo "  make up                 - Start ClickHouse server (Docker)"
	@echo "  make down               - Stop ClickHouse server"
	@echo "  make regen-examples     - Regenerate example code (requires ClickHouse on localhost)"
	@echo "  make test               - Run tests"
	@echo "  make lint               - Run ruff linter"
	@echo "  make format             - Format code with ruff"
	@echo "  make clean              - Clean generated files and caches"
	@echo "  make install            - Install dependencies"
	@echo "  make update-version V=x.y.z - Update version (e.g., make update-version V=0.2.0)"

up:
	@echo "Starting ClickHouse server..."
	docker compose up -d
	@echo "Waiting for ClickHouse to be ready..."
	@sleep 5
	@echo "✓ ClickHouse is running at localhost:8123"
	@echo "  User: admin"
	@echo "  Password: admin"

down:
	@echo "Stopping ClickHouse server..."
	docker compose down
	@echo "✓ ClickHouse stopped"

regen-examples:
	@echo "Regenerating example code..."
	uv run chty generate examples/queries/ -o examples/generated/ --db-url clickhouse://admin:admin@localhost:8123
	@echo "✓ Example code regenerated"

test:
	uv run python -m pytest -v

lint:
	uvx ruff check .

format:
	uvx ruff format .
	uvx ruff check --fix .

clean:
	@echo "Cleaning generated files and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

install:
	uv sync

update-version:
	@if [ -z "$(V)" ]; then \
		echo "Error: Version not specified. Usage: make bump-version V=x.y.z"; \
		exit 1; \
	fi
	@echo "Bumping version to $(V)..."
	@sed -i '' 's/^version = ".*"/version = "$(V)"/' pyproject.toml
	@rm -rf chty.egg-info
	@uv pip install -e . > /dev/null 2>&1
	@echo "✓ Version bumped to $(V)"
