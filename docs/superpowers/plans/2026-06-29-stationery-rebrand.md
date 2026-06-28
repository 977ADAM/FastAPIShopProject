# Stationery Rebrand ("Канцелярия №1") Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-profile the generic FastAPI Shop demo into a Russian-language school/office stationery store ("Канцелярия №1") with a clean "warm school" design system, ₽ pricing, and stationery product fields.

**Architecture:** Layered bottom-up (Variant 1): backend model + migration → seed data → frontend design-system tokens → component reskin + Russian copy → tests + docs. Backend layers `models → repositories → services → routes` are reused; repo/service pass the model through (`Product(**model_dump())`, `model_dump(exclude_unset=True)`), so new fields flow without repo/service edits.

**Tech Stack:** FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, `uv` (backend); Vue 3 `<script setup>`, Vite, Pinia, Tailwind CSS v4, Vitest, Playwright (frontend).

**Spec:** `docs/superpowers/specs/2026-06-29-stationery-rebrand-design.md`

**Conventions:** Backend commands run from `backend/` with `uv run --frozen`. Frontend from `frontend/` with `npm`. Work on a branch off `main`.

---

## File map

**Backend**
- Modify `backend/app/models/product.py` — add `brand`, `sku`, `unit`, `pack_qty`.
- Modify `backend/app/schemas/product.py` — new fields + `name` min_length 5→2.
- Create `backend/alembic/versions/<rev>_add_stationery_fields.py` — migration.
- Rewrite `backend/seed_data.py` — stationery categories + products.
- Modify `backend/tests/test_features.py` — add domain-field + short-name tests.

**Frontend**
- Modify `frontend/index.html` — load Rubik, drop Archivo/Space Mono.
- Modify `frontend/src/assets/main.css` — new `@theme` tokens, soft shapes.
- Create `frontend/src/utils/format.js` — `formatPrice()` helper.
- Modify components/views (reskin + Russian + ₽): `ProductCard.vue`, `ProductDetailPage.vue`, `CartPage.vue`, `CartItem.vue`, `CartDrawer.vue`, `AppHeader.vue`, `AppFooter.vue`, `UspBar.vue`, `AppMarquee.vue`, `HomePage.vue`, `CategoryCircle.vue`, `AppToast.vue`, and `views/admin/*`.
- Modify specs: `ProductCard.spec.js`, e2e `storefront.spec.js`, `cart.spec.js`.

**Docs**
- Modify `CLAUDE.md` — design-system section.

---

## Phase A — Backend model, schema, migration

### Task 1: Add stationery fields to the Product model

**Files:**
- Modify: `backend/app/models/product.py`

- [ ] **Step 1: Add the four columns**

In `backend/app/models/product.py`, after the `stock` column (line 24) and before `created_at`, add:

```python
    brand: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sku: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    unit: Mapped[str] = mapped_column(
        String, nullable=False, default="шт", server_default="шт"
    )
    pack_qty: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
```

(`String`, `Integer`, `Optional` are already imported.)

- [ ] **Step 2: Verify it imports**

Run: `cd backend && uv run --frozen python -c "from app.models.product import Product; print(Product.__table__.columns.keys())"`
Expected: list includes `brand`, `sku`, `unit`, `pack_qty`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/models/product.py
git commit -m "feat(backend): add brand/sku/unit/pack_qty to Product model"
```

---

### Task 2: Extend product schemas and lower name min_length

**Files:**
- Modify: `backend/app/schemas/product.py`
- Test: `backend/tests/test_features.py`

- [ ] **Step 1: Write failing tests**

Append to `backend/tests/test_features.py`:

```python
def test_create_product_with_stationery_fields(client, seeded_db):
    category_id = seeded_db["category"].id
    payload = {
        "name": "Ручка гелевая Pilot G-2",
        "description": "Синяя, 0.7 мм",
        "price": 89,
        "category_id": category_id,
        "brand": "Pilot",
        "sku": "PIL-G2-BL",
        "unit": "упаковка",
        "pack_qty": 12,
    }
    resp = client.post("/api/products", json=payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["brand"] == "Pilot"
    assert body["sku"] == "PIL-G2-BL"
    assert body["unit"] == "упаковка"
    assert body["pack_qty"] == 12


def test_product_defaults_unit_and_pack_qty(client, seeded_db):
    category_id = seeded_db["category"].id
    payload = {"name": "Ластик", "price": 25, "category_id": category_id}
    resp = client.post("/api/products", json=payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["unit"] == "шт"
    assert body["pack_qty"] == 1
    assert body["brand"] is None


def test_short_product_name_is_allowed(client, seeded_db):
    category_id = seeded_db["category"].id
    payload = {"name": "Клей", "price": 60, "category_id": category_id}
    resp = client.post("/api/products", json=payload)
    assert resp.status_code == 201, resp.text
```

> Note: confirm the create route path/verb. If products are created at a different path (check `backend/app/routes/products.py`), adjust `client.post("/api/products", ...)` and the expected status (200 vs 201) to match existing product tests in `test_app.py`/`test_admin.py`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && uv run --frozen pytest tests/test_features.py -k "stationery or defaults or short_product_name" -v`
Expected: FAIL (schema rejects unknown `brand`/`sku`/`unit`/`pack_qty`, and `"Клей"`/`"Ластик"` fail `min_length=5`).

- [ ] **Step 3: Update schemas**

In `backend/app/schemas/product.py`:

Replace `ProductBase` (lines 9–17) with:

```python
class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200,
                            description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0,
                            description="Product price(must be greater than 0")
    category_id: int = Field(..., description='Category ID')
    image_url: Optional[str] = Field(None, description='Product image URL')
    stock: int = Field(0, ge=0, description='Available stock')
    brand: Optional[str] = Field(None, description='Brand name')
    sku: Optional[str] = Field(None, description='Article number')
    unit: str = Field("шт", description='Unit: шт / упаковка')
    pack_qty: int = Field(1, ge=1, description='Quantity per pack')
```

Replace `ProductUpdate` (lines 22–28) with:

```python
class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    brand: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    pack_qty: Optional[int] = Field(None, ge=1)
```

In `ProductResponse` (lines 30–41), add after `stock: int`:

```python
    brand: Optional[str]
    sku: Optional[str]
    unit: str
    pack_qty: int
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && uv run --frozen pytest tests/test_features.py -k "stationery or defaults or short_product_name" -v`
Expected: PASS.

- [ ] **Step 5: Run the full backend suite + lint + types**

Run: `cd backend && uv run --frozen pytest && uv run --frozen ruff check . && uv run --frozen mypy app`
Expected: all green. (Existing tests still pass — new fields have defaults; conftest's `Product(...)` without them relies on model defaults.)

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas/product.py backend/tests/test_features.py
git commit -m "feat(backend): expose stationery fields in schemas; allow short names"
```

---

### Task 3: Alembic migration for the new columns

**Files:**
- Create: `backend/alembic/versions/<rev>_add_stationery_fields.py` (generated)

- [ ] **Step 1: Autogenerate the migration**

Run: `cd backend && uv run --frozen alembic revision --autogenerate -m "add stationery fields"`
Expected: a new file in `alembic/versions/` containing `op.add_column('products', ...)` for `brand`, `sku`, `unit`, `pack_qty`.

- [ ] **Step 2: Verify the generated upgrade/downgrade**

Open the generated file. Confirm `upgrade()` adds all four columns and `unit`/`pack_qty` carry `server_default` so existing rows backfill. It should resemble:

```python
def upgrade() -> None:
    op.add_column('products', sa.Column('brand', sa.String(), nullable=True))
    op.add_column('products', sa.Column('sku', sa.String(), nullable=True))
    op.add_column('products', sa.Column('unit', sa.String(), server_default='шт', nullable=False))
    op.add_column('products', sa.Column('pack_qty', sa.Integer(), server_default='1', nullable=False))
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_column('products', 'pack_qty')
    op.drop_column('products', 'unit')
    op.drop_column('products', 'sku')
    op.drop_column('products', 'brand')
```

If autogenerate omitted `server_default` on `unit`/`pack_qty`, add it by hand (existing rows would otherwise violate `NOT NULL`).

- [ ] **Step 3: Apply the migration**

Run: `cd backend && uv run --frozen alembic upgrade head`
Expected: completes without error.

- [ ] **Step 4: Verify schema round-trips (downgrade then upgrade)**

Run: `cd backend && uv run --frozen alembic downgrade -1 && uv run --frozen alembic upgrade head`
Expected: both succeed.

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat(backend): migration adding stationery product fields"
```

---

## Phase B — Seed data

### Task 4: Rewrite seed_data.py for stationery

**Files:**
- Modify: `backend/seed_data.py`

- [ ] **Step 1: Replace `create_categories` data**

In `backend/seed_data.py`, replace the `categories_data` list inside `create_categories` with:

```python
    categories_data = [
        {"name": "Письменные принадлежности", "slug": "pismennye"},
        {"name": "Тетради и бумага", "slug": "bumaga"},
        {"name": "Школьные товары", "slug": "shkolnye"},
        {"name": "Офисные принадлежности", "slug": "ofisnye"},
        {"name": "Рисование и творчество", "slug": "tvorchestvo"},
    ]
```

- [ ] **Step 2: Replace `products_data` with stationery items**

Replace the entire `products_data` list inside `create_products` with the following (~22 items). Keep the trailing loop `for product_data in products_data: ... Product(stock=100, **product_data)`. Note each dict now includes `brand`/`sku`/`unit`/`pack_qty`:

```python
    products_data = [
        # Письменные принадлежности
        {"name": "Ручка гелевая Pilot G-2", "description": "Гелевая ручка 0.7 мм, синие чернила. Плавное письмо, удобный грип.", "price": 89, "brand": "Pilot", "sku": "PIL-G2-BL", "unit": "шт", "pack_qty": 1, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400"},
        {"name": "Карандаш чернографитный HB", "description": "Классический карандаш твёрдости HB, заточенный. Набор 12 шт.", "price": 145, "brand": "Koh-i-Noor", "sku": "KIN-HB-12", "unit": "упаковка", "pack_qty": 12, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1587145820266-a5951ee6f620?w=400"},
        {"name": "Маркер текстовый набор 4 цв.", "description": "Флуоресцентные текстовыделители, скошенный наконечник. 4 цвета.", "price": 210, "brand": "Stabilo", "sku": "STB-BOSS-4", "unit": "упаковка", "pack_qty": 4, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400"},
        {"name": "Ручка шариковая синяя", "description": "Шариковая ручка 0.5 мм, экономичный расход. Упаковка 50 шт.", "price": 390, "brand": "ErichKrause", "sku": "EK-R301-50", "unit": "упаковка", "pack_qty": 50, "category_id": categories["pismennye"].id, "image_url": "https://images.unsplash.com/photo-1625480860249-be231d1e1d0f?w=400"},

        # Тетради и бумага
        {"name": "Тетрадь 48 л. в клетку", "description": "Тетрадь на скрепке, обложка картон, клетка. Плотная бумага.", "price": 65, "brand": "ErichKrause", "sku": "EK-48-KL", "unit": "шт", "pack_qty": 1, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=400"},
        {"name": "Бумага А4 «SvetoCopy» 500 л.", "description": "Офисная бумага для печати, белизна 146% CIE, плотность 80 г/м².", "price": 540, "brand": "SvetoCopy", "sku": "SC-A4-500", "unit": "упаковка", "pack_qty": 500, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1568871391541-1d62a0d54c89?w=400"},
        {"name": "Блокнот на пружине А5", "description": "Блокнот 80 листов, твёрдая обложка, перфорация. Клетка.", "price": 230, "brand": "Hatber", "sku": "HAT-A5-80", "unit": "шт", "pack_qty": 1, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=400"},
        {"name": "Стикеры клейкие 76×76 мм", "description": "Самоклеящиеся листки, неоновые цвета, 100 листов в блоке.", "price": 120, "brand": "Global Notes", "sku": "GN-76-100", "unit": "упаковка", "pack_qty": 100, "category_id": categories["bumaga"].id, "image_url": "https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=400"},

        # Школьные товары
        {"name": "Пенал школьный", "description": "Пенал на молнии, два отделения, прочный текстиль.", "price": 340, "brand": "Brauberg", "sku": "BRG-PEN-01", "unit": "шт", "pack_qty": 1, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1546548970-71785318a17b?w=400"},
        {"name": "Рюкзак школьный", "description": "Ортопедическая спинка, светоотражатели, два больших отделения.", "price": 2490, "brand": "Brauberg", "sku": "BRG-BAG-22", "unit": "шт", "pack_qty": 1, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"},
        {"name": "Дневник школьный", "description": "Дневник в твёрдой обложке, 48 листов, справочный материал.", "price": 180, "brand": "Hatber", "sku": "HAT-DN-48", "unit": "шт", "pack_qty": 1, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400"},
        {"name": "Обложки для тетрадей 20 шт.", "description": "Универсальные плотные обложки ПВХ, набор 20 штук.", "price": 95, "brand": "ErichKrause", "sku": "EK-OBL-20", "unit": "упаковка", "pack_qty": 20, "category_id": categories["shkolnye"].id, "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400"},

        # Офисные принадлежности
        {"name": "Степлер №24/6", "description": "Металлический степлер до 20 листов, скобы 24/6.", "price": 410, "brand": "KW-trio", "sku": "KW-24-6", "unit": "шт", "pack_qty": 1, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1612599316791-451087c7ff00?w=400"},
        {"name": "Папка-регистратор 75 мм", "description": "Архивная папка с арочным механизмом, ламинированный картон.", "price": 320, "brand": "Brauberg", "sku": "BRG-REG-75", "unit": "шт", "pack_qty": 1, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1568667256549-094345857637?w=400"},
        {"name": "Скрепки канцелярские 28 мм", "description": "Металлические скрепки, никелированные, 100 шт. в упаковке.", "price": 55, "brand": "ErichKrause", "sku": "EK-SKR-100", "unit": "упаковка", "pack_qty": 100, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1456735190827-d1262f71b8a3?w=400"},
        {"name": "Лоток для бумаг горизонтальный", "description": "Пластиковый лоток-сетка для документов, штабелируемый.", "price": 260, "brand": "Brauberg", "sku": "BRG-LOT-H", "unit": "шт", "pack_qty": 1, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400"},
        {"name": "Файлы-вкладыши А4 100 шт.", "description": "Перфорированные прозрачные файлы, плотность 35 мкм.", "price": 240, "brand": "ErichKrause", "sku": "EK-FL-100", "unit": "упаковка", "pack_qty": 100, "category_id": categories["ofisnye"].id, "image_url": "https://images.unsplash.com/photo-1583521214690-73421a1829a9?w=400"},

        # Рисование и творчество
        {"name": "Краски акварельные 24 цв.", "description": "Медовая акварель 24 цвета с кистью, яркие пигменты.", "price": 210, "brand": "Гамма", "sku": "GAM-AQ-24", "unit": "шт", "pack_qty": 1, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400"},
        {"name": "Пластилин 12 цветов", "description": "Мягкий пластилин, не липнет к рукам, стек в комплекте.", "price": 150, "brand": "Луч", "sku": "LUCH-PL-12", "unit": "упаковка", "pack_qty": 12, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1499744937866-d7e566a20a61?w=400"},
        {"name": "Цветная бумага А4 16 цв.", "description": "Двусторонняя цветная бумага, 16 листов, для аппликаций.", "price": 110, "brand": "Hatber", "sku": "HAT-CB-16", "unit": "упаковка", "pack_qty": 16, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1502691876148-a84978e59af8?w=400"},
        {"name": "Кисти художественные набор 5 шт.", "description": "Синтетические кисти разных размеров для красок.", "price": 175, "brand": "Гамма", "sku": "GAM-KS-5", "unit": "упаковка", "pack_qty": 5, "category_id": categories["tvorchestvo"].id, "image_url": "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400"},
    ]
```

Also update the module docstring (lines 2–5) to say it seeds stationery demo data.

- [ ] **Step 3: Seed a fresh DB and verify**

Run: `cd backend && rm -f shop.db && uv run --frozen alembic upgrade head && uv run --frozen python seed_data.py`
Expected: prints "Created 5 categories" and "Created 22 products", no errors.

- [ ] **Step 4: Spot-check the data via the API**

Run: `cd backend && uv run --frozen python -c "from app.database import SessionLocal; from app.models.product import Product; db=SessionLocal(); p=db.query(Product).first(); print(p.name, p.brand, p.unit, p.pack_qty)"`
Expected: prints a Russian product name with brand/unit/pack_qty populated.

- [ ] **Step 5: Commit**

```bash
git add backend/seed_data.py
git commit -m "feat(backend): stationery categories and seed products"
```

---

## Phase C — Frontend design-system foundation

### Task 5: Swap fonts to Rubik

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: Replace the Google Fonts link and title**

In `frontend/index.html`, set `<title>` (line 7) to `Канцелярия №1` and replace the font `<link>` (lines 10–13) with:

```html
    <link
      href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700;800&display=swap&subset=cyrillic,latin"
      rel="stylesheet"
    />
```

Also set `<html lang="ru">` (line 2).

- [ ] **Step 2: Verify dev server boots**

Run: `cd frontend && npm run build`
Expected: build succeeds (no broken references).

- [ ] **Step 3: Commit**

```bash
git add frontend/index.html
git commit -m "chore(frontend): load Rubik font, set ru lang and title"
```

---

### Task 6: New design-system tokens

**Files:**
- Modify: `frontend/src/assets/main.css`

- [ ] **Step 1: Replace the `@theme` block**

In `frontend/src/assets/main.css`, replace the `@theme { ... }` block (lines 3–18) with:

```css
@theme {
  --color-bg: #f7f1e3;
  --color-surface: #ffffff;
  --color-ink: #1f2a44;
  --color-accent: #f0b429;
  --color-accent-ink: #1f2a44;
  --color-sale: #d64545;
  --color-border: #e7ddc7;
  --color-muted: #8a7f63;
  --color-success: #16a34a;
  --color-warning: #f59e0b;

  --font-sans: 'Rubik', system-ui, sans-serif;
}
```

- [ ] **Step 2: Recolor the placeholder hatch**

Replace the `.placeholder-hatch` rule with a cream-toned version:

```css
.placeholder-hatch {
  background: repeating-linear-gradient(45deg, #efe7d3 0 12px, #e7ddc7 12px 24px);
}
```

- [ ] **Step 3: Verify the build**

Run: `cd frontend && npm run build`
Expected: succeeds. (Utilities like `font-mono`/`font-black` referencing removed tokens still compile as Tailwind classes; they are removed per-component in Phase D.)

- [ ] **Step 4: Commit**

```bash
git add frontend/src/assets/main.css
git commit -m "feat(frontend): warm-school design tokens (cream/navy/yellow)"
```

---

### Task 7: Price-format helper

**Files:**
- Create: `frontend/src/utils/format.js`
- Test: `frontend/src/utils/format.spec.js`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/utils/format.spec.js`:

```js
import { describe, it, expect } from 'vitest'
import { formatPrice } from '@/utils/format'

describe('formatPrice', () => {
  it('appends ₽ and groups thousands', () => {
    expect(formatPrice(1250)).toBe('1 250 ₽')
  })
  it('renders whole rubles without decimals', () => {
    expect(formatPrice(89.0)).toBe('89 ₽')
  })
  it('handles zero and undefined', () => {
    expect(formatPrice(0)).toBe('0 ₽')
    expect(formatPrice(undefined)).toBe('0 ₽')
  })
})
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd frontend && npm run test -- --run format`
Expected: FAIL (module not found).

- [ ] **Step 3: Implement the helper**

Create `frontend/src/utils/format.js`:

```js
// Formats a numeric amount as Russian rubles, e.g. 1250 -> "1 250 ₽".
// Uses a regular space as the grouping separator for predictable test output.
export function formatPrice(value) {
  const n = Number(value) || 0
  const grouped = Math.round(n)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return `${grouped} ₽`
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `cd frontend && npm run test -- --run format`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/utils/format.js frontend/src/utils/format.spec.js
git commit -m "feat(frontend): formatPrice helper for ₽ display"
```

---

## Phase D — Reskin + Russian copy + new fields

> For every task in this phase: replace `font-mono` utility classes with `font-sans` plus letter spacing (`tracking-wide`/`tracking-wider`) where the spacing reads well; replace hard 2px borders with `border` + `border-border`; round cards/buttons with `rounded-xl`; swap any `bg-ink ... text-white` CTA to keep `bg-ink text-white` (navy on cream still reads) and use `bg-accent text-ink` for the primary "В корзину" action. Keep all `data-test` attributes byte-for-byte. After each task, run `npm run build` and the relevant unit spec.

### Task 8: Reskin ProductCard + update its spec

**Files:**
- Modify: `frontend/src/components/ProductCard.vue`
- Modify: `frontend/src/components/ProductCard.spec.js`

- [ ] **Step 1: Update the spec first (failing)**

In `frontend/src/components/ProductCard.spec.js`, change the `product` fixture (lines 8–15) to Russian/stationery and add brand/unit:

```js
const product = {
  id: 1,
  name: 'Ручка гелевая Pilot G-2',
  price: 89,
  image_url: 'http://example.com/img.jpg',
  stock: 5,
  brand: 'Pilot',
  unit: 'шт',
  pack_qty: 1,
  category: { id: 1, name: 'Письменные принадлежности' },
}
```

Replace the first test body (lines 28–33) with:

```js
  it('renders name, category, brand and ₽ price', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Ручка гелевая Pilot G-2')
    expect(wrapper.text()).toContain('Письменные принадлежности')
    expect(wrapper.text()).toContain('Pilot')
    expect(wrapper.text()).toContain('89 ₽')
  })
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd frontend && npm run test -- --run ProductCard`
Expected: FAIL (card renders `$89.00`, no brand).

- [ ] **Step 3: Reskin the component**

Replace `frontend/src/components/ProductCard.vue` `<template>` and `<script setup>` price/brand bits. Key changes: import `formatPrice`; show brand label; use `formatPrice(product.price)`; Russian button text; show unit when packaged; soft shape. New file:

```vue
<template>
  <div class="emp-card rounded-xl border border-border bg-surface overflow-hidden">
    <RouterLink :to="`/product/${product.id}`" class="block">
      <div class="placeholder-hatch relative flex h-[300px] items-center justify-center overflow-hidden">
        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
      </div>
    </RouterLink>
    <div class="flex items-start justify-between p-4">
      <div>
        <div class="text-[10px] uppercase tracking-wider text-muted">{{ product.category?.name }}</div>
        <div v-if="product.brand" class="text-xs font-semibold text-muted">{{ product.brand }}</div>
        <RouterLink :to="`/product/${product.id}`" class="mt-1 block font-bold text-base text-ink">{{ product.name }}</RouterLink>
      </div>
      <div class="text-right">
        <div class="whitespace-nowrap font-extrabold text-[17px] text-ink">{{ formatPrice(product.price) }}</div>
        <div v-if="product.unit === 'упаковка'" class="text-[10px] text-muted">за упак. {{ product.pack_qty }} шт</div>
      </div>
    </div>
    <button
      type="button"
      data-test="add-to-cart"
      class="emp-add w-full cursor-pointer bg-ink py-3 text-center text-xs font-semibold tracking-wide text-white"
      @click="onAdd"
    >
      В КОРЗИНУ +
    </button>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'
import { formatPrice } from '@/utils/format'

const props = defineProps({ product: { type: Object, required: true } })
const cart = useCartStore()
const ui = useUiStore()

async function onAdd() {
  const ok = await cart.addToCart(props.product.id, 1)
  if (ok) ui.showToast('Добавлено в корзину')
}
</script>

<style scoped>
.emp-card { transition: transform 0.25s ease, box-shadow 0.25s ease; }
.emp-card:hover { transform: translateY(-6px); box-shadow: 0 14px 30px rgba(31, 42, 68, 0.12); }
.emp-card:hover .emp-add { background: var(--color-accent); color: var(--color-ink); }
</style>
```

- [ ] **Step 4: Run the spec to verify it passes**

Run: `cd frontend && npm run test -- --run ProductCard`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ProductCard.vue frontend/src/components/ProductCard.spec.js
git commit -m "feat(frontend): reskin ProductCard, ₽ price, brand/unit, RU copy"
```

---

### Task 9: ProductDetailPage — ₽, characteristics, Russian

**Files:**
- Modify: `frontend/src/views/ProductDetailPage.vue`

- [ ] **Step 1: Apply changes**

In `frontend/src/views/ProductDetailPage.vue`:
- Import the helper: add `import { formatPrice } from '@/utils/format'` to `<script setup>`.
- Price (line 20): replace `${{ product.price.toFixed(2) }}` with `{{ formatPrice(product.price) }}`.
- Add-to-cart button (line 38): replace the ternary with
  `{{ product.stock > 0 ? `В корзину — ${formatPrice(product.price)}` : 'Нет в наличии' }}`.
- Add a characteristics block under the price (only render rows that have a value):

```vue
        <dl class="mt-5 grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 text-sm">
          <dt v-if="product.brand" class="text-muted">Бренд</dt>
          <dd v-if="product.brand" class="text-ink">{{ product.brand }}</dd>
          <dt v-if="product.sku" class="text-muted">Артикул</dt>
          <dd v-if="product.sku" class="text-ink">{{ product.sku }}</dd>
          <dt class="text-muted">Единица</dt>
          <dd class="text-ink">{{ product.unit }}<span v-if="product.unit === 'упаковка'"> ({{ product.pack_qty }} шт)</span></dd>
        </dl>
```

- Replace remaining English UI strings (e.g. stock badge "IN STOCK"/"OUT OF STOCK", any "ADD TO CART") with Russian: «В наличии» / «Нет в наличии» / «В корзину». Replace `font-mono`/`font-black` per the phase note.

- [ ] **Step 2: Verify build**

Run: `cd frontend && npm run build`
Expected: succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/ProductDetailPage.vue
git commit -m "feat(frontend): product page in ₽ + characteristics + RU copy"
```

---

### Task 10: Cart surfaces — ₽ and Russian

**Files:**
- Modify: `frontend/src/views/CartPage.vue`, `frontend/src/components/CartItem.vue`, `frontend/src/components/CartDrawer.vue`

- [ ] **Step 1: Apply ₽ + copy changes**

Import `formatPrice` into each of the three files and replace every `${{ ... .toFixed(2) }}` with `{{ formatPrice(...) }}`:
- `CartPage.vue:31` total → `{{ formatPrice(cartStore.totalPrice) }}`.
- `CartPage.vue:73` alert → `` `Заказ #${order.id} оформлен! Сумма: ${formatPrice(order.total)}` ``.
- `CartItem.vue:25` → `{{ formatPrice(item.price) }} за шт` (replace the `each` text).
- `CartItem.vue:67` subtotal → `{{ formatPrice(item.subtotal) }}`.
- `CartDrawer.vue:41` → `{{ formatPrice(item.subtotal) }}`.
- `CartDrawer.vue:48` total → `{{ formatPrice(cart.totalPrice) }}`.

Translate any remaining English strings in these files (e.g. "CHECKOUT", "Your cart is empty", "Subtotal", "each") to Russian («Оформить заказ», «Корзина пуста», «Итого», «за шт»). **Do not change** `data-test="open-cart"`, `cart-drawer`, `drawer-checkout`, `checkout`. Apply the phase styling note (`font-mono`→`font-sans`, rounded, tokens).

- [ ] **Step 2: Run cart unit specs**

Run: `cd frontend && npm run test -- --run CartDrawer`
Expected: PASS. If `CartDrawer.spec.js` asserts `$`/English text, update those assertions to the ₽/Russian equivalents in the same commit.

- [ ] **Step 3: Verify build + commit**

```bash
cd frontend && npm run build
git add frontend/src/views/CartPage.vue frontend/src/components/CartItem.vue frontend/src/components/CartDrawer.vue frontend/src/components/CartDrawer.spec.js
git commit -m "feat(frontend): cart in ₽ + RU copy + reskin"
```

---

### Task 11: Chrome — header, footer, USP, marquee, home hero, branding

**Files:**
- Modify: `frontend/src/components/AppHeader.vue`, `AppFooter.vue`, `UspBar.vue`, `AppMarquee.vue`, `CategoryCircle.vue`, `AppToast.vue`, `frontend/src/views/HomePage.vue`

- [ ] **Step 1: Branding**

In `AppHeader.vue` and `AppFooter.vue`, replace the "FastAPI Shop" name/logo text with **Канцелярия №1**. Apply tokens + `font-sans`.

- [ ] **Step 2: Storefront copy (use these exact strings)**

- **HomePage hero:** label `КАНЦЕЛЯРИЯ №1 — ВСЁ ДЛЯ ШКОЛЫ И ОФИСА`; H1 `Соберись` / `<span class="text-accent">к учёбе</span>`; subtitle `Ручки, тетради, бумага и всё для офиса. Доставка от 1 штуки — быстро и без лишнего.`; button `В КАТАЛОГ →`. Section headings `FEATURED`/`NEW`/`DROP` → `ХИТЫ` / `НОВИНКИ` / `КАТАЛОГ`; loading `Loading…` → `Загрузка…`.
- **UspBar items:** `ДОСТАВКА ПО ВСЕЙ СТРАНЕ` · `ОПЛАТА ПРИ ПОЛУЧЕНИИ` · `ВОЗВРАТ 14 ДНЕЙ` · `ОТ 1 ШТУКИ`.
- **AppMarquee items:** `СВЕЖИЕ ПОСТАВКИ КАЖДУЮ НЕДЕЛЮ` · `ЦЕНЫ ОПТ И РОЗНИЦА` · `ВСЁ ДЛЯ ШКОЛЫ И ОФИСА` · `БЫСТРАЯ ДОСТАВКА`.
- **AppFooter:** column `SHOP`→`МАГАЗИН` (links `Catalog`→`Каталог`, `New`→`Новинки`, `Cart`→`Корзина`); column `HELP`→`ПОМОЩЬ` (`Shipping`→`Доставка`, `Returns`→`Возврат`, `Contact`→`Контакты`). Copyright line → `© 2026 Канцелярия №1`.
- **AppHeader:** `Catalog`→`Каталог`, `SEARCH`→`ПОИСК`, keep the BAG/`open-cart` trigger; label it `КОРЗИНА`.

Apply the phase styling note throughout (`font-mono`/`font-black`→`font-sans`, soft shapes, tokens). The accent marquee bar stays but uses `bg-accent text-ink` (yellow needs dark text).

- [ ] **Step 3: Verify build + unit tests**

Run: `cd frontend && npm run build && npm run test -- --run`
Expected: build succeeds; all unit tests pass (AppToast/ProductCard/CartDrawer/format).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/AppHeader.vue frontend/src/components/AppFooter.vue frontend/src/components/UspBar.vue frontend/src/components/AppMarquee.vue frontend/src/components/CategoryCircle.vue frontend/src/components/AppToast.vue frontend/src/views/HomePage.vue
git commit -m "feat(frontend): RU storefront chrome + Канцелярия №1 branding"
```

---

### Task 12: Admin views — reskin, ₽, new product-form fields

**Files:**
- Modify: `frontend/src/views/admin/AdminProducts.vue`, `AdminOrders.vue`, `AdminLogin.vue`

- [ ] **Step 1: Add new fields to the product form**

In `AdminProducts.vue`, the form object `form` and template have `name/description/price/stock/category_id` (template lines ~25–62). Add reactive keys `brand`, `sku`, `unit` (default `'шт'`), `pack_qty` (default `1`) to the `form` ref, and add inputs after the `stock` field:

```vue
          <input v-model="form.brand" placeholder="Бренд" class="..." />
          <input v-model="form.sku" placeholder="Артикул" class="..." />
          <select v-model="form.unit" class="...">
            <option value="шт">шт</option>
            <option value="упаковка">упаковка</option>
          </select>
          <input v-model.number="form.pack_qty" type="number" min="1" placeholder="В упаковке" class="..." />
```

(Reuse the existing input class string from the neighbouring fields for visual consistency.) Ensure the create/update submit payload includes the four new keys (if it posts `form` wholesale, no change needed; if it builds an explicit object, add them).

- [ ] **Step 2: ₽ in admin tables**

- `AdminProducts.vue:174` → `{{ formatPrice(p.price) }}` (import `formatPrice`).
- `AdminOrders.vue:32` → `{{ formatPrice(o.total) }}` (import `formatPrice`).

- [ ] **Step 3: Reskin to tokens**

Apply tokens + `font-sans` across the three admin views. **Do not rename** the Russian labels the e2e depends on: `Логин`, `Пароль`, `Войти` (`AdminLogin.vue`) and the `Добавить категорию` button (`AdminProducts.vue`).

- [ ] **Step 4: Verify build + commit**

```bash
cd frontend && npm run build
git add frontend/src/views/admin/
git commit -m "feat(frontend): admin reskin, ₽ totals, stationery product fields"
```

---

## Phase E — E2E, docs, verification

### Task 13: Update e2e specs to Russian/₽

**Files:**
- Modify: `frontend/e2e/storefront.spec.js`, `frontend/e2e/cart.spec.js`

- [ ] **Step 1: Update text assertions**

In `storefront.spec.js` and `cart.spec.js`, replace English/`$` text assertions with the Russian/₽ equivalents introduced in Phase D (e.g. hero "Соберись к учёбе", button "В КОРЗИНУ +", "В КАТАЛОГ →", price strings ending in "₽"). Keep all `data-test` selectors unchanged — they did not change. Do **not** touch `admin.spec.js` label expectations (labels preserved).

- [ ] **Step 2: Start a seeded backend (port 8010 per CLAUDE.md)**

Run (from `backend/`): `uv run --frozen alembic upgrade head && uv run --frozen python seed_data.py` then in a background shell `uv run --frozen uvicorn app.main:app --host 0.0.0.0 --port 8010`.

- [ ] **Step 3: Run e2e against it**

Run (from `frontend/`): `VITE_API_BASE_URL=http://localhost:8010/api npm run test:e2e`
Expected: storefront, cart, and admin specs pass. Fix assertion text iteratively until green.

- [ ] **Step 4: Commit**

```bash
git add frontend/e2e/storefront.spec.js frontend/e2e/cart.spec.js
git commit -m "test(frontend): e2e assertions for RU/₽ stationery storefront"
```

---

### Task 14: Update CLAUDE.md design-system section

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Rewrite the "Frontend design system" section**

Replace the EMPIRE description with the new system: tokens (`--color-bg #f7f1e3`, `--color-surface`, `--color-ink #1f2a44`, `--color-accent #f0b429`, `--color-sale #d64545`, `--color-border #e7ddc7`, `--color-muted`), single font `--font-sans 'Rubik'` (no Archivo/Space Mono, no `font-mono`), soft rounded shapes. Update the top-of-file description from "brutalist EMPIRE" to the warm-school stationery identity and note prices render via `formatPrice` (`src/utils/format.js`) in ₽. Keep the `data-test` hook list and the Russian admin-label note unchanged.

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update design-system notes for stationery rebrand"
```

---

### Task 15: Full verification sweep

- [ ] **Step 1: Backend**

Run: `cd backend && uv run --frozen pytest && uv run --frozen ruff check . && uv run --frozen mypy app`
Expected: all green.

- [ ] **Step 2: Frontend unit + lint + build**

Run: `cd frontend && npm run lint && npm run test -- --run && npm run build`
Expected: lint clean, all unit tests pass, build succeeds.

- [ ] **Step 3: Frontend e2e (seeded backend on 8010 running)**

Run: `cd frontend && VITE_API_BASE_URL=http://localhost:8010/api npm run test:e2e`
Expected: all specs pass.

- [ ] **Step 4: Manual smoke (optional)**

Open `http://localhost:5173` (Vite started with `VITE_API_BASE_URL=http://localhost:8010/api npm run dev`): confirm the cream/navy/yellow Rubik storefront, Russian copy, ₽ prices, brand/unit on cards, and a working add-to-cart → drawer → checkout flow.

- [ ] **Step 5: Finish the branch**

Use the `superpowers:finishing-a-development-branch` skill to merge/PR.

---

## Self-review notes

- **Spec coverage:** model fields (T1), schemas + name length (T2), migration (T3), categories+seed (T4), fonts (T5), tokens/shapes (T6), ₽ helper (T7), reskin + new-field UI + RU copy across storefront/cart/chrome/admin (T8–T12), tests (T2, T8, T10, T13), CLAUDE.md (T14), verification (T15). All §3–§7 spec items mapped.
- **Naming consistency:** `formatPrice` used identically everywhere; `brand`/`sku`/`unit`/`pack_qty` identical across model, schema, seed, UI; category slugs match between seed and any future filters.
- **Assumptions to confirm during execution:** exact product-create route path/status code (T2 note); current English strings in components not read line-by-line (UspBar/marquee/footer) — translate in place using the provided target strings; `CartDrawer.spec.js`/e2e current assertions — adjust to match.
