import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useUiStore } from '@/stores/ui'

describe('ui store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  it('cart drawer opens and closes', () => {
    const ui = useUiStore()
    expect(ui.cartOpen).toBe(false)
    ui.openCart()
    expect(ui.cartOpen).toBe(true)
    ui.closeCart()
    expect(ui.cartOpen).toBe(false)
  })

  it('showToast sets message then auto-clears', () => {
    const ui = useUiStore()
    ui.showToast('Added to cart')
    expect(ui.toast).toBe('Added to cart')
    vi.advanceTimersByTime(2000)
    expect(ui.toast).toBe(null)
  })
})
