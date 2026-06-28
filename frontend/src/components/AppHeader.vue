<template>
  <header class="sticky top-0 z-50 flex h-[74px] items-center justify-between border-b border-border bg-white px-5 md:px-12">
    <RouterLink to="/" class="flex items-center gap-3">
      <div class="flex h-9 w-9 items-center justify-center rounded-[9px] bg-accent font-sans font-extrabold text-xl text-ink">К</div>
      <span class="font-sans font-extrabold text-2xl tracking-tight text-ink">Канцелярия №1</span>
    </RouterLink>

    <nav class="hidden gap-1 font-sans text-xs font-semibold uppercase tracking-wide text-ink md:flex">
      <RouterLink to="/" class="px-2.5 py-1.5">Каталог</RouterLink>
    </nav>

    <div class="flex items-center gap-4 font-sans text-xs font-semibold text-ink">
      <span class="hidden cursor-default sm:inline">ПОИСК</span>
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
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const cart = useCartStore()
const ui = useUiStore()
</script>
