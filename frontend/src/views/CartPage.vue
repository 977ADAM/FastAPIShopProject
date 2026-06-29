<!-- frontend/src/views/CartPage.vue -->
<!--
  Страница корзины покупок.
  Отображает список товаров в корзине с возможностью управления количеством.
-->

<template>
  <main class="mx-auto max-w-[1100px] px-6 py-10 md:px-12">
    <h1 class="font-sans font-extrabold text-4xl uppercase tracking-tight text-ink">Корзина</h1>

    <p v-if="cartStore.loading" class="mt-8 font-sans text-sm text-muted">Загрузка…</p>

    <div v-else-if="!cartStore.hasItems" class="mt-10 border border-border bg-surface p-12 text-center font-sans text-sm tracking-wide text-muted">
      Корзина пуста
      <div class="mt-4"><RouterLink to="/" class="font-bold text-ink underline">← В каталог</RouterLink></div>
    </div>

    <div v-else class="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1fr_320px]">
      <div class="border border-border bg-surface">
        <CartItem
          v-for="item in cartStore.cartDetails?.items || []"
          :key="item.product_id"
          :item="item"
        />
      </div>

      <aside class="h-fit rounded-xl border border-border bg-surface p-7">
        <h2 class="font-sans font-extrabold text-xl uppercase tracking-tight text-ink">Сумма заказа</h2>
        <div class="mt-6 flex items-baseline justify-between">
          <span class="font-sans text-xs font-medium tracking-wide text-muted">Итого</span>
          <span class="font-sans font-extrabold text-2xl text-ink">{{ formatPrice(cartStore.totalPrice) }}</span>
        </div>
        <button
          type="button"
          data-test="checkout"
          class="emp-press mt-6 w-full cursor-pointer bg-accent py-4 font-sans text-sm font-bold tracking-wide text-ink"
          @click="handleCheckout"
        >
          Оформить заказ →
        </button>
        <button
          type="button"
          class="mt-3 w-full cursor-pointer border border-border py-3 font-sans text-xs font-medium tracking-wide text-ink rounded"
          @click="handleClearCart"
        >
          Очистить корзину
        </button>
      </aside>
    </div>
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { formatPrice } from '@/utils/format'
import { isValidEmail } from '@/utils/validate'
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
  if (!isValidEmail(email)) {
    alert('Введите корректный email, например name@example.com')
    return
  }
  try {
    const order = await cartStore.checkout({ name, email })
    alert(`Заказ #${order.id} оформлен! Сумма: ${formatPrice(order.total)}`)
  } catch (err) {
    // 4xx from the API may carry a string detail (e.g. out of stock) or, for
    // 422 validation errors, an array — only show strings to the user.
    const detail = err.response?.data?.detail
    alert(typeof detail === 'string' ? detail : 'Не удалось оформить заказ. Проверьте данные.')
  }
}

/**
 * Очистить корзину с подтверждением
 */
function handleClearCart() {
  if (confirm('Очистить корзину?')) {
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
