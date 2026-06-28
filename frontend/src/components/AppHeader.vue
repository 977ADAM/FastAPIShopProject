<template>
  <header class="sticky top-0 z-50 flex h-[74px] items-center justify-between border-b border-border bg-white px-5 md:px-12">
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
        data-test="open-cart"
        class="cursor-pointer bg-ink px-3 py-1.5 text-white"
        @click="ui.openCart()"
      >
        КОРЗИНА · {{ cart.itemsCount }}
      </button>
    </div>
  </header>
</template>

<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'
import { useProductsStore } from '@/stores/products'

const cart = useCartStore()
const ui = useUiStore()
const products = useProductsStore()
const router = useRouter()
const route = useRoute()

function onSearch(event) {
  products.setSearch(event.target.value)
  // Results live in the home catalog — make sure the user can see them.
  if (route.name !== 'home') router.push('/')
}
</script>
