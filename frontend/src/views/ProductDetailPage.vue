<template>
  <main class="mx-auto max-w-[1440px] px-6 py-6 pb-16 md:px-12">
    <RouterLink to="/" class="font-mono text-[11px] tracking-wide text-muted">← CATALOG</RouterLink>

    <p v-if="loading" class="mt-8 font-mono text-sm text-muted">Loading…</p>
    <p v-else-if="error" class="mt-8 font-mono text-sm text-accent">{{ error }}</p>

    <div v-else-if="product" class="mt-6 flex flex-col gap-11 md:flex-row">
      <div class="flex-[1.1]">
        <div class="placeholder-hatch flex h-[600px] items-center justify-center overflow-hidden bg-ink">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
        </div>
      </div>

      <div class="flex-1 pt-2">
        <span class="font-mono text-[11px] tracking-[2px] text-muted">
          {{ product.category?.name?.toUpperCase() }} · {{ stockLabel }}
        </span>
        <h1 class="mt-3 font-black text-5xl uppercase leading-[0.95] tracking-tight">{{ product.name }}</h1>
        <div class="mt-5 font-black text-4xl">${{ product.price.toFixed(2) }}</div>
        <p class="mt-5 max-w-[440px] text-[15px] leading-relaxed text-neutral-700">{{ product.description }}</p>

        <div class="mt-7 font-mono text-[11px] tracking-wide">QUANTITY</div>
        <div class="mt-2.5 flex items-center gap-3">
          <button class="flex h-10 w-10 items-center justify-center border border-ink font-mono" @click="qty = Math.max(1, qty - 1)">−</button>
          <span class="min-w-6 text-center font-mono">{{ qty }}</span>
          <button class="flex h-10 w-10 items-center justify-center border border-ink font-mono" @click="qty++">+</button>
        </div>

        <div class="mt-7 flex gap-3">
          <button
            type="button"
            data-test="add-to-cart"
            class="emp-press flex-1 cursor-pointer bg-accent py-4.5 text-center font-mono text-sm font-bold tracking-wide text-white disabled:opacity-50"
            :disabled="product.stock <= 0"
            @click="onAdd"
          >
            {{ product.stock > 0 ? `ADD TO CART — $${product.price.toFixed(2)}` : 'OUT OF STOCK' }}
          </button>
        </div>

        <div class="mt-6 flex gap-6 font-mono text-[11px] tracking-wide text-muted">
          <span>✦ FREE SHIPPING</span><span>✦ 14-DAY RETURNS</span>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const store = useProductsStore()
const cart = useCartStore()
const ui = useUiStore()

const product = ref(null)
const loading = ref(false)
const error = ref(null)
const qty = ref(1)

const stockLabel = computed(() => {
  if (!product.value) return ''
  if (product.value.stock <= 0) return 'OUT OF STOCK'
  if (product.value.stock < 5) return 'LOW STOCK'
  return 'IN STOCK'
})

async function onAdd() {
  const ok = await cart.addToCart(product.value.id, qty.value)
  if (ok) ui.showToast('Added to cart')
}

onMounted(async () => {
  loading.value = true
  try {
    product.value = await store.fetchProductById(route.params.id)
  } catch {
    error.value = 'Product not found'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.emp-press { transition: transform 0.12s ease, filter 0.2s ease; }
.emp-press:hover { filter: brightness(0.92); }
.emp-press:active { transform: scale(0.97); }
</style>
