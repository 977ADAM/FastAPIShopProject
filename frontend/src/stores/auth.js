/**
 * Pinia store аутентификации администратора.
 * Хранит JWT в localStorage; токен подставляется в запросы интерсептором axios.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'

const TOKEN_KEY = 'admin_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY))
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.login(username, password)
      token.value = response.data.access_token
      localStorage.setItem(TOKEN_KEY, token.value)
      return true
    } catch (err) {
      error.value =
        err.response?.status === 401
          ? 'Неверный логин или пароль'
          : err.response?.status === 429
            ? 'Слишком много попыток. Попробуйте позже.'
            : 'Ошибка входа'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, loading, error, isAuthenticated, login, logout }
})
