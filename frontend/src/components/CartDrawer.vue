<template>
  <Transition name="drawer">
    <div
      v-if="ui.cartOpen"
      class="fixed inset-0 z-[100] flex justify-end bg-black/50"
      @click.self="ui.closeCart()"
    >
      <aside
        data-test="cart-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Корзина"
        class="flex h-full w-[430px] max-w-[90vw] flex-col bg-surface"
      >
        <div class="flex items-center justify-between border-b border-border px-7 py-6">
          <span class="font-sans font-extrabold text-xl uppercase tracking-tight text-ink">Корзина · {{ cart.itemsCount }}</span>
          <button type="button" aria-label="Закрыть" class="cursor-pointer font-sans text-ink" @click="ui.closeCart()">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto px-7">
          <p
            v-if="!cart.hasItems"
            class="py-16 text-center font-sans text-sm tracking-wide text-muted"
          >
            Корзина пуста
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
              <div class="font-sans font-bold text-sm uppercase text-ink">{{ item.name }}</div>
              <div class="mt-2 flex items-center gap-2.5 font-sans text-sm">
                <button class="flex h-6 w-6 items-center justify-center rounded border border-ink/20 text-ink" @click="cart.updateQuantity(item.product_id, item.quantity - 1)">−</button>
                <span class="min-w-4 text-center text-ink">{{ item.quantity }}</span>
                <button class="flex h-6 w-6 items-center justify-center rounded border border-ink/20 text-ink" @click="cart.updateQuantity(item.product_id, item.quantity + 1)">+</button>
                <button class="ml-1.5 font-sans text-[10px] font-medium tracking-wide text-muted underline" @click="cart.removeFromCart(item.product_id)">Удалить</button>
              </div>
            </div>
            <div class="font-sans font-extrabold text-sm text-ink">{{ formatPrice(item.subtotal) }}</div>
          </div>
        </div>

        <div class="border-t-2 border-ink px-7 py-6">
          <div class="mb-4 flex items-baseline justify-between">
            <span class="font-sans text-xs font-medium tracking-wide text-muted">Итого</span>
            <span class="font-sans font-extrabold text-2xl text-ink">{{ formatPrice(cart.totalPrice) }}</span>
          </div>
          <RouterLink
            to="/cart"
            data-test="drawer-checkout"
            class="block cursor-pointer bg-accent py-4 text-center font-sans text-sm font-bold tracking-wide text-ink"
            @click="ui.closeCart()"
          >
            Оформить заказ →
          </RouterLink>
        </div>
      </aside>
    </div>
  </Transition>
</template>

<script setup>
import { computed, watch, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'
import { formatPrice } from '@/utils/format'

const cart = useCartStore()
const ui = useUiStore()
const items = computed(() => cart.cartDetails?.items ?? [])

function onKeydown(event) {
  if (event.key === 'Escape') ui.closeCart()
}

watch(
  () => ui.cartOpen,
  (open) => {
    if (open) {
      cart.fetchCartDetails()
      document.addEventListener('keydown', onKeydown)
    } else {
      document.removeEventListener('keydown', onKeydown)
    }
  },
)

onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active { transition: opacity 0.2s ease; }
.drawer-enter-from,
.drawer-leave-to { opacity: 0; }
</style>
