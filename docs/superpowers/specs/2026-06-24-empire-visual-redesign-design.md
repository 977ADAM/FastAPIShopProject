# Spec: Visual redesign — "EMPIRE Sneakers" style on FastAPI Shop

**Date:** 2026-06-24
**Status:** Approved (design); ready for implementation planning
**Scope option:** B — adopt the *visual* design only; keep FastAPI Shop data, branding,
currency, and backend unchanged.

## 1. Goal

Replace the current "default-looking" frontend with a distinctive, production-grade UI
based on the user's Claude Design mockup **"EMPIRE Sneakers — Direction A"**
(`claude.ai/design` project `Дизайн сайта одежды`, file
`EMPIRE Sneakers - Direction A.dc.html`). We take the **look** (brutalist / streetwear,
beige + red, Archivo / Space Mono, the layouts and components) and apply it to the
existing app's data and behavior. No backend or data-model changes.

## 2. Decisions

| Topic | Decision |
|-------|----------|
| Fidelity | Option **B**: visual only. Keep `$`, English, existing categories/products, existing API. |
| Theme | **Light only** (the mockup has no dark variant). No theme toggle. |
| Accent | Red `#e11d2e`. |
| Fonts | `Archivo` + `Archivo Black` (headings, UPPERCASE, tight tracking); `Space Mono` (labels, prices where mono fits). Loaded via Google Fonts. |
| Styling | **Tailwind CSS v4** (`@tailwindcss/vite`) with a `@theme` token block. Remove the legacy Vue scaffold `base.css`. |
| Branding | Stays **FastAPI Shop** (logo mark + name). USP/marquee copy rewritten in English, generic (shipping/returns), no sneaker-specific claims. |
| Backend | **Untouched.** No sizes, brands, ₽, installments, old-price, or order changes. |

### Superseded earlier brainstorm decisions
The earlier text-brainstorm (dark+light, violet, "sleek tech", Inter) is **superseded**
by the supplied mockup. Only the Tailwind v4 choice carries over.

## 3. Design tokens

```
--color-bg:        #e7e7e2   /* page background (warm beige) */
--color-surface:   #ffffff   /* cards, drawer */
--color-ink:       #111111   /* primary text, nav, footer, buttons */
--color-accent:    #e11d2e   /* CTAs, price highlight, active states */
--color-border:    #e2e2dc   /* hairline borders */
--color-muted:     #7a7a74   /* secondary mono text */
--color-success:   #16a34a   /* "In stock" */
--color-warning:   #f59e0b   /* "Low stock" */
font-sans:  'Archivo', system-ui, sans-serif
font-black: 'Archivo Black', sans-serif
font-mono:  'Space Mono', monospace
radius:     0 (brutalist, square) with selective small radius only on logo mark/badges
```

Patterned placeholder for missing imagery: `repeating-linear-gradient(45deg, #ecece7 0 12px, #e4e4de 12px 24px)`. Real product images from the API are used when present; the gradient is the fallback.

## 4. Information architecture / routes

Unchanged routes; restyled views.

| Route | View | Becomes |
|-------|------|---------|
| `/` | `HomePage` | Landing: USP bar, hero, marquee, category circles, "Best sellers" grid, category split tiles, footer. Also hosts the catalog grid + category filter (current behavior). |
| `/product/:id` | `ProductDetailPage` | Product page: large image, info, price, quantity, add-to-cart, trust badges. |
| `/cart` | `CartPage` | Restyled cart page (brutalist). |
| `/admin/login`, `/admin`, `/admin/orders` | admin views | Restyled to the same tokens; structure & behavior unchanged. |

Global: **CartDrawer** (slide-in) opens from the nav "BAG" button on any page; **Toast**
on add-to-cart.

## 5. Page specs (with adaptations)

### 5.1 Header / nav (`AppHeader`)
- USP top bar (`UspBar`): black, Space Mono, scrolling-free static line, EN copy
  (e.g. "FREE SHIPPING · EASY RETURNS · −15% ON FIRST ORDER").
- Sticky nav: logo mark (red square "S"→ use FastAPI Shop mark) + "FastAPI Shop";
  nav links (Catalog; category quick-links optional); SEARCH affordance (non-functional
  placeholder unless trivial); **BAG · N** button opens CartDrawer.

### 5.2 Landing (`HomePage`)
- **Hero**: split layout. Left: eyebrow, big `Archivo Black` headline, subcopy, two CTAs
  ("Shop now" → scrolls to catalog; secondary). Right: dark media panel with a featured
  product image (from API, first product or a chosen one) + "NEW DROP" badge + brand/tag
  chips. Adapt copy to generic shop.
- **Marquee** (`Marquee`): red band, animated scrolling shop USPs.
- **Category circles** (`CategoryCircle`): from API categories; click filters the catalog.
- **Best sellers**: grid (3 cols) of first N products via `ProductCard`.
- **Category split tiles**: two large clickable tiles → catalog filtered.
- **Catalog section**: the existing product grid + category filter, restyled (the current
  `HomePage` responsibility). Sidebar filters from the mockup are **reduced to category**
  (no brand/size/color — no such data).

### 5.3 Product page (`ProductDetailPage`)
- Breadcrumb (mono). Large product image (gradient fallback). Info column: SKU-style line
  uses `id`/category; `Archivo Black` name; price (`$`); **quantity stepper**; **stock
  badge** (in/low/out from `stock`) — replaces the EU size selector. Add-to-cart CTA
  (red) + wishlist heart (local-only toggle, optional/nice-to-have). Trust badges row
  (shipping/returns). No installments, no old-price, no size/thumbs strip (single image).

### 5.4 Cart
- **CartDrawer** (global): slide-in from right, line items (image, name, qty −/+, remove),
  subtotal, "Proceed to checkout". Backed by existing cart store.
- **CartPage** (`/cart`): restyled full-page version of the same data; checkout uses the
  existing flow (name/email prompt → `cartStore.checkout`). (A nicer inline checkout form
  is a future enhancement, out of scope here.)

### 5.5 Toast (`Toast`)
- Fixed bottom-center, black with red border, "Added to cart", auto-dismiss ~1.8s.
  Triggered by add-to-cart across storefront. This also satisfies the deferred
  "global feedback" item.

### 5.6 Admin (restyle only)
- `AdminLogin`, `AdminProducts`, `AdminOrders` adopt the same tokens/fonts (beige surface,
  black/red, Archivo/Space Mono, square borders). Layout and functionality unchanged.
  No mockup exists for admin, so styling is derived from the design system for consistency.

## 6. Components

Reusable units (each: one purpose, props in, events out):

- `UspBar` — static promo strip. No props.
- `AppHeader` — logo, nav, BAG button. Emits `open-cart`. Reads cart count from store.
- `Marquee` — animated text band. Prop: `items: string[]`.
- `CategoryCircle` — one category chip-circle. Props: `category`; emits `select`.
- `ProductCard` — product tile (image/gradient, category, name, stock dot, price,
  add button). Props: `product`; emits `add`. Replaces current `ProductCard`.
- `CartDrawer` — slide-in cart. Reads/acts on cart store; emits `close`, `checkout`.
- `Toast` — transient message. Driven by a tiny UI store or provide/inject.
- `AppFooter` — columns + brand.
- Base styles for buttons/chips via Tailwind component classes or small `@layer`.

A lightweight **UI store** (Pinia) or composable manages: cart drawer open state and the
toast queue (so any add-to-cart can trigger them). Cart logic stays in the existing cart store.

## 7. Theming & Tailwind setup

- Add `tailwindcss` + `@tailwindcss/vite`; import Tailwind in `main.css`; define `@theme`
  with the tokens above; remove obsolete `base.css` scaffold rules (keep only resets we need).
- Google Fonts `<link>` in `index.html` (Archivo, Archivo Black, Space Mono).
- Existing inert Tailwind utility classes in templates light up; components are then
  refactored to the new design rather than kept verbatim.

## 8. Testing impact

- **Vitest** unit tests (stores) — unaffected (logic, not markup).
- **E2E (Playwright)** — selectors are role/label/text based; rework where the redesign
  changes text or structure (e.g., login labels stay "Логин/Пароль" in admin — admin copy
  is not part of option B's storefront rebrand, so keep as-is; or add `data-test` hooks).
  Add a storefront "add to cart shows toast / drawer" E2E as a nice-to-have.
- Add `data-test` attributes on key interactive elements (BAG button, add-to-cart,
  drawer, checkout) to keep E2E robust across future visual tweaks.
- Full CI (ruff/mypy/pytest, vitest, e2e, docker) must stay green.

## 9. Out of scope / non-goals

- Any backend/API/data-model change (sizes, brands, ₽, installments, old price, orders).
- Dark theme / theme toggle.
- Full rebrand to "EMPIRE Sneakers" (kept as FastAPI Shop).
- Real search, wishlist persistence, multi-image galleries.
- A redesigned inline checkout form (keep current prompt-based flow).

## 10. High-level implementation order

1. Tailwind v4 + tokens + fonts; strip legacy CSS. Verify build.
2. Global chrome: `UspBar`, `AppHeader` (+ BAG), `AppFooter`, `Marquee`, UI store, `Toast`.
3. `CartDrawer` wired to cart store; nav opens it; add-to-cart triggers toast.
4. `ProductCard` + landing (`HomePage`): hero, categories, best sellers, split tiles, catalog grid + filter.
5. `ProductDetailPage` restyle (qty + stock badge).
6. `CartPage` restyle.
7. Admin restyle (login, products, orders).
8. E2E `data-test` hooks + spec updates; run full CI.

Detailed step-by-step plan to be produced by the writing-plans step.
