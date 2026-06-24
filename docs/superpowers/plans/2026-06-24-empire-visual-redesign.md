# EMPIRE Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the FastAPI Shop frontend to the brutalist beige+red "EMPIRE" aesthetic (Archivo / Space Mono, Tailwind v4) without touching the backend or data model.

**Architecture:** Introduce Tailwind v4 with a `@theme` token block as the single styling foundation, add a small Pinia UI store for cart-drawer + toast state, build a set of focused presentational/interactive components, then reassemble the storefront pages and restyle admin views. All data comes from the existing API and Pinia stores (`products`, `cart`, `auth`).

**Tech Stack:** Vue 3 (Composition API, `<script setup>`), Vite 7, Tailwind CSS v4 (`@tailwindcss/vite`), Pinia, Vitest + @vue/test-utils, Playwright.

**Visual source of truth:** `docs/superpowers/specs/2026-06-24-empire-visual-redesign-design.md` and the mockup `EMPIRE Sneakers - Direction A.dc.html` (Claude Design). Tokens are defined in Task 1.

**Conventions for this plan:**
- All paths are relative to repo root. Frontend work runs from `frontend/`.
- Visual components can't be TDD'd via assertions; their verification steps are `npm run lint`, `npm run build`, and a Playwright MCP screenshot. Stateful logic (UI store, drawer, card emit, checkout) keeps real Vitest tests.
- Commit after every task. Keep CI green.

---

## Task 1: Tailwind v4 foundation, tokens, fonts

**Files:**
- Modify: `frontend/package.json` (dep added by npm)
- Modify: `frontend/vite.config.js`
- Modify: `frontend/src/assets/main.css`
- Delete: `frontend/src/assets/base.css`
- Modify: `frontend/index.html`

- [ ] **Step 1: Install Tailwind v4**

Run (from `frontend/`):
```bash
npm install -D tailwindcss @tailwindcss/vite
```
Expected: packages added to devDependencies, `package-lock.json` updated.

- [ ] **Step 2: Register the Vite plugin**

Edit `frontend/vite.config.js` — add the import and plugin (keep existing `vue()`, `test`, `resolve`, `server`):
```js
import tailwindcss from '@tailwindcss/vite'
// ...
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  // ...rest unchanged
})
```

- [ ] **Step 3: Replace global CSS with Tailwind + tokens**

Overwrite `frontend/src/assets/main.css` entirely:
```css
@import 'tailwindcss';

@theme {
  --color-bg: #e7e7e2;
  --color-surface: #ffffff;
  --color-ink: #111111;
  --color-accent: #e11d2e;
  --color-accent-ink: #ffffff;
  --color-border: #e2e2dc;
  --color-muted: #7a7a74;
  --color-success: #16a34a;
  --color-warning: #f59e0b;

  --font-sans: 'Archivo', system-ui, sans-serif;
  --font-black: 'Archivo Black', sans-serif;
  --font-mono: 'Space Mono', monospace;
}

@layer base {
  html,
  body {
    margin: 0;
    background: var(--color-bg);
    color: var(--color-ink);
    font-family: var(--font-sans);
  }
  #app {
    min-height: 100vh;
  }
}

/* Patterned placeholder for missing imagery */
.placeholder-hatch {
  background: repeating-linear-gradient(45deg, #ecece7 0 12px, #e4e4de 12px 24px);
}

/* Brutalist marquee animation */
@keyframes marquee {
  from { transform: translateX(0); }
  to { transform: translateX(-50%); }
}
.animate-marquee { animation: marquee 22s linear infinite; }
```

- [ ] **Step 4: Delete the legacy scaffold CSS**

Run (from repo root):
```bash
git rm frontend/src/assets/base.css
```
(`main.css` no longer `@import`s it — Step 3 removed that line.)

- [ ] **Step 5: Add fonts**

Edit `frontend/index.html` — add inside `<head>` (above the existing module script):
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Archivo+Black&family=Space+Mono:wght@400;700&display=swap"
  rel="stylesheet"
/>
```

- [ ] **Step 6: Verify build and lint**

Run (from `frontend/`):
```bash
npm run build && npm run lint
```
Expected: build succeeds, no lint errors. (Existing views still render; some old utility classes now resolve via Tailwind. Visual breakage is expected and fixed in later tasks.)

- [ ] **Step 7: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.js frontend/src/assets/main.css frontend/index.html
git commit -m "build(frontend): add Tailwind v4 with EMPIRE design tokens and fonts"
```

---

## Task 2: UI store (cart drawer + toast)

**Files:**
- Create: `frontend/src/stores/ui.js`
- Test: `frontend/src/stores/ui.spec.js`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/stores/ui.spec.js`:
```js
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useUiStore } from '@/stores/ui'

describe('ui store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  it('cart drawer opens and closes', () => {
    const ui = useUiStore()
    expect(ui.cartOpen).toBe(false)
    ui.openCart()
    expect(ui.cartOpen).toBe(true)
    ui.closeCart()
    expect(ui.cartOpen).toBe(false)
  })

  it('showToast sets message then auto-clears', () => {
    const ui = useUiStore()
    ui.showToast('Added to cart')
    expect(ui.toast).toBe('Added to cart')
    vi.advanceTimersByTime(2000)
    expect(ui.toast).toBe(null)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `frontend/`): `npx vitest run src/stores/ui.spec.js`
Expected: FAIL — cannot resolve `@/stores/ui`.

- [ ] **Step 3: Implement the store**

Create `frontend/src/stores/ui.js`:
```js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const cartOpen = ref(false)
  const toast = ref(null)
  let timer = null

  function openCart() {
    cartOpen.value = true
  }
  function closeCart() {
    cartOpen.value = false
  }
  function showToast(message, duration = 1800) {
    toast.value = message
    clearTimeout(timer)
    timer = setTimeout(() => {
      toast.value = null
    }, duration)
  }

  return { cartOpen, toast, openCart, closeCart, showToast }
})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run src/stores/ui.spec.js`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/stores/ui.js frontend/src/stores/ui.spec.js
git commit -m "feat(frontend): add UI store for cart drawer and toast"
```

---

## Task 3: Toast component

**Files:**
- Create: `frontend/src/components/AppToast.vue`
- Modify: `frontend/src/App.vue`
- Test: `frontend/src/components/AppToast.spec.js`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/AppToast.spec.js`:
```js
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import AppToast from '@/components/AppToast.vue'
import { useUiStore } from '@/stores/ui'

describe('AppToast', () => {
  it('shows nothing when toast is empty', () => {
    const wrapper = mount(AppToast, {
      global: { plugins: [createTestingPinia({ createSpy: vi.fn })] },
    })
    expect(wrapper.text()).toBe('')
  })

  it('renders the toast message', () => {
    const wrapper = mount(AppToast, {
      global: {
        plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })],
      },
    })
    const ui = useUiStore()
    ui.toast = 'Added to cart'
    return wrapper.vm.$nextTick().then(() => {
      expect(wrapper.text()).toContain('Added to cart')
    })
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/components/AppToast.spec.js`
Expected: FAIL — cannot resolve `@/components/AppToast.vue`.

- [ ] **Step 3: Implement the component**

Create `frontend/src/components/AppToast.vue`:
```vue
<template>
  <Transition name="toast">
    <div
      v-if="ui.toast"
      data-test="toast"
      class="fixed bottom-7 left-1/2 z-[120] -translate-x-1/2 border-2 border-accent bg-ink px-6 py-3.5 font-mono text-sm font-bold tracking-wide text-accent"
    >
      ✦ {{ ui.toast }}
    </div>
  </Transition>
</template>

<script setup>
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 8px);
}
</style>
```

- [ ] **Step 4: Mount it globally**

Edit `frontend/src/App.vue` — add the import in `<script setup>` and render `<AppToast />` once near the root (after `<RouterView />`):
```vue
<AppToast />
```
```js
import AppToast from '@/components/AppToast.vue'
```

- [ ] **Step 5: Run test to verify it passes**

Run: `npx vitest run src/components/AppToast.spec.js`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/AppToast.vue frontend/src/components/AppToast.spec.js frontend/src/App.vue
git commit -m "feat(frontend): global toast component"
```

---

## Task 4: Static chrome — UspBar, Marquee, AppFooter

**Files:**
- Create: `frontend/src/components/UspBar.vue`
- Create: `frontend/src/components/AppMarquee.vue`
- Create: `frontend/src/components/AppFooter.vue`

- [ ] **Step 1: UspBar**

Create `frontend/src/components/UspBar.vue`:
```vue
<template>
  <div
    class="bg-ink px-4 py-2.5 text-center font-mono text-[11px] tracking-wider text-white"
  >
    FREE SHIPPING NATIONWIDE&nbsp;·&nbsp;EASY 14-DAY RETURNS&nbsp;·&nbsp;−15% ON YOUR FIRST ORDER
  </div>
</template>
```

- [ ] **Step 2: AppMarquee**

Create `frontend/src/components/AppMarquee.vue`:
```vue
<template>
  <div class="flex h-12 items-center overflow-hidden border-y-2 border-ink bg-accent">
    <div
      class="flex animate-marquee whitespace-nowrap font-mono text-[13px] font-bold tracking-wide text-white"
    >
      <span>{{ line }}&nbsp;</span>
      <span>{{ line }}&nbsp;</span>
    </div>
  </div>
</template>

<script setup>
const items = [
  'FREE SHIPPING NATIONWIDE',
  'EASY RETURNS',
  'SECURE CHECKOUT',
  'NEW ARRIVALS WEEKLY',
]
const line = items.map((i) => `✦ ${i} `).join('')
</script>
```

- [ ] **Step 3: AppFooter**

Create `frontend/src/components/AppFooter.vue`:
```vue
<template>
  <footer class="bg-ink px-6 py-12 text-white md:px-12">
    <div class="mx-auto flex max-w-[1440px] flex-wrap items-start justify-between gap-6">
      <div>
        <div class="flex items-center gap-2.5">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-accent font-black text-lg text-white">S</div>
          <div class="font-black text-2xl tracking-tight">FastAPI <span class="text-accent">Shop</span></div>
        </div>
        <div class="mt-3 font-mono text-[11px] leading-[1.9] tracking-wide text-neutral-400">
          BUILT WITH FASTAPI + VUE<br />OPEN 24/7
        </div>
      </div>
      <div class="flex gap-12 font-mono text-xs tracking-wide text-neutral-300">
        <div class="flex flex-col gap-2">
          <span class="text-white">SHOP</span><span>Catalog</span><span>New</span><span>Cart</span>
        </div>
        <div class="flex flex-col gap-2">
          <span class="text-white">HELP</span><span>Shipping</span><span>Returns</span><span>Sizes</span>
        </div>
      </div>
    </div>
  </footer>
</template>
```

- [ ] **Step 4: Verify lint + build**

Run (from `frontend/`): `npm run lint && npm run build`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/UspBar.vue frontend/src/components/AppMarquee.vue frontend/src/components/AppFooter.vue
git commit -m "feat(frontend): UspBar, Marquee, Footer chrome components"
```

---

## Task 5: AppHeader (rename + redesign)

**Files:**
- Modify (rename): `frontend/src/components/AppHeader.vue` (already exists)
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Rewrite AppHeader**

Overwrite `frontend/src/components/AppHeader.vue`:
```vue
<template>
  <header class="sticky top-0 z-50 flex h-[74px] items-center justify-between border-b border-border bg-white px-5 md:px-12">
    <RouterLink to="/" class="flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-[9px] bg-accent font-black text-xl text-white">S</div>
      <span class="font-black text-2xl tracking-tight text-ink">FastAPI Shop</span>
    </RouterLink>

    <nav class="hidden gap-1 font-mono text-xs uppercase tracking-wide text-ink md:flex">
      <RouterLink to="/" class="px-2.5 py-1.5">Catalog</RouterLink>
    </nav>

    <div class="flex items-center gap-4 font-mono text-xs text-ink">
      <span class="hidden cursor-default sm:inline">SEARCH</span>
      <button
        type="button"
        data-test="open-cart"
        class="cursor-pointer bg-ink px-3 py-1.5 text-white"
        @click="ui.openCart()"
      >
        BAG · {{ cart.itemsCount }}
      </button>
    </div>
  </header>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const cart = useCartStore()
const ui = useUiStore()
</script>
```

- [ ] **Step 2: Ensure App.vue uses header + footer + usp**

Edit `frontend/src/App.vue` template to the structure (replace old footer markup):
```vue
<template>
  <div id="app">
    <UspBar />
    <AppHeader />
    <RouterView />
    <AppFooter />
    <CartDrawer />
    <AppToast />
  </div>
</template>
```
Add imports in `<script setup>`:
```js
import UspBar from '@/components/UspBar.vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import CartDrawer from '@/components/CartDrawer.vue'
import AppToast from '@/components/AppToast.vue'
```
(Keep the existing `onMounted` cart init logic if present.) `CartDrawer` is created in Task 6 — build will fail until then; that's expected, do not run build at this step.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/AppHeader.vue frontend/src/App.vue
git commit -m "feat(frontend): redesign AppHeader with BAG drawer trigger"
```

---

## Task 6: CartDrawer

**Files:**
- Create: `frontend/src/components/CartDrawer.vue`
- Test: `frontend/src/components/CartDrawer.spec.js`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/components/CartDrawer.spec.js`:
```js
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import CartDrawer from '@/components/CartDrawer.vue'
import { useUiStore } from '@/stores/ui'
import { useCartStore } from '@/stores/cart'

function mountDrawer() {
  return mount(CartDrawer, {
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: false })],
      stubs: { RouterLink: { template: '<a><slot /></a>' } },
    },
  })
}

describe('CartDrawer', () => {
  it('is hidden when ui.cartOpen is false', () => {
    const wrapper = mountDrawer()
    expect(wrapper.find('[data-test="cart-drawer"]').exists()).toBe(false)
  })

  it('shows empty state when open with no items', async () => {
    const wrapper = mountDrawer()
    const ui = useUiStore()
    ui.cartOpen = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[data-test="cart-drawer"]').exists()).toBe(true)
    expect(wrapper.text().toLowerCase()).toContain('empty')
  })

  it('renders line items from cart details', async () => {
    const wrapper = mountDrawer()
    const ui = useUiStore()
    const cart = useCartStore()
    cart.cartItems = { 1: 2 }
    cart.cartDetails = {
      items: [{ product_id: 1, name: 'Wireless Headphones', price: 299.99, quantity: 2, subtotal: 599.98 }],
      total: 599.98,
      items_count: 2,
    }
    ui.cartOpen = true
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Wireless Headphones')
    expect(wrapper.text()).toContain('599.98')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/components/CartDrawer.spec.js`
Expected: FAIL — cannot resolve `@/components/CartDrawer.vue`.

- [ ] **Step 3: Implement CartDrawer**

Create `frontend/src/components/CartDrawer.vue`:
```vue
<template>
  <Transition name="drawer">
    <div
      v-if="ui.cartOpen"
      class="fixed inset-0 z-[100] flex justify-end bg-black/50"
      @click.self="ui.closeCart()"
    >
      <aside
        data-test="cart-drawer"
        class="flex h-full w-[430px] max-w-[90vw] flex-col bg-white"
      >
        <div class="flex items-center justify-between border-b border-border px-7 py-6">
          <span class="font-black text-xl uppercase tracking-tight">Cart · {{ cart.itemsCount }}</span>
          <button type="button" class="cursor-pointer font-mono" @click="ui.closeCart()">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto px-7">
          <p
            v-if="!cart.hasItems"
            class="py-16 text-center font-mono text-sm tracking-wide text-muted"
          >
            YOUR CART IS EMPTY
          </p>
          <div
            v-for="item in items"
            :key="item.product_id"
            class="flex gap-3.5 border-b border-neutral-100 py-4"
          >
            <div class="placeholder-hatch h-[74px] w-[74px] shrink-0 overflow-hidden">
              <img v-if="item.image_url" :src="item.image_url" :alt="item.name" class="h-full w-full object-cover" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="font-bold text-sm uppercase">{{ item.name }}</div>
              <div class="mt-2 flex items-center gap-2.5 font-mono text-sm">
                <button class="flex h-6 w-6 items-center justify-center border border-ink" @click="cart.updateQuantity(item.product_id, item.quantity - 1)">−</button>
                <span class="min-w-4 text-center">{{ item.quantity }}</span>
                <button class="flex h-6 w-6 items-center justify-center border border-ink" @click="cart.updateQuantity(item.product_id, item.quantity + 1)">+</button>
                <button class="ml-1.5 font-mono text-[10px] tracking-wide text-accent" @click="cart.removeFromCart(item.product_id)">REMOVE</button>
              </div>
            </div>
            <div class="font-extrabold text-sm">${{ item.subtotal.toFixed(2) }}</div>
          </div>
        </div>

        <div class="border-t-2 border-ink px-7 py-6">
          <div class="mb-4 flex items-baseline justify-between">
            <span class="font-mono text-xs tracking-wide text-muted">TOTAL</span>
            <span class="font-black text-2xl">${{ cart.totalPrice.toFixed(2) }}</span>
          </div>
          <RouterLink
            to="/cart"
            data-test="drawer-checkout"
            class="block cursor-pointer bg-ink py-4 text-center font-mono text-sm font-bold tracking-wide text-white"
            @click="ui.closeCart()"
          >
            GO TO CHECKOUT →
          </RouterLink>
        </div>
      </aside>
    </div>
  </Transition>
</template>

<script setup>
import { computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const cart = useCartStore()
const ui = useUiStore()
const items = computed(() => cart.cartDetails?.items ?? [])

// Refresh details whenever the drawer opens.
watch(
  () => ui.cartOpen,
  (open) => {
    if (open) cart.fetchCartDetails()
  },
)
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active { transition: opacity 0.2s ease; }
.drawer-enter-from,
.drawer-leave-to { opacity: 0; }
</style>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run src/components/CartDrawer.spec.js`
Expected: PASS (3 tests).

- [ ] **Step 5: Verify build now succeeds (App.vue references resolve)**

Run: `npm run build`
Expected: success.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/CartDrawer.vue frontend/src/components/CartDrawer.spec.js
git commit -m "feat(frontend): slide-in cart drawer"
```

---

## Task 7: ProductCard redesign

**Files:**
- Modify: `frontend/src/components/ProductCard.vue`
- Modify: `frontend/src/components/ProductCard.spec.js`

- [ ] **Step 1: Update the test for new structure**

Overwrite `frontend/src/components/ProductCard.spec.js`:
```js
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import ProductCard from '@/components/ProductCard.vue'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const product = {
  id: 1,
  name: 'Wireless Headphones',
  price: 299.99,
  image_url: 'http://example.com/img.jpg',
  stock: 5,
  category: { id: 1, name: 'Electronics' },
}

function mountCard() {
  return mount(ProductCard, {
    props: { product },
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: false })],
      stubs: { RouterLink: { template: '<a><slot /></a>' } },
    },
  })
}

describe('ProductCard', () => {
  it('renders name, category and price', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Wireless Headphones')
    expect(wrapper.text()).toContain('Electronics')
    expect(wrapper.text()).toContain('299.99')
  })

  it('add button calls cart.addToCart and shows toast', async () => {
    const wrapper = mountCard()
    const cart = useCartStore()
    const ui = useUiStore()
    cart.addToCart = vi.fn().mockResolvedValue(true)
    ui.showToast = vi.fn()
    await wrapper.find('[data-test="add-to-cart"]').trigger('click')
    expect(cart.addToCart).toHaveBeenCalledWith(1, 1)
    expect(ui.showToast).toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/components/ProductCard.spec.js`
Expected: FAIL (no `[data-test="add-to-cart"]` / structure mismatch).

- [ ] **Step 3: Rewrite ProductCard**

Overwrite `frontend/src/components/ProductCard.vue`:
```vue
<template>
  <div class="emp-card border border-border bg-white">
    <RouterLink :to="`/product/${product.id}`" class="block">
      <div class="placeholder-hatch relative flex h-[300px] items-center justify-center overflow-hidden">
        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
      </div>
    </RouterLink>
    <div class="flex items-start justify-between p-4">
      <div>
        <div class="font-mono text-[10px] uppercase tracking-wider text-muted">{{ product.category?.name }}</div>
        <RouterLink :to="`/product/${product.id}`" class="mt-1 block font-bold text-base uppercase text-ink">{{ product.name }}</RouterLink>
      </div>
      <div class="whitespace-nowrap font-extrabold text-[17px]">${{ product.price.toFixed(2) }}</div>
    </div>
    <button
      type="button"
      data-test="add-to-cart"
      class="emp-add w-full cursor-pointer bg-ink py-3 text-center font-mono text-xs tracking-wide text-white"
      @click="onAdd"
    >
      ADD TO CART +
    </button>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const props = defineProps({ product: { type: Object, required: true } })
const cart = useCartStore()
const ui = useUiStore()

async function onAdd() {
  const ok = await cart.addToCart(props.product.id, 1)
  if (ok) ui.showToast('Added to cart')
}
</script>

<style scoped>
.emp-card { transition: transform 0.25s ease, box-shadow 0.25s ease; }
.emp-card:hover { transform: translateY(-6px); box-shadow: 0 14px 30px rgba(0, 0, 0, 0.14); }
.emp-card:hover .emp-add { background: var(--color-accent); }
</style>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npx vitest run src/components/ProductCard.spec.js`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ProductCard.vue frontend/src/components/ProductCard.spec.js
git commit -m "feat(frontend): redesign ProductCard (brutalist + toast)"
```

---

## Task 8: CategoryCircle + HomePage landing

**Files:**
- Create: `frontend/src/components/CategoryCircle.vue`
- Modify: `frontend/src/views/HomePage.vue`

- [ ] **Step 1: CategoryCircle component**

Create `frontend/src/components/CategoryCircle.vue`:
```vue
<template>
  <button type="button" class="emp-cat flex cursor-pointer flex-col items-center gap-3" @click="$emit('select', category.id)">
    <span
      class="emp-cat-circle placeholder-hatch flex h-24 w-24 items-center justify-center rounded-full border border-ink"
      :class="{ 'border-accent': active }"
    >
      <span class="font-mono text-[11px] tracking-wide text-muted">{{ short }}</span>
    </span>
    <span class="font-mono text-[11px] uppercase tracking-wide text-ink">{{ category.name }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  category: { type: Object, required: true },
  active: { type: Boolean, default: false },
})
defineEmits(['select'])
const short = computed(() => props.category.name.slice(0, 4).toUpperCase())
</script>

<style scoped>
.emp-cat-circle { transition: transform 0.25s ease, border-color 0.25s ease; }
.emp-cat:hover .emp-cat-circle { transform: translateY(-4px); border-color: var(--color-accent); }
</style>
```

- [ ] **Step 2: Rewrite HomePage**

Overwrite `frontend/src/views/HomePage.vue`. It assembles hero, marquee, category circles, best sellers, split tiles, and the catalog grid + filter using the existing `products` store (`fetchProducts`, `fetchCategories`, `filteredProducts`, `categories`, `selectedCategory`, `setCategory`, `clearCategoryFilter`, `loading`):
```vue
<template>
  <main>
    <!-- HERO -->
    <section class="relative flex flex-col overflow-hidden md:flex-row" style="background:#efece4">
      <div class="z-[2] flex max-w-[760px] flex-1 flex-col justify-center px-6 py-14 md:px-12">
        <span class="font-mono text-xs tracking-[3px] text-accent">FASTAPI SHOP — ONLINE STORE</span>
        <h1 class="mt-4 font-black text-5xl uppercase leading-[0.9] tracking-tight md:text-7xl">
          Shop<br /><span class="text-accent">everything.</span>
        </h1>
        <p class="mt-6 max-w-[430px] text-base leading-relaxed text-neutral-600">
          A curated catalog of electronics, apparel, books and more. Fast, clean, no nonsense.
        </p>
        <div class="mt-8 flex gap-3">
          <a href="#catalog" class="emp-press cursor-pointer bg-accent px-7 py-4 font-mono text-[13px] font-bold tracking-wide text-white">SHOP NOW →</a>
        </div>
      </div>
      <div class="relative flex flex-1 flex-col justify-between overflow-hidden p-10" style="background:radial-gradient(circle at 52% 44%, #343434 0%, #161616 58%, #111 100%)">
        <div class="flex items-center justify-between">
          <span class="font-mono text-xs tracking-[3px] text-neutral-500">FEATURED</span>
          <div class="emp-badge flex h-[92px] w-[92px] rotate-12 items-center justify-center rounded-full bg-accent text-center font-mono text-[11px] font-bold leading-tight text-white">NEW<br />DROP</div>
        </div>
        <img v-if="featured?.image_url" :src="featured.image_url" :alt="featured.name" class="mx-auto max-h-[260px] object-contain" />
      </div>
    </section>

    <AppMarquee />

    <!-- CATEGORY CIRCLES -->
    <section class="mx-auto flex max-w-[1440px] flex-wrap justify-center gap-9 px-6 pb-2 pt-10 md:px-12">
      <CategoryCircle
        v-for="c in store.categories"
        :key="c.id"
        :category="c"
        :active="store.selectedCategory === c.id"
        @select="onSelectCategory"
      />
    </section>

    <!-- CATALOG -->
    <section id="catalog" class="mx-auto max-w-[1440px] px-6 pb-16 pt-8 md:px-12">
      <div class="mb-6 flex items-baseline justify-between">
        <h2 class="m-0 font-black text-3xl uppercase tracking-tight">
          {{ store.selectedCategory ? activeCategoryName : 'Best sellers' }}
        </h2>
        <button v-if="store.selectedCategory" class="font-mono text-xs tracking-wide text-ink underline decoration-accent decoration-2" @click="store.clearCategoryFilter()">
          ALL PRODUCTS →
        </button>
      </div>

      <p v-if="store.loading" class="font-mono text-sm text-muted">Loading…</p>
      <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <ProductCard v-for="p in store.filteredProducts" :key="p.id" :product="p" />
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'
import AppMarquee from '@/components/AppMarquee.vue'
import CategoryCircle from '@/components/CategoryCircle.vue'
import ProductCard from '@/components/ProductCard.vue'

const store = useProductsStore()
const featured = computed(() => store.products[0] ?? null)
const activeCategoryName = computed(
  () => store.categories.find((c) => c.id === store.selectedCategory)?.name ?? '',
)

function onSelectCategory(id) {
  store.setCategory(id)
  document.getElementById('catalog')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  store.fetchProducts()
  store.fetchCategories()
})
</script>

<style scoped>
@keyframes empBadge { 0%,100% { transform: rotate(12deg) scale(1); } 50% { transform: rotate(12deg) scale(1.07); } }
.emp-badge { animation: empBadge 2.6s ease-in-out infinite; }
.emp-press { transition: transform 0.12s ease, filter 0.2s ease; }
.emp-press:hover { filter: brightness(0.92); }
.emp-press:active { transform: scale(0.97); }
</style>
```

- [ ] **Step 3: Verify unit tests + build + lint**

Run (from `frontend/`):
```bash
npm run test && npm run lint && npm run build
```
Expected: all pass.

- [ ] **Step 4: Visual check via Playwright MCP**

Start backend (port 8000) and `npm run dev`, then with the Playwright MCP: `browser_navigate` to `http://localhost:5173/` and `browser_take_screenshot`. Confirm hero, marquee, category circles, and product grid render in the EMPIRE style. (See "Running the app" note at the end.)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/CategoryCircle.vue frontend/src/views/HomePage.vue
git commit -m "feat(frontend): EMPIRE landing page (hero, marquee, categories, catalog)"
```

---

## Task 9: ProductDetailPage redesign

**Files:**
- Modify: `frontend/src/views/ProductDetailPage.vue`

- [ ] **Step 1: Inspect current data usage**

Read `frontend/src/views/ProductDetailPage.vue` to confirm how it loads the product (it uses `productsStore.fetchProductById(id)` and renders a single product). Preserve the data-loading logic; replace only the markup.

- [ ] **Step 2: Rewrite the template + add qty/stock**

Replace the template and script of `frontend/src/views/ProductDetailPage.vue` with (adjust the load call to match what Step 1 found — keep the existing fetch + `product` ref + loading/error handling):
```vue
<template>
  <main class="mx-auto max-w-[1440px] px-6 py-6 pb-16 md:px-12">
    <RouterLink to="/" class="font-mono text-[11px] tracking-wide text-muted">← CATALOG</RouterLink>

    <p v-if="loading" class="mt-8 font-mono text-sm text-muted">Loading…</p>
    <p v-else-if="error" class="mt-8 font-mono text-sm text-accent">{{ error }}</p>

    <div v-else-if="product" class="mt-6 flex flex-col gap-11 md:flex-row">
      <div class="flex-[1.1]">
        <div class="placeholder-hatch flex h-[600px] items-center justify-center overflow-hidden bg-ink">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
        </div>
      </div>

      <div class="flex-1 pt-2">
        <span class="font-mono text-[11px] tracking-[2px] text-muted">
          {{ product.category?.name?.toUpperCase() }} · {{ stockLabel }}
        </span>
        <h1 class="mt-3 font-black text-5xl uppercase leading-[0.95] tracking-tight">{{ product.name }}</h1>
        <div class="mt-5 font-black text-4xl">${{ product.price.toFixed(2) }}</div>
        <p class="mt-5 max-w-[440px] text-[15px] leading-relaxed text-neutral-700">{{ product.description }}</p>

        <div class="mt-7 font-mono text-[11px] tracking-wide">QUANTITY</div>
        <div class="mt-2.5 flex items-center gap-3">
          <button class="flex h-10 w-10 items-center justify-center border border-ink font-mono" @click="qty = Math.max(1, qty - 1)">−</button>
          <span class="min-w-6 text-center font-mono">{{ qty }}</span>
          <button class="flex h-10 w-10 items-center justify-center border border-ink font-mono" @click="qty++">+</button>
        </div>

        <div class="mt-7 flex gap-3">
          <button
            type="button"
            data-test="add-to-cart"
            class="emp-press flex-1 cursor-pointer bg-accent py-4.5 text-center font-mono text-sm font-bold tracking-wide text-white disabled:opacity-50"
            :disabled="product.stock <= 0"
            @click="onAdd"
          >
            {{ product.stock > 0 ? `ADD TO CART — $${product.price.toFixed(2)}` : 'OUT OF STOCK' }}
          </button>
        </div>

        <div class="mt-6 flex gap-6 font-mono text-[11px] tracking-wide text-muted">
          <span>✦ FREE SHIPPING</span><span>✦ 14-DAY RETURNS</span>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const store = useProductsStore()
const cart = useCartStore()
const ui = useUiStore()

const product = ref(null)
const loading = ref(false)
const error = ref(null)
const qty = ref(1)

const stockLabel = computed(() => {
  if (!product.value) return ''
  if (product.value.stock <= 0) return 'OUT OF STOCK'
  if (product.value.stock < 5) return 'LOW STOCK'
  return 'IN STOCK'
})

async function onAdd() {
  const ok = await cart.addToCart(product.value.id, qty.value)
  if (ok) ui.showToast('Added to cart')
}

onMounted(async () => {
  loading.value = true
  try {
    product.value = await store.fetchProductById(route.params.id)
  } catch {
    error.value = 'Product not found'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.emp-press { transition: transform 0.12s ease, filter 0.2s ease; }
.emp-press:hover { filter: brightness(0.92); }
.emp-press:active { transform: scale(0.97); }
</style>
```

- [ ] **Step 3: Verify build + lint**

Run: `npm run lint && npm run build`
Expected: pass.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/ProductDetailPage.vue
git commit -m "feat(frontend): redesign product page (qty + stock badge)"
```

---

## Task 10: CartPage redesign

**Files:**
- Modify: `frontend/src/views/CartPage.vue`

- [ ] **Step 1: Rewrite CartPage template (keep existing script logic)**

Keep the existing `<script setup>` (cart store usage, `handleCheckout`, `handleClearCart`, `onMounted`). Replace the template with:
```vue
<template>
  <main class="mx-auto max-w-[1100px] px-6 py-10 md:px-12">
    <h1 class="font-black text-4xl uppercase tracking-tight">Cart</h1>

    <p v-if="cartStore.loading" class="mt-8 font-mono text-sm text-muted">Loading…</p>

    <div v-else-if="!cartStore.hasItems" class="mt-10 border border-border bg-white p-12 text-center font-mono text-sm tracking-wide text-muted">
      YOUR CART IS EMPTY
      <div class="mt-4"><RouterLink to="/" class="text-accent">← Back to catalog</RouterLink></div>
    </div>

    <div v-else class="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_320px]">
      <div class="border border-border bg-white">
        <CartItem
          v-for="item in cartStore.cartDetails?.items || []"
          :key="item.product_id"
          :item="item"
        />
      </div>

      <aside class="h-fit border-2 border-ink bg-white p-7">
        <h2 class="font-black text-xl uppercase">Order summary</h2>
        <div class="mt-6 flex items-baseline justify-between">
          <span class="font-mono text-xs tracking-wide text-muted">TOTAL</span>
          <span class="font-black text-2xl">${{ cartStore.totalPrice.toFixed(2) }}</span>
        </div>
        <button
          type="button"
          data-test="checkout"
          class="emp-press mt-6 w-full cursor-pointer bg-accent py-4 font-mono text-sm font-bold tracking-wide text-white"
          @click="handleCheckout"
        >
          PROCEED TO CHECKOUT →
        </button>
        <button
          type="button"
          class="mt-3 w-full cursor-pointer border border-ink py-3 font-mono text-xs tracking-wide"
          @click="handleClearCart"
        >
          CLEAR CART
        </button>
      </aside>
    </div>
  </main>
</template>
```
Ensure `RouterLink` is imported in the script if not already. Keep `CartItem` import.

- [ ] **Step 2: Restyle CartItem**

Read `frontend/src/components/CartItem.vue` and replace its template classes with the brutalist style (white surface, mono labels, square qty buttons), preserving its props/events. Minimum: image (or `.placeholder-hatch`), name uppercase bold, qty stepper bordered, price extrabold, remove link in accent.

- [ ] **Step 3: Add the `emp-press` helper (shared)**

If `.emp-press` is needed outside scoped styles, add it once to `main.css` under a `@layer components` block:
```css
@layer components {
  .emp-press { transition: transform 0.12s ease, filter 0.2s ease; }
  .emp-press:hover { filter: brightness(0.92); }
  .emp-press:active { transform: scale(0.97); }
}
```
(Then remove the duplicated scoped `.emp-press` blocks from HomePage/ProductDetail if you prefer DRY — optional.)

- [ ] **Step 4: Verify build + lint + unit tests**

Run: `npm run test && npm run lint && npm run build`
Expected: pass (cart store checkout test still green).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/CartPage.vue frontend/src/components/CartItem.vue frontend/src/assets/main.css
git commit -m "feat(frontend): redesign cart page + cart item"
```

---

## Task 11: Admin restyle (login, products, orders)

**Files:**
- Modify: `frontend/src/views/admin/AdminLogin.vue`
- Modify: `frontend/src/views/admin/AdminProducts.vue`
- Modify: `frontend/src/views/admin/AdminOrders.vue`

- [ ] **Step 1: Restyle AdminLogin**

Replace the scoped-CSS styling with Tailwind tokens: beige page, white bordered card, `font-black` heading "ADMIN", mono labels, square inputs (`border border-ink`), accent submit button. Keep all script logic, the `getByLabel('Логин'/'Пароль')` text and the submit button text unchanged (E2E depends on them).

- [ ] **Step 2: Restyle AdminProducts**

Replace scoped CSS with Tailwind tokens. Keep structure (new-product form incl. stock field, category form, products table with stock column, nav link to Orders, logout). Use: white cards `border border-border`, `font-black` headings, mono table headers, accent primary buttons, square inputs. Do not change field labels/logic.

- [ ] **Step 3: Restyle AdminOrders**

Replace scoped CSS with Tailwind tokens. Keep the orders table, status `<select>`, and nav. Style status values with small colored pills (optional): pending=muted, paid/shipped=ink, completed=success, cancelled=accent.

- [ ] **Step 4: Verify build + lint + unit tests**

Run: `npm run test && npm run lint && npm run build`
Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/admin/AdminLogin.vue frontend/src/views/admin/AdminProducts.vue frontend/src/views/admin/AdminOrders.vue
git commit -m "feat(frontend): restyle admin views to EMPIRE tokens"
```

---

## Task 12: E2E hardening + full CI

**Files:**
- Modify: `frontend/e2e/storefront.spec.js`
- Create: `frontend/e2e/cart.spec.js`

- [ ] **Step 1: Update storefront E2E for new markup**

The home title is unchanged (`Shop - Home`). The seeded product "Wireless Headphones" still renders. Keep `storefront.spec.js` "storefront loads" test. Update the "cart page reachable" test to assert the new heading:
```js
test('cart page is reachable', async ({ page }) => {
  await page.goto('/cart')
  await expect(page.getByRole('heading', { name: /cart/i })).toBeVisible()
})
```

- [ ] **Step 2: Add an add-to-cart → drawer/toast E2E**

Create `frontend/e2e/cart.spec.js`:
```js
import { test, expect } from '@playwright/test'

test('adding a product shows a toast and updates the bag', async ({ page }) => {
  await page.goto('/')
  await page.locator('[data-test="add-to-cart"]').first().click()
  await expect(page.locator('[data-test="toast"]')).toBeVisible()
  await page.locator('[data-test="open-cart"]').click()
  await expect(page.locator('[data-test="cart-drawer"]')).toBeVisible()
})
```

- [ ] **Step 3: Run E2E locally**

Start backend on port 8000 (seeded), then from `frontend/`:
```bash
npm run test:e2e
```
Expected: all storefront + admin + cart specs pass. (If port 8000 is busy locally, run backend on another port and pass `VITE_API_BASE_URL=http://localhost:<port>/api` — the webServer inherits it.)

- [ ] **Step 4: Run the full frontend gate**

Run (from `frontend/`): `npm run lint && npm run test && npm run build`
Expected: all pass.

- [ ] **Step 5: Commit and push; confirm CI green**

```bash
git add frontend/e2e/storefront.spec.js frontend/e2e/cart.spec.js
git commit -m "test(frontend): e2e for cart drawer/toast; update storefront specs"
git push origin <branch>
```
Then watch CI (`gh run watch`) — backend (ruff/mypy/alembic/pytest), frontend (lint/test/build), e2e (Playwright), docker must all pass.

---

## Running the app (reference for visual-check steps)

Backend (SQLite, seeded), from `backend/`:
```bash
uv run --frozen alembic upgrade head
uv run --frozen python seed_data.py
uv run --frozen uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Frontend dev, from `frontend/`: `npm run dev` (proxies/points to `:8000`). If 8000 is occupied, run uvicorn on another port and start vite with `VITE_API_BASE_URL=http://localhost:<port>/api`.

Visual checks use the Playwright MCP (`browser_navigate`, `browser_take_screenshot`).

---

## Self-review notes

- **Spec coverage:** tokens (T1), light-only/no-toggle (T1, no toggle built), fonts (T1), Tailwind v4 (T1), UspBar/Marquee/Footer (T4), AppHeader+BAG (T5), CartDrawer (T6), Toast (T3 + #6 deferred item), ProductCard (T7), landing hero/categories/best-sellers/catalog (T8), product page qty+stock (T9), cart page (T10), admin restyle (T11), E2E + data-test (T12). Split tiles from §5.2 are optional polish — folded into hero/landing; add if desired (non-blocking).
- **No backend changes** anywhere — confirmed (no tasks touch `backend/`).
- **Type/name consistency:** UI store API (`cartOpen/openCart/closeCart/toast/showToast`) used identically in T3/T5/T6/T7/T9. Cart store methods (`addToCart`, `updateQuantity`, `removeFromCart`, `fetchCartDetails`, `totalPrice`, `itemsCount`, `hasItems`, `cartDetails`) match the existing store. `data-test` hooks (`add-to-cart`, `open-cart`, `cart-drawer`, `drawer-checkout`, `checkout`, `toast`) are consistent across components and E2E.
