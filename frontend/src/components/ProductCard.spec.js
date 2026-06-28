import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import ProductCard from '@/components/ProductCard.vue'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const product = {
  id: 1,
  name: 'Ручка гелевая Pilot G-2',
  price: 89,
  image_url: 'http://example.com/img.jpg',
  stock: 5,
  brand: 'Pilot',
  unit: 'шт',
  pack_qty: 1,
  category: { id: 1, name: 'Письменные принадлежности' },
}

function mountCard() {
  return mount(ProductCard, {
    props: { product },
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: false })],
      stubs: { RouterLink: { template: '<a><slot /></a>' } },
    },
  })
}

describe('ProductCard', () => {
  it('renders name, category, brand and ₽ price', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Ручка гелевая Pilot G-2')
    expect(wrapper.text()).toContain('Письменные принадлежности')
    expect(wrapper.text()).toContain('Pilot')
    expect(wrapper.text()).toContain('89 ₽')
  })

  it('add button calls cart.addToCart and shows toast', async () => {
    const wrapper = mountCard()
    const cart = useCartStore()
    const ui = useUiStore()
    cart.addToCart = vi.fn().mockResolvedValue(true)
    ui.showToast = vi.fn()
    await wrapper.find('[data-test="add-to-cart"]').trigger('click')
    expect(cart.addToCart).toHaveBeenCalledWith(1, 1)
    expect(ui.showToast).toHaveBeenCalled()
  })
})
