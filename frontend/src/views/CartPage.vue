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
        <form class="mt-6 flex flex-col gap-3" @submit.prevent="handleCheckout">
          <input
            v-model="customerName"
            data-test="checkout-name"
            type="text"
            placeholder="Ваше имя"
            class="rounded-lg border border-border bg-bg px-3 py-2 font-sans text-sm text-ink placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent"
          />
          <input
            v-model="customerEmail"
            data-test="checkout-email"
            type="email"
            placeholder="Email для подтверждения"
            class="rounded-lg border border-border bg-bg px-3 py-2 font-sans text-sm text-ink placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent"
          />
          <p v-if="formError" data-test="checkout-error" class="font-sans text-xs text-sale">{{ formError }}</p>
          <button
            type="submit"
            data-test="checkout"
            :disabled="!canSubmit || submitting"
            class="emp-press w-full bg-accent py-4 font-sans text-sm font-bold tracking-wide text-ink disabled:cursor-not-allowed disabled:opacity-50"
          >
            {{ submitting ? 'Оформляем…' : 'Оформить заказ →' }}
          </button>
        </form>
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
import { onMounted, ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { formatPrice } from '@/utils/format'
import { isValidEmail } from '@/utils/validate'
import CartItem from '@/components/CartItem.vue'

const cartStore = useCartStore()

const customerName = ref('')
const customerEmail = ref('')
const submitting = ref(false)
const formError = ref('')

const canSubmit = computed(
  () => customerName.value.trim().length >= 2 && isValidEmail(customerEmail.value),
)

/**
 * Оформление заказа из формы (имя + email с инлайн-валидацией).
 */
async function handleCheckout() {
  if (!cartStore.hasItems || !canSubmit.value || submitting.value) return
  submitting.value = true
  formError.value = ''
  try {
    const order = await cartStore.checkout({
      name: customerName.value.trim(),
      email: customerEmail.value.trim(),
    })
    alert(`Заказ #${order.id} оформлен! Сумма: ${formatPrice(order.total)}`)
    customerName.value = ''
    customerEmail.value = ''
  } catch (err) {
    // 4xx may carry a string detail (e.g. out of stock); 422 carries an array.
    const detail = err.response?.data?.detail
    formError.value =
      typeof detail === 'string' ? detail : 'Не удалось оформить заказ. Проверьте данные.'
  } finally {
    submitting.value = false
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
