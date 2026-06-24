import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import ProductCard from '@/components/ProductCard.vue'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'

const product = {
  id: 1,
  name: 'Wireless Headphones',
  price: 299.99,
  image_url: 'http://example.com/img.jpg',
  stock: 5,
  category: { id: 1, name: 'Electronics' },
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
  it('renders name, category and price', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Wireless Headphones')
    expect(wrapper.text()).toContain('Electronics')
    expect(wrapper.text()).toContain('299.99')
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
