<template>
  <header class="sticky top-0 z-50 flex h-[74px] items-center justify-between border-b border-border bg-white px-5 md:px-12 relative">
    <RouterLink to="/" class="flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-[9px] bg-accent font-sans font-extrabold text-xl text-ink">К</div>
      <span class="font-sans font-extrabold text-2xl tracking-tight text-ink">Канцелярия №1</span>
    </RouterLink>

    <nav class="hidden gap-1 font-sans text-xs font-semibold uppercase tracking-wide text-ink md:flex">
      <RouterLink to="/" class="px-2.5 py-1.5">Каталог</RouterLink>
    </nav>

    <div class="flex items-center gap-3 font-sans text-xs font-semibold text-ink">
      <input
        :value="products.searchTerm"
        data-test="search"
        type="search"
        placeholder="Поиск…"
        class="hidden w-36 rounded-lg border border-border bg-bg px-3 py-1.5 font-sans text-xs font-medium text-ink placeholder:text-muted focus:w-48 focus:outline-none focus:ring-2 focus:ring-accent sm:inline-block"
        @input="onSearch"
      />
      <button
        type="button"
        data-test="open-mobile-search"
        aria-label="Поиск"
        class="cursor-pointer text-ink sm:hidden"
        @click="mobileSearchOpen = !mobileSearchOpen"
      >
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="7" />
          <path d="m21 21-4.3-4.3" />
        </svg>
      </button>
      <button
        type="button"
        data-test="open-cart"
        class="cursor-pointer bg-ink px-3 py-1.5 text-white"
        @click="ui.openCart()"
      >
        КОРЗИНА · {{ cart.itemsCount }}
      </button>
    </div>

    <!-- Mobile-only expandable search bar -->
    <div v-if="mobileSearchOpen" class="absolute left-0 top-full w-full border-b border-border bg-white px-5 py-3 sm:hidden">
      <input
        ref="mobileSearchInput"
        :value="products.searchTerm"
        data-test="search-mobile"
        type="search"
        placeholder="Поиск по названию, бренду, артикулу…"
        class="w-full rounded-lg border border-border bg-bg px-3 py-2 font-sans text-sm font-medium text-ink placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent"
        @input="onSearch"
      />
    </div>
  </header>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'
import { useProductsStore } from '@/stores/products'

const mobileSearchOpen = ref(false)
const mobileSearchInput = ref(null)
const cart = useCartStore()
const ui = useUiStore()
const products = useProductsStore()
const router = useRouter()
const route = useRoute()

// Focus the field as soon as the mobile search opens.
watch(mobileSearchOpen, async (open) => {
  if (open) {
    await nextTick()
    mobileSearchInput.value?.focus()
  }
})

// Don't leave the mobile search bar hanging open after navigating away.
watch(
  () => route.fullPath,
  () => {
    mobileSearchOpen.value = false
  },
)

function onSearch(event) {
  products.setSearch(event.target.value)
  // Results live in the home catalog — make sure the user can see them.
  if (route.name !== 'home') router.push('/')
}
</script>
