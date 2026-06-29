<template>
  <div class="emp-card rounded-xl border border-border bg-surface overflow-hidden">
    <RouterLink :to="`/product/${product.id}`" class="block">
      <div class="placeholder-hatch relative flex h-[300px] items-center justify-center overflow-hidden">
        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
        <span v-if="!inStock" class="absolute left-2 top-2 rounded bg-ink/80 px-2 py-0.5 font-sans text-[10px] font-semibold uppercase tracking-wide text-white">
          Нет в наличии
        </span>
      </div>
    </RouterLink>
    <div class="flex items-start justify-between p-4">
      <div>
        <div class="text-[10px] uppercase tracking-wider text-muted">{{ product.category?.name }}</div>
        <div v-if="product.brand" class="text-xs font-semibold text-muted">{{ product.brand }}</div>
        <RouterLink :to="`/product/${product.id}`" class="mt-1 block font-bold text-base text-ink">{{ product.name }}</RouterLink>
      </div>
      <div class="text-right">
        <div class="whitespace-nowrap font-extrabold text-[17px] text-ink">{{ formatPrice(product.price) }}</div>
        <div v-if="product.unit === 'упаковка'" class="text-[10px] text-muted">за упак. {{ product.pack_qty }} шт</div>
      </div>
    </div>
    <button
      type="button"
      data-test="add-to-cart"
      :disabled="!inStock"
      class="emp-add w-full py-3 text-center text-xs font-semibold tracking-wide"
      :class="inStock ? 'cursor-pointer bg-ink text-white' : 'cursor-not-allowed bg-border text-muted'"
      @click="onAdd"
    >
      {{ inStock ? 'В КОРЗИНУ +' : 'НЕТ В НАЛИЧИИ' }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'
import { formatPrice } from '@/utils/format'

const props = defineProps({ product: { type: Object, required: true } })
const cart = useCartStore()
const ui = useUiStore()

const inStock = computed(() => (props.product.stock ?? 0) > 0)

async function onAdd() {
  if (!inStock.value) return
  const ok = await cart.addToCart(props.product.id, 1)
  if (ok) ui.showToast('Добавлено в корзину')
}
</script>

<style scoped>
.emp-card { transition: transform 0.25s ease, box-shadow 0.25s ease; }
.emp-card:hover { transform: translateY(-6px); box-shadow: 0 14px 30px rgba(31, 42, 68, 0.12); }
.emp-card:hover .emp-add:not(:disabled) { background: var(--color-accent); color: var(--color-ink); }
</style>
