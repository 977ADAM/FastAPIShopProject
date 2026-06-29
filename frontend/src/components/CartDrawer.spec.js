import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import CartDrawer from '@/components/CartDrawer.vue'
import { useUiStore } from '@/stores/ui'
import { useCartStore } from '@/stores/cart'

function mountDrawer() {
  return mount(CartDrawer, {
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: false })],
      stubs: { RouterLink: { template: '<a><slot /></a>' } },
    },
  })
}

describe('CartDrawer', () => {
  it('is hidden when ui.cartOpen is false', () => {
    const wrapper = mountDrawer()
    expect(wrapper.find('[data-test="cart-drawer"]').exists()).toBe(false)
  })

  it('shows empty state when open with no items', async () => {
    const wrapper = mountDrawer()
    const ui = useUiStore()
    ui.cartOpen = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[data-test="cart-drawer"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Корзина пуста')
  })

  it('renders line items from cart details', async () => {
    const wrapper = mountDrawer()
    const ui = useUiStore()
    const cart = useCartStore()
    cart.cartItems = { 1: 2 }
    cart.cartDetails = {
      items: [{ product_id: 1, name: 'Wireless Headphones', price: 299.99, quantity: 2, subtotal: 599.98 }],
      total: 599.98,
      items_count: 2,
    }
    ui.cartOpen = true
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Wireless Headphones')
    expect(wrapper.text()).toContain('600 ₽')
  })

  it('exposes dialog semantics and a labelled close button', async () => {
    const wrapper = mountDrawer()
    const ui = useUiStore()
    ui.cartOpen = true
    await wrapper.vm.$nextTick()
    const dialog = wrapper.find('[data-test="cart-drawer"]')
    expect(dialog.attributes('role')).toBe('dialog')
    expect(dialog.attributes('aria-modal')).toBe('true')
    expect(wrapper.find('button[aria-label="Закрыть"]').exists()).toBe(true)
  })

  it('closes on the Escape key', async () => {
    const wrapper = mountDrawer()
    const ui = useUiStore()
    ui.cartOpen = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[data-test="cart-drawer"]').exists()).toBe(true)
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await wrapper.vm.$nextTick()
    expect(ui.cartOpen).toBe(false)
    expect(wrapper.find('[data-test="cart-drawer"]').exists()).toBe(false)
  })
})
