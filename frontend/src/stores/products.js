// frontend/src/stores/products.js
/**
 * Pinia store для управления состоянием товаров.
 * Хранит список товаров, информацию о фильтрации и состояние загрузки.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { productsAPI, categoriesAPI } from '@/services/api'

export const useProductsStore = defineStore('products', () => {
  // State
  const products = ref([])
  const categories = ref([])
  const selectedCategory = ref(null)
  const searchTerm = ref('')
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const filteredProducts = computed(() => {
    let list = products.value
    if (selectedCategory.value) {
      list = list.filter((product) => product.category_id === selectedCategory.value)
    }
    const q = searchTerm.value.trim().toLowerCase()
    if (q) {
      list = list.filter((product) =>
        [product.name, product.brand, product.sku]
          .filter(Boolean)
          .some((field) => field.toLowerCase().includes(q)),
      )
    }
    return list
  })

  const productsCount = computed(() => filteredProducts.value.length)

  // Actions
  /**
   * Загрузить все товары с сервера
   */
  async function fetchProducts() {
    loading.value = true
    error.value = null
    try {
      const response = await productsAPI.getAll()
      products.value = response.data.products
    } catch (err) {
      error.value = 'Failed to load products'
      console.error('Error fetching products:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Загрузить товар по ID
   */
  async function fetchProductById(id) {
    loading.value = true
    error.value = null
    try {
      const response = await productsAPI.getById(id)
      return response.data
    } catch (err) {
      error.value = 'Failed to load product'
      console.error('Error fetching product:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Загрузить все категории
   */
  async function fetchCategories() {
    try {
      const response = await categoriesAPI.getAll()
      categories.value = response.data
    } catch (err) {
      console.error('Error fetching categories:', err)
    }
  }

  /**
   * Установить фильтр по категории
   */
  function setCategory(categoryId) {
    selectedCategory.value = categoryId
  }

  /**
   * Сбросить фильтр категории
   */
  function clearCategoryFilter() {
    selectedCategory.value = null
  }

  /**
   * Установить поисковый запрос (фильтрует по названию, бренду и артикулу)
   */
  function setSearch(term) {
    searchTerm.value = term ?? ''
  }

  return {
    // State
    products,
    categories,
    selectedCategory,
    searchTerm,
    loading,
    error,
    // Getters
    filteredProducts,
    productsCount,
    // Actions
    fetchProducts,
    fetchProductById,
    fetchCategories,
    setCategory,
    clearCategoryFilter,
    setSearch,
  }
})
