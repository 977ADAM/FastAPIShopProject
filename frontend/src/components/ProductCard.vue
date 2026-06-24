<template>
  <div class="emp-card border border-border bg-white">
    <RouterLink :to="`/product/${product.id}`" class="block">
      <div class="placeholder-hatch relative flex h-[300px] items-center justify-center overflow-hidden">
        <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
      </div>
    </RouterLink>
    <div class="flex items-start justify-between p-4">
      <div>
        <div class="font-mono text-[10px] uppercase tracking-wider text-muted">{{ product.category?.name }}</div>
        <RouterLink :to="`/product/${product.id}`" class="mt-1 block font-bold text-base uppercase text-ink">{{ product.name }}</RouterLink>
      </div>
      <div class="whitespace-nowrap font-extrabold text-[17px]">${{ product.price.toFixed(2) }}</div>
    </div>
    <button
      type="button"
      data-test="add-to-cart"
      class="emp-add w-full cursor-pointer bg-ink py-3 text-center font-mono text-xs tracking-wide text-white"
      @click="onAdd"
    >
      ADD TO CART +
    </button>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const props = defineProps({ product: { type: Object, required: true } })
const cart = useCartStore()
const ui = useUiStore()

async function onAdd() {
  const ok = await cart.addToCart(props.product.id, 1)
  if (ok) ui.showToast('Added to cart')
}
</script>

<style scoped>
.emp-card { transition: transform 0.25s ease, box-shadow 0.25s ease; }
.emp-card:hover { transform: translateY(-6px); box-shadow: 0 14px 30px rgba(0, 0, 0, 0.14); }
.emp-card:hover .emp-add { background: var(--color-accent); }
</style>
