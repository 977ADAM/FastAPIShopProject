<template>
  <div id="app">
    <UspBar />
    <AppHeader />
    <RouterView />
    <AppFooter />
    <CartDrawer />
    <AppToast />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import UspBar from '@/components/UspBar.vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import CartDrawer from '@/components/CartDrawer.vue'
import AppToast from '@/components/AppToast.vue'
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()

onMounted(() => {
  // Загрузить корзину из localStorage при запуске
  cartStore.initCart()
})
</script>
