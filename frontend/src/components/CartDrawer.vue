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
