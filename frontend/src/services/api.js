// frontend/src/services/api.js
/**
 * API сервис для взаимодействия с backend.
 * Централизует все HTTP запросы к FastAPI серверу.
 * Использует axios для выполнения запросов.
 */

import axios from 'axios'

// Базовый URL API из переменных окружения или значение по умолчанию
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Создаем экземпляр axios с настройками по умолчанию
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

const TOKEN_KEY = 'admin_token'

// Подставляем JWT в каждый запрос, если он есть
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// При протухшем/невалидном токене — разлогиниваем и уводим на логин.
// Сам запрос логина (401 = неверный пароль) пропускаем — его обработает форма.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url || ''
    if (status === 401 && !url.includes('/auth/login')) {
      localStorage.removeItem(TOKEN_KEY)
      if (!window.location.pathname.startsWith('/admin/login')) {
        window.location.assign('/admin/login')
      }
    }
    return Promise.reject(error)
  },
)

// Авторизация
export const authAPI = {
  login(username, password) {
    return apiClient.post('/auth/login', { username, password })
  },
}

// Загрузка изображений (только для админа)
export const uploadsAPI = {
  uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/uploads/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

/**
 * API методы для работы с товарами
 */
export const productsAPI = {
  /**
   * Получить все товары (с опциональными limit/offset/search)
   */
  getAll(params = {}) {
    return apiClient.get('/products', { params })
  },

  /**
   * Создать товар (админ)
   */
  create(product) {
    return apiClient.post('/products', product)
  },

  /**
   * Обновить товар (админ)
   */
  update(id, product) {
    return apiClient.put(`/products/${id}`, product)
  },

  /**
   * Удалить товар (админ)
   */
  remove(id) {
    return apiClient.delete(`/products/${id}`)
  },

  /**
   * Получить товар по ID
   */
  getById(id) {
    return apiClient.get(`/products/${id}`)
  },

  /**
   * Получить товары по категории
   */
  getByCategory(categoryId) {
    return apiClient.get(`/products/category/${categoryId}`)
  },
}

/**
 * API методы для работы с категориями
 */
export const categoriesAPI = {
  /**
   * Получить все категории
   */
  getAll() {
    return apiClient.get('/categories')
  },

  /**
   * Получить категорию по ID
   */
  getById(id) {
    return apiClient.get(`/categories/${id}`)
  },

  /**
   * Создать категорию (админ)
   */
  create(category) {
    return apiClient.post('/categories', category)
  },

  /**
   * Обновить категорию (админ)
   */
  update(id, category) {
    return apiClient.put(`/categories/${id}`, category)
  },

  /**
   * Удалить категорию (админ)
   */
  remove(id) {
    return apiClient.delete(`/categories/${id}`)
  },
}

/**
 * API методы для работы с корзиной
 */
export const cartAPI = {
  /**
   * Добавить товар в корзину
   */
  addItem(item, cartData) {
    return apiClient.post('/cart/add', {
      product_id: item.product_id,
      quantity: item.quantity,
      cart: cartData,
    })
  },

  /**
   * Получить содержимое корзины
   */
  getCart(cartData) {
    return apiClient.post('/cart', cartData)
  },

  /**
   * Обновить количество товара
   */
  updateItem(item, cartData) {
    return apiClient.put('/cart/update', {
      product_id: item.product_id,
      quantity: item.quantity,
      cart: cartData,
    })
  },

  /**
   * Удалить товар из корзины
   */
  removeItem(productId, cartData) {
    return apiClient.delete(`/cart/remove/${productId}`, {
      data: {
        cart: cartData,
      },
    })
  },
}

/**
 * API методы для работы с заказами
 */
export const ordersAPI = {
  /**
   * Создать заказ (публично)
   */
  create(order) {
    return apiClient.post('/orders', order)
  },

  /**
   * Список заказов (админ)
   */
  getAll(params = {}) {
    return apiClient.get('/orders', { params })
  },

  /**
   * Заказ по ID (админ)
   */
  getById(id) {
    return apiClient.get(`/orders/${id}`)
  },

  /**
   * Изменить статус заказа (админ)
   */
  updateStatus(id, status) {
    return apiClient.patch(`/orders/${id}/status`, { status })
  },
}

export default apiClient
