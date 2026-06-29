<template>
  <main>
    <!-- HERO -->
    <section class="relative flex flex-col overflow-hidden md:flex-row" style="background:#efece4">
      <div class="z-[2] flex max-w-[760px] flex-1 flex-col justify-center px-6 py-14 md:px-12">
        <span class="font-sans text-xs font-semibold tracking-[3px] text-accent">КАНЦЕЛЯРИЯ №1 — ВСЁ ДЛЯ ШКОЛЫ И ОФИСА</span>
        <h1 class="mt-4 font-sans font-extrabold text-5xl uppercase leading-[0.9] tracking-tight md:text-7xl">
          Соберись<br /><span class="text-accent">к учёбе</span>
        </h1>
        <p class="mt-6 max-w-[430px] text-base leading-relaxed text-neutral-600">
          Ручки, тетради, бумага и всё для офиса. Доставка от 1 штуки — быстро и без лишнего.
        </p>
        <div class="mt-8 flex gap-3">
          <a href="#catalog" class="emp-press cursor-pointer bg-accent px-7 py-4 font-sans text-[13px] font-bold tracking-wide text-ink">В КАТАЛОГ →</a>
        </div>
      </div>
      <div class="relative flex flex-1 flex-col justify-between overflow-hidden p-10" style="background:radial-gradient(circle at 52% 44%, #343434 0%, #161616 58%, #111 100%)">
        <div class="flex items-center justify-between">
          <span class="font-sans text-xs font-semibold tracking-[3px] text-neutral-500">ХИТЫ</span>
          <div class="emp-badge flex h-[92px] w-[92px] rotate-12 items-center justify-center rounded-full bg-accent text-center font-sans text-[11px] font-bold leading-tight text-ink">НОВИНКИ<br />КАТАЛОГ</div>
        </div>
        <img v-if="featured?.image_url" :src="featured.image_url" :alt="featured.name" class="mx-auto max-h-[260px] object-contain" />
      </div>
    </section>

    <AppMarquee />

    <!-- CATEGORY CIRCLES -->
    <section class="mx-auto flex max-w-[1440px] flex-wrap justify-center gap-9 px-6 pb-2 pt-10 md:px-12">
      <CategoryCircle
        v-for="c in store.categories"
        :key="c.id"
        :category="c"
        :active="store.selectedCategory === c.id"
        @select="onSelectCategory"
      />
    </section>

    <!-- CATALOG -->
    <section id="catalog" class="mx-auto max-w-[1440px] px-6 pb-16 pt-8 md:px-12">
      <div class="mb-6 flex items-baseline justify-between gap-4">
        <h2 class="m-0 font-sans font-extrabold text-3xl uppercase tracking-tight">
          {{ headingText }}
        </h2>
        <span v-if="isSearching" class="shrink-0 font-sans text-xs font-semibold tracking-wide text-muted">
          Найдено: {{ store.filteredProducts.length }}
        </span>
        <button v-else-if="store.selectedCategory" class="font-sans text-xs font-semibold tracking-wide text-ink underline decoration-accent decoration-2" @click="store.clearCategoryFilter()">
          ВЕСЬ КАТАЛОГ →
        </button>
      </div>

      <p v-if="store.loading" class="font-sans text-sm text-muted">Загрузка…</p>
      <p v-else-if="!store.filteredProducts.length" class="font-sans text-sm text-muted">
        Ничего не найдено.
      </p>
      <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <ProductCard v-for="p in store.filteredProducts" :key="p.id" :product="p" />
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'
import AppMarquee from '@/components/AppMarquee.vue'
import CategoryCircle from '@/components/CategoryCircle.vue'
import ProductCard from '@/components/ProductCard.vue'

const store = useProductsStore()
const featured = computed(() => store.products[0] ?? null)
const activeCategoryName = computed(
  () => store.categories.find((c) => c.id === store.selectedCategory)?.name ?? '',
)
const isSearching = computed(() => store.searchTerm.trim().length > 0)
const headingText = computed(() => {
  if (isSearching.value) return `Поиск: «${store.searchTerm.trim()}»`
  return store.selectedCategory ? activeCategoryName.value : 'Хиты продаж'
})

function onSelectCategory(id) {
  store.setCategory(id)
  document.getElementById('catalog')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  store.fetchProducts()
  store.fetchCategories()
})
</script>

<style scoped>
@keyframes empBadge { 0%,100% { transform: rotate(12deg) scale(1); } 50% { transform: rotate(12deg) scale(1.07); } }
.emp-badge { animation: empBadge 2.6s ease-in-out infinite; }
.emp-press { transition: transform 0.12s ease, filter 0.2s ease; }
.emp-press:hover { filter: brightness(0.92); }
.emp-press:active { transform: scale(0.97); }
</style>
