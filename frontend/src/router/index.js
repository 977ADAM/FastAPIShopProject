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
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: {
        title: 'Shop - Home',
      },
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: ProductDetailPage,
      meta: {
        title: 'Product Details',
      },
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartPage,
      meta: {
        title: 'Shopping Cart',
      },
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLogin,
      meta: {
        title: 'Admin — Login',
      },
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminProducts,
      meta: {
        title: 'Admin — Products',
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
  document.title = to.meta.title || 'FastAPI Shop'
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      return next({ name: 'admin-login' })
    }
  }
  next()
})

export default router
