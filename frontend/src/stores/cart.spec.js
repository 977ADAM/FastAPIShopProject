import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'

vi.mock('@/services/api', () => ({
  cartAPI: {
    addItem: vi.fn(),
    getCart: vi.fn(),
    updateItem: vi.fn(),
    removeItem: vi.fn(),
  },
}))

import { cartAPI } from '@/services/api'
import { useCartStore } from '@/stores/cart'

describe('cart store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('itemsCount sums quantities', () => {
    const store = useCartStore()
    store.cartItems = { 1: 2, 3: 5 }
    expect(store.itemsCount).toBe(7)
  })

  it('hasItems reflects content', () => {
    const store = useCartStore()
    expect(store.hasItems).toBe(false)
    store.cartItems = { 1: 1 }
    expect(store.hasItems).toBe(true)
  })

  it('initCart loads from localStorage', () => {
    localStorage.setItem('shopping_cart', JSON.stringify({ 2: 4 }))
    const store = useCartStore()
    store.initCart()
    expect(store.cartItems).toEqual({ 2: 4 })
  })

  it('addToCart updates state, persists and fetches details', async () => {
    cartAPI.addItem.mockResolvedValue({ data: { cart: { 1: 1 } } })
    cartAPI.getCart.mockResolvedValue({
      data: { items: [], total: 10, items_count: 1 },
    })

    const store = useCartStore()
    const ok = await store.addToCart(1, 1)

    expect(ok).toBe(true)
    expect(store.cartItems).toEqual({ 1: 1 })
    expect(JSON.parse(localStorage.getItem('shopping_cart'))).toEqual({ 1: 1 })
    expect(store.totalPrice).toBe(10)
  })

  it('addToCart returns false on API error', async () => {
    cartAPI.addItem.mockRejectedValue(new Error('network'))
    const store = useCartStore()
    expect(await store.addToCart(1, 1)).toBe(false)
  })

  it('clearCart resets state', () => {
    const store = useCartStore()
    store.cartItems = { 1: 2 }
    store.clearCart()
    expect(store.cartItems).toEqual({})
    expect(store.hasItems).toBe(false)
  })
})
