.PHONY: dev install install-dev lint format type-check test test-cov pre-commit clean cdk-test

# Development server
dev:
	docker compose up -d
	open http://localhost:10120/docs

# Install dependencies
install:
	uv sync

install-dev:
	uv sync --all-extras

# Code quality
lint:
	uv run ruff check spotify_api

format:
	uv run ruff format spotify_api
	uv run ruff check --fix spotify_api

type-check:
	uv run mypy spotify_api

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=spotify_api --cov-report=term --cov-report=html

# Pre-commit
pre-commit:
	uv run pre-commit run --all-files

pre-commit-install:
	uv run pre-commit install

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true

# CDK
cdk-test:
	cd cdk && npm run test

# All checks
check: lint type-check test
