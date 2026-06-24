# CLAUDE.md

Guidance for working in this repo. Keep it short; only non-obvious things live here.

## What this is

FastAPI Shop — full-stack e-commerce demo.
- **backend/** — FastAPI, layered: `models → repositories → services → routes`. SQLAlchemy 2.0
  (`Mapped`/`mapped_column`), Pydantic v2, Alembic migrations, JWT admin auth (single admin from
  env), slowapi rate-limit on login, image upload. PostgreSQL in Docker, **SQLite for local dev/tests**.
- **frontend/** — Vue 3 (`<script setup>`), Vite, Pinia, Vue Router, Tailwind CSS v4. Storefront
  + `/admin` (JWT, router-guard). Visual style: brutalist "EMPIRE" (beige+red, Archivo/Space Mono).

## Tooling — non-obvious

- **Backend uses `uv`, not pip.** Always `uv run --frozen <cmd>` from `backend/`. Add deps with
  `uv add` / `uv add --dev`; never edit `pyproject.toml` deps by hand then expect pip.
- **Frontend uses npm** from `frontend/`.
- Dependencies are pinned via `uv.lock` / `package-lock.json`; CI runs `--frozen` / `npm ci`.

## Commands

Backend (from `backend/`):
- Tests: `uv run --frozen pytest` · Lint: `uv run --frozen ruff check .` · Types: `uv run --frozen mypy app`
- Migrations: `uv run --frozen alembic upgrade head`; new: `uv run --frozen alembic revision --autogenerate -m "..."`
- Seed demo data: `uv run --frozen python seed_data.py`

Frontend (from `frontend/`):
- `npm run dev` · `npm run build` · `npm run lint` · `npm run test` (Vitest unit) · `npm run test:e2e` (Playwright)

## Running locally — read this before launching

1. Backend (SQLite): `uv run --frozen alembic upgrade head && uv run --frozen python seed_data.py`,
   then `uv run --frozen uvicorn app.main:app --host 0.0.0.0 --port 8000`.
2. Frontend: `npm run dev` (Vite on 5173). `api.js` defaults to `http://localhost:8000/api`.

**Environment gotcha:** port **8000 is often occupied** on this machine by another service. When it
is, run the backend on **8010** and start Vite with `VITE_API_BASE_URL=http://localhost:8010/api npm run dev`
(the Playwright `webServer` inherits this env too). The Playwright MCP `--browser chromium` is registered
in local scope; for screenshots, navigate to `http://localhost:5173`.

E2E needs a running, seeded backend — unit tests (Vitest/pytest) do not (pytest uses an in-memory SQLite fixture).

## Frontend design system

- Tokens live in `frontend/src/assets/main.css` `@theme`: `--color-bg #e7e7e2`, `--color-surface`,
  `--color-ink #111`, `--color-accent #e11d2e`, `--color-border`, `--color-muted`, plus `--font-sans`
  (Archivo), `--font-black` (Archivo Black), `--font-mono` (Space Mono). Use Tailwind utilities like
  `bg-ink`, `text-accent`, `font-mono`, `.placeholder-hatch`.
- Global UI state (cart drawer + toast) is the **ui store** (`stores/ui.js`): `openCart/closeCart/cartOpen`,
  `showToast/toast`. Cart logic stays in `stores/cart.js`. Add-to-cart → `cart.addToCart(id, qty)` then
  `ui.showToast(...)`.
- Reusable components: `UspBar`, `AppHeader` (BAG → `ui.openCart`), `AppMarquee`, `AppFooter`,
  `AppToast`, `CartDrawer`, `CategoryCircle`, `ProductCard`.
- **E2E `data-test` hooks** (keep stable across visual changes): `add-to-cart`, `open-cart`,
  `cart-drawer`, `drawer-checkout`, `checkout`, `toast`.
- Admin views are Russian-labeled; E2E depends on labels `Логин`/`Пароль`/`Войти` and the
  `Добавить категорию` button — don't rename them.

## Conventions

- Feature work goes on a branch, then merge to `main` (CI runs on push + PRs to `main`). Small
  doc/fix commits have gone directly to `main`.
- Admin secrets come from env: `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` (bcrypt), `JWT_SECRET`.
  In `.env` / docker-compose the bcrypt hash **must escape `$` as `$$`** (compose interpolation);
  `deploy.sh` does this automatically.
- Specs/plans for larger work live in `docs/superpowers/`.
