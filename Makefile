dev:
	docker compose up -d
	open http://localhost:10120/docs

cdk-test:
	cd cdk && npm run test

# uv commands
install:
	uv sync

install-dev:
	uv sync --all-extras

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy spotify_api
