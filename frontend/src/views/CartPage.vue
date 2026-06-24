<!-- frontend/src/views/CartPage.vue -->
<!--
  Страница корзины покупок.
  Отображает список товаров в корзине с возможностью управления количеством.
-->

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

<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import CartItem from '@/components/CartItem.vue'

const cartStore = useCartStore()

/**
 * Оформление заказа.
 * Минимальный сбор данных покупателя; полноценная форма — в редизайне.
 */
async function handleCheckout() {
  if (!cartStore.hasItems) return
  const name = window.prompt('Ваше имя:')
  if (!name) return
  const email = window.prompt('Ваш email:')
  if (!email) return
  try {
    const order = await cartStore.checkout({ name, email })
    alert(`Заказ #${order.id} оформлен! Сумма: $${order.total.toFixed(2)}`)
  } catch (err) {
    const detail = err.response?.data?.detail || 'Не удалось оформить заказ'
    alert(detail)
  }
}

/**
 * Очистить корзину с подтверждением
 */
function handleClearCart() {
  if (confirm('Are you sure you want to clear your cart?')) {
    cartStore.clearCart()
  }
}

/**
 * Загрузить данные корзины при монтировании
 */
onMounted(async () => {
  await cartStore.fetchCartDetails()
})
</script>
