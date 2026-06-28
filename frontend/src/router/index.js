// frontend/src/router/index.js
/**
 * Конфигурация Vue Router.
 * Определяет маршруты приложения и связывает их с компонентами.
 */

import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import ProductDetailPage from '@/views/ProductDetailPage.vue'
import CartPage from '@/views/CartPage.vue'
import AdminLogin from '@/views/admin/AdminLogin.vue'
import AdminProducts from '@/views/admin/AdminProducts.vue'
import AdminOrders from '@/views/admin/AdminOrders.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: {
        title: 'Канцелярия №1 — Всё для школы и офиса',
      },
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: ProductDetailPage,
      meta: {
        title: 'Товар — Канцелярия №1',
      },
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartPage,
      meta: {
        title: 'Корзина — Канцелярия №1',
      },
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLogin,
      meta: {
        title: 'Вход — Админка',
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminProducts,
      meta: {
        title: 'Товары — Админка',
        requiresAuth: true,
      },
    },
    {
      path: '/admin/orders',
      name: 'admin-orders',
      component: AdminOrders,
      meta: {
        title: 'Заказы — Админка',
        requiresAuth: true,
      },
    },
  ],
  // Прокрутка страницы вверх при переходе между роутами
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Обновление заголовка + защита админских маршрутов
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Канцелярия №1'
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      return next({ name: 'admin-login' })
    }
  }
  next()
})

export default router
