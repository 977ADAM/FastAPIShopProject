# Spec: Re-profile FastAPI Shop into a stationery store ("Канцелярия №1")

**Date:** 2026-06-29
**Status:** Approved (design); ready for implementation planning
**Approach:** Variant 1 — layered bottom-up (backend → data → frontend → tests)

## 1. Goal

Re-profile the generic "shop everything" demo into a focused **stationery store for
school and office** ("всё для школы и офиса"), Russian-language storefront with prices in
**₽**. This replaces the brutalist EMPIRE visual with a new clean "warm school" design
system and adds stationery-specific product fields. Backend architecture
(`models → repositories → services → routes`), auth, cart, orders, rate-limit and image
upload are reused unchanged except where listed below.

Brand name: **Канцелярия №1**.

## 2. Decisions

| Topic | Decision |
|-------|----------|
| Niche | Stationery — school + office supplies. |
| Depth | Rebrand + new seed data **+ domain fields** (brand, sku, unit, pack_qty). No new store features (no search/filters/B2B/discounts). |
| Language / currency | **Russian + ₽** on the storefront (admin already Russian). Not i18n — Russian only, copy inline. |
| Visual style | New **clean "warm school"** direction (Direction B), replacing brutalism. |
| Palette | bg `#f7f1e3`, surface `#ffffff`, ink `#1f2a44`, accent `#f0b429`, sale/price `#d64545`, border `#e7ddc7`, muted `#8a7f63`. |
| Typography | **Rubik** only (headings 800, body 400/500) — rounded sans, latin+cyrillic. No serif, no mono. |
| Shape language | Soft rounded corners (`rounded-xl`), light shadows, thin borders. Remove brutalist hard borders / hard-shadow press effect. |

### Superseded
The EMPIRE brutalist redesign (`2026-06-24-empire-visual-redesign-design.md`) visual layer
is **superseded** by this clean "warm school" direction. The Tailwind v4 `@theme` token
approach carries over; the token *values*, fonts, and shape language are replaced.

## 3. Backend — data model & migration

### 3.1 `Product` model (`backend/app/models/product.py`)
Add four columns (all backwards-compatible):

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `brand` | `str \| None` | `NULL` | e.g. "Pilot", "ErichKrause" |
| `sku` | `str \| None` | `NULL` | article number, indexed like `name` |
| `unit` | `str` | `"шт"` | values: `шт` / `упаковка`; `server_default="шт"` |
| `pack_qty` | `int` | `1` | quantity per pack; `server_default="1"` |

### 3.2 Schemas (`backend/app/schemas/product.py`)
- `ProductBase`: add `brand`, `sku`, `unit` (default `"шт"`), `pack_qty` (default `1`, `ge=1`).
- `ProductUpdate`: same four as optional.
- `ProductResponse`: expose all four.
- **Lower `name` `min_length` from 5 → 2** (stationery names like "Клей ПВА", "Ластик").
  Applies to `ProductBase.name` and `ProductUpdate.name`.

### 3.3 Migration
- New Alembic revision `add_stationery_fields` (third revision).
- `op.add_column` × 4 with `server_default` for `unit`/`pack_qty` so existing rows backfill;
  use SQLite-friendly batch mode (consistent with existing migrations).

### 3.4 Repositories / services
- `product_repository` / `product_service` mostly pass the model through. Verify
  `product_service.create/update` doesn't hardcode a field allow-list; if it does, add the
  four new fields.
- Unchanged: `Order`/`OrderItem`, cart, auth, rate-limit, image upload.

## 4. Data — categories & seed

Rewrite `backend/seed_data.py` for stationery. Keep the existing "skip if already seeded"
guard. Prices in ₽, descriptions in Russian.

### 4.1 Categories
| Name | slug |
|------|------|
| Письменные принадлежности | `pismennye` |
| Тетради и бумага | `bumaga` |
| Школьные товары | `shkolnye` |
| Офисные принадлежности | `ofisnye` |
| Рисование и творчество | `tvorchestvo` |

### 4.2 Products
~4–5 products per category (~22 total), each with the new fields. Reference anchor items:

| Name | brand | sku | price ₽ | unit | pack_qty | category |
|------|-------|-----|---------|------|----------|----------|
| Ручка гелевая Pilot G-2 | Pilot | PIL-G2-BL | 89 | шт | 1 | pismennye |
| Тетрадь 48 л. в клетку | ErichKrause | EK-48-KL | 65 | шт | 1 | bumaga |
| Бумага А4 «SvetoCopy» 500 л. | SvetoCopy | SC-A4-500 | 540 | упаковка | 500 | bumaga |
| Пенал школьный | — | PEN-SCH-01 | 340 | шт | 1 | shkolnye |
| Степлер №24/6 | KW-trio | KW-24-6 | 410 | шт | 1 | ofisnye |
| Краски акварельные 24 цв. | Гамма | GAM-AQ-24 | 210 | шт | 1 | tvorchestvo |

Images: keep Unsplash URLs (pen/notebook/office queries); missing imagery falls back to
`.placeholder-hatch`. The full ~22-item list is authored during implementation.

## 5. Frontend — design system & reskin

### 5.1 Tokens (`frontend/src/assets/main.css`)
Replace EMPIRE `@theme` values with palette in §2:
```
--color-bg: #f7f1e3;   --color-surface: #ffffff;
--color-ink: #1f2a44;  --color-accent: #f0b429;  --color-accent-ink: #1f2a44;
--color-sale: #d64545; --color-border: #e7ddc7;  --color-muted: #8a7f63;
--font-sans: 'Rubik', system-ui, sans-serif;
```
- `index.html`: load **Rubik** (400/500/700/800, latin+cyrillic) via Google Fonts; remove
  Archivo / Archivo Black / Space Mono.
- Remove brutalist treatments: hard 2px borders and hard-shadow `.emp-press` → soft
  `rounded-xl`, light shadow, thin `--color-border`. Recolor `.placeholder-hatch` to cream.
- **`font-mono` is removed** — replace every `font-mono` usage (USP, marquee, prices,
  labels) with `font-sans` + letter-spacing, per component.

### 5.2 Component reskin
Re-skin to the new tokens while **preserving `data-test` hooks** (`add-to-cart`,
`open-cart`, `cart-drawer`, `drawer-checkout`, `checkout`, `toast`):
`AppHeader`, `AppFooter`, `UspBar`, `AppMarquee`, `AppToast`, `CartDrawer`, `CartItem`,
`CategoryCircle`, `ProductCard`, `HomePage`, `ProductDetailPage`, `CartPage`, and the
`/admin` views.

### 5.3 Russian copy & ₽
- All hardcoded storefront English copy → Russian (USP bar, marquee, footer, hero:
  "Соберись к учёбе" / "Всё для школы и офиса", buttons, empty/loading states).
- Price rendering `$` → `₽` after the amount, format `1 250 ₽`. Add a small price-format
  helper and use it everywhere a price renders.

### 5.4 New fields in UI
- `ProductCard`: small brand label on top; show unit next to price when `упаковка`
  (e.g. "540 ₽ / упак. 500 л.").
- `ProductDetailPage`: brand, sku (артикул), unit/pack in a characteristics block.
- Admin product form: inputs for `brand`, `sku`, `unit`, `pack_qty`.

### 5.5 Branding
Logo/name → **Канцелярия №1** in `AppHeader` and `AppFooter`.

## 6. Docs

Update the **design-system section of `CLAUDE.md`** (currently describes EMPIRE tokens,
Archivo/Space Mono, mono utilities) to reflect the new palette, Rubik, and shape language.
Keep the `data-test` hooks and Russian admin-label notes.

## 7. Testing

### Backend (pytest)
- New fields default-backfill → existing tests should pass; verify.
- Add: create/update round-trip asserting `brand/sku/unit/pack_qty`.
- Verify `name.min_length=2` change (a 2-char name validates; empty still rejected).
- Run against the rewritten Russian seed.
- `ruff check .` and `mypy app` green.

### Frontend (Vitest unit)
- Update `ProductCard.spec` (₽ not `$`, brand/unit, Russian strings), `CartDrawer.spec`,
  `AppToast.spec` where text-coupled. `data-test` selectors unchanged.

### E2E (Playwright)
- `storefront.spec` / `cart.spec`: update text assertions to Russian/₽; `data-test`
  selectors stay.
- `admin.spec`: labels `Логин`/`Пароль`/`Войти`/`Добавить категорию` **unchanged**; verify
  reskin didn't break selectors.

### Final verification
`npm run lint`, `npm run build`, `npm run test`, then e2e against a running seeded backend
(port 8010 per CLAUDE.md when 8000 is occupied).

## 8. Out of scope (YAGNI)

Search, category/price filters, B2B/wholesale flows, volume discounts, multi-language i18n,
product variants/colors, country-of-origin field, customer accounts. Order/cart/auth flows
unchanged.
