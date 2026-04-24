.PHONY: dev api web db-up db-down db-up-brew db-down-brew migrate migration test test-api test-web lint clean setup

# Start everything (uses brew services by default)
dev: db-up-brew
	@echo "Starting Forge dev environment..."
	$(MAKE) -j2 api web

api:
	cd apps/api && .venv/bin/uvicorn app.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

# Database — Homebrew (default for local dev)
db-up-brew:
	brew services start postgresql@16 2>/dev/null || true
	brew services start redis 2>/dev/null || true
	@echo "Postgres and Redis running via Homebrew"

db-down-brew:
	brew services stop postgresql@16 2>/dev/null || true
	brew services stop redis 2>/dev/null || true

# Database — Docker (alternative)
db-up:
	docker compose up -d postgres redis minio

db-down:
	docker compose down

# Migrations
migrate:
	cd apps/api && .venv/bin/alembic upgrade head

migration:
	cd apps/api && .venv/bin/alembic revision --autogenerate -m "$(msg)"

# Testing
test: test-api test-web

test-api:
	cd apps/api && .venv/bin/pytest tests/ -v

test-web:
	cd apps/web && npx vitest run

# Linting
lint:
	cd apps/api && .venv/bin/ruff check .
	cd apps/web && npx eslint .

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf apps/web/.next
	rm -rf apps/api/.pytest_cache

# Initial setup
setup:
	cd apps/api && python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -e ".[dev]"
	cd apps/web && npm install
	@echo "Run 'make migrate' to set up the database"
