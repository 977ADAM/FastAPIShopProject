import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'

vi.mock('@/services/api', () => ({
  authAPI: { login: vi.fn() },
}))

import { authAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('starts unauthenticated', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
  })

  it('login stores token and authenticates', async () => {
    authAPI.login.mockResolvedValue({ data: { access_token: 'jwt-123' } })
    const store = useAuthStore()
    const ok = await store.login('admin', 'admin')
    expect(ok).toBe(true)
    expect(store.isAuthenticated).toBe(true)
    expect(localStorage.getItem('admin_token')).toBe('jwt-123')
  })

  it('login maps 401 to a message and returns false', async () => {
    authAPI.login.mockRejectedValue({ response: { status: 401 } })
    const store = useAuthStore()
    const ok = await store.login('admin', 'wrong')
    expect(ok).toBe(false)
    expect(store.error).toBe('Неверный логин или пароль')
    expect(store.isAuthenticated).toBe(false)
  })

  it('logout clears token', async () => {
    authAPI.login.mockResolvedValue({ data: { access_token: 'jwt-123' } })
    const store = useAuthStore()
    await store.login('admin', 'admin')
    store.logout()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('admin_token')).toBeNull()
  })
})
