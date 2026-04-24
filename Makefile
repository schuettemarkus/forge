.PHONY: dev api web db-up db-down migrate migration test test-api test-web lint clean setup

dev: db-up
	@echo "Starting Forge dev environment..."
	$(MAKE) -j2 api web

api:
	cd apps/api && uvicorn app.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

db-up:
	docker compose up -d postgres redis minio

db-down:
	docker compose down

migrate:
	cd apps/api && alembic upgrade head

migration:
	cd apps/api && alembic revision --autogenerate -m "$(msg)"

test: test-api test-web

test-api:
	cd apps/api && pytest

test-web:
	cd apps/web && npx vitest run

lint:
	cd apps/api && ruff check .
	cd apps/web && npx eslint .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf apps/web/node_modules apps/web/.next
	rm -rf apps/api/.venv

setup:
	cd apps/api && python -m venv .venv && .venv/bin/pip install -e ".[dev]"
	cd apps/web && npm install
