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
