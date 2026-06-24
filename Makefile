# FastAPI Shop — developer command shortcuts.
# Backend uses `uv run --frozen` (from backend/); frontend uses npm (from frontend/).
# Port 8000 is often occupied on this machine — override with `make back-run PORT=8010`.

BACKEND  := backend
FRONTEND := frontend
PORT     ?= 8000
UV       := uv run --frozen

.DEFAULT_GOAL := help

# ---- Meta ----------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---- Setup ---------------------------------------------------------------

.PHONY: install
install: install-back install-front ## Install all dependencies

.PHONY: install-back
install-back: ## Sync backend deps (uv)
	cd $(BACKEND) && uv sync --frozen

.PHONY: install-front
install-front: ## Install frontend deps (npm ci)
	cd $(FRONTEND) && npm ci

# ---- Backend -------------------------------------------------------------

.PHONY: back-run
back-run: ## Run backend (uvicorn). Override port: make back-run PORT=8010
	cd $(BACKEND) && $(UV) uvicorn app.main:app --host 0.0.0.0 --port $(PORT)

.PHONY: back-test
back-test: ## Run backend tests (pytest)
	cd $(BACKEND) && $(UV) pytest

.PHONY: back-lint
back-lint: ## Lint backend (ruff)
	cd $(BACKEND) && $(UV) ruff check .

.PHONY: back-types
back-types: ## Type-check backend (mypy)
	cd $(BACKEND) && $(UV) mypy app

.PHONY: back-check
back-check: back-lint back-types back-test ## Lint + types + tests

.PHONY: migrate
migrate: ## Apply DB migrations (alembic upgrade head)
	cd $(BACKEND) && $(UV) alembic upgrade head

.PHONY: migration
migration: ## Create a migration: make migration m="message"
	cd $(BACKEND) && $(UV) alembic revision --autogenerate -m "$(m)"

.PHONY: seed
seed: ## Seed demo data
	cd $(BACKEND) && $(UV) python seed_data.py

.PHONY: db-reset
db-reset: migrate seed ## Migrate then seed demo data

# ---- Frontend ------------------------------------------------------------

.PHONY: front-run
front-run: ## Run Vite dev server (5173)
	cd $(FRONTEND) && npm run dev

.PHONY: front-build
front-build: ## Build frontend for production
	cd $(FRONTEND) && npm run build

.PHONY: front-lint
front-lint: ## Lint frontend (eslint)
	cd $(FRONTEND) && npm run lint

.PHONY: front-test
front-test: ## Run frontend unit tests (vitest)
	cd $(FRONTEND) && npm run test

.PHONY: front-e2e
front-e2e: ## Run frontend e2e tests (playwright; needs seeded backend)
	cd $(FRONTEND) && npm run test:e2e

.PHONY: front-check
front-check: front-lint front-test ## Lint + unit tests

# ---- Docker (compose: db, backend, frontend, nginx, certbot) -------------

COMPOSE := docker compose

.PHONY: up
up: ## Start the full stack in the background
	$(COMPOSE) up -d

.PHONY: up-build
up-build: ## Rebuild images and start the stack
	$(COMPOSE) up -d --build

.PHONY: down
down: ## Stop and remove containers
	$(COMPOSE) down

.PHONY: ps
ps: ## Show compose service status
	$(COMPOSE) ps

.PHONY: logs
logs: ## Tail logs (all services, or: make logs s=backend)
	$(COMPOSE) logs -f $(s)

.PHONY: docker-build
docker-build: ## Build all images
	$(COMPOSE) build

.PHONY: docker-migrate
docker-migrate: ## Run alembic migrations in the backend container
	$(COMPOSE) exec backend uv run --frozen --no-dev alembic upgrade head

.PHONY: docker-seed
docker-seed: ## Seed demo data in the backend container
	$(COMPOSE) exec backend uv run --frozen --no-dev python seed_data.py

.PHONY: backup
backup: ## Back up the Postgres DB to ./backups/
	./scripts/backup.sh

.PHONY: restore
restore: ## Restore the DB from a dump: make restore f=backups/dump.sql.gz
	./scripts/restore.sh $(f)

.PHONY: deploy
deploy: ## Run the VPS deploy script
	./deploy.sh

# ---- Combined ------------------------------------------------------------

.PHONY: test
test: back-test front-test ## Run backend + frontend unit tests

.PHONY: lint
lint: back-lint front-lint ## Lint backend + frontend

.PHONY: check
check: back-check front-check ## Full check: lint, types, tests (both)
