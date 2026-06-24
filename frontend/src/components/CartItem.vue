<!-- frontend/src/components/CartItem.vue -->
<!--
  Компонент элемента корзины.
  Отображает товар в корзине с возможностью изменения количества и удаления.
-->

<template>
  <div class="flex items-center gap-5 border-b border-neutral-100 p-5">
    <!-- Изображение товара -->
    <div class="placeholder-hatch h-20 w-20 flex-shrink-0 overflow-hidden border border-border">
      <img
        v-if="item.image_url"
        :src="item.image_url"
        :alt="item.name"
        class="h-full w-full object-cover"
        @error="handleImageError"
      />
    </div>

    <!-- Информация о товаре -->
    <div class="min-w-0 flex-grow">
      <h3 class="font-bold uppercase tracking-tight">
        {{ item.name }}
      </h3>
      <p class="mt-1 font-mono text-xs text-muted">${{ item.price.toFixed(2) }} each</p>

      <!-- Управление количеством -->
      <div class="mt-3 flex items-center gap-4">
        <div class="flex items-center font-mono">
          <button
            type="button"
            @click="decreaseQuantity"
            :disabled="updating"
            class="flex h-8 w-8 cursor-pointer items-center justify-center border border-ink text-sm disabled:opacity-50"
          >
            −
          </button>

          <span class="w-10 text-center text-sm font-bold">
            {{ item.quantity }}
          </span>

          <button
            type="button"
            @click="increaseQuantity"
            :disabled="updating"
            class="flex h-8 w-8 cursor-pointer items-center justify-center border border-ink text-sm disabled:opacity-50"
          >
            +
          </button>
        </div>

        <!-- Кнопка удаления -->
        <button
          type="button"
          @click="handleRemove"
          :disabled="updating"
          class="cursor-pointer font-mono text-xs tracking-wide text-accent disabled:opacity-50"
        >
          REMOVE
        </button>
      </div>
    </div>

    <!-- Сумма -->
    <div class="text-right">
      <p class="font-extrabold">${{ item.subtotal.toFixed(2) }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'

// Props
const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
})

// State
const cartStore = useCartStore()
const updating = ref(false)

// Methods
/**
 * Увеличить количество товара
 */
async function increaseQuantity() {
  updating.value = true
  await cartStore.updateQuantity(props.item.product_id, props.item.quantity + 1)
  updating.value = false
}

/**
 * Уменьшить количество товара
 */
async function decreaseQuantity() {
  updating.value = true
  if (props.item.quantity > 1) {
    await cartStore.updateQuantity(props.item.product_id, props.item.quantity - 1)
  } else {
    await cartStore.removeFromCart(props.item.product_id)
  }
  updating.value = false
}

/**
 * Удалить товар из корзины
 */
async function handleRemove() {
  updating.value = true
  await cartStore.removeFromCart(props.item.product_id)
  updating.value = false
}

/**
 * Обработка ошибки загрузки изображения
 */
function handleImageError(event) {
  event.target.src = 'https://via.placeholder.com/100x100?text=No+Image'
}
</script>
