<template>
  <main class="mx-auto max-w-[1440px] px-6 py-6 pb-16 md:px-12">
    <RouterLink to="/" class="font-sans text-[11px] font-bold tracking-wide text-muted">← Каталог</RouterLink>

    <p v-if="loading" class="mt-8 font-sans text-sm text-muted">Загрузка…</p>
    <p v-else-if="error" class="mt-8 font-sans text-sm text-accent">{{ error }}</p>

    <div v-else-if="product" class="mt-6 flex flex-col gap-11 md:flex-row">
      <div class="flex-[1.1]">
        <div class="placeholder-hatch flex h-[600px] items-center justify-center overflow-hidden bg-ink">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" class="h-full w-full object-cover" />
        </div>
      </div>

      <div class="flex-1 pt-2">
        <span class="font-sans text-[11px] font-bold tracking-wider text-muted">
          {{ product.category?.name?.toUpperCase() }} · {{ stockLabel }}
        </span>
        <h1 class="mt-3 font-extrabold text-5xl leading-[0.95] tracking-tight text-ink">{{ product.name }}</h1>
        <div class="mt-5 font-extrabold text-4xl text-ink">{{ formatPrice(product.price) }}</div>

        <dl class="mt-5 grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 text-sm">
          <dt v-if="product.brand" class="text-muted">Бренд</dt>
          <dd v-if="product.brand" class="text-ink">{{ product.brand }}</dd>
          <dt v-if="product.sku" class="text-muted">Артикул</dt>
          <dd v-if="product.sku" class="text-ink">{{ product.sku }}</dd>
          <dt class="text-muted">Единица</dt>
          <dd class="text-ink">{{ product.unit }}<span v-if="product.unit === 'упаковка'"> ({{ product.pack_qty }} шт)</span></dd>
        </dl>

        <p class="mt-5 max-w-[440px] text-[15px] leading-relaxed text-neutral-700">{{ product.description }}</p>

        <div class="mt-7 font-sans text-[11px] font-bold tracking-wide text-ink">Количество</div>
        <div class="mt-2.5 flex items-center gap-3">
          <button class="flex h-10 w-10 items-center justify-center border border-ink font-sans" @click="qty = Math.max(1, qty - 1)">−</button>
          <span class="min-w-6 text-center font-sans">{{ qty }}</span>
          <button class="flex h-10 w-10 items-center justify-center border border-ink font-sans" @click="qty++">+</button>
        </div>

        <div class="mt-7 flex gap-3">
          <button
            type="button"
            data-test="add-to-cart"
            class="emp-press flex-1 cursor-pointer bg-accent py-4.5 text-center font-sans text-sm font-bold tracking-wide text-ink disabled:opacity-50"
            :disabled="product.stock <= 0"
            @click="onAdd"
          >
            {{ product.stock > 0 ? `В корзину — ${formatPrice(product.price)}` : 'Нет в наличии' }}
          </button>
        </div>

        <div class="mt-6 flex gap-6 font-sans text-[11px] font-bold tracking-wide text-muted">
          <span>✦ Бесплатная доставка</span><span>✦ Возврат 14 дней</span>
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
import { formatPrice } from '@/utils/format'

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
  if (product.value.stock <= 0) return 'НЕТ В НАЛИЧИИ'
  if (product.value.stock < 5) return 'МАЛО НА СКЛАДЕ'
  return 'В НАЛИЧИИ'
})

async function onAdd() {
  const ok = await cart.addToCart(product.value.id, qty.value)
  if (ok) ui.showToast('Добавлено в корзину')
}

onMounted(async () => {
  loading.value = true
  try {
    product.value = await store.fetchProductById(route.params.id)
  } catch {
    error.value = 'Товар не найден'
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
