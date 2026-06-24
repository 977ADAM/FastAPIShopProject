import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import ProductCard from '@/components/ProductCard.vue'

const product = {
  id: 1,
  name: 'Test Product',
  price: 19.99,
  image_url: 'http://example.com/img.jpg',
  category: { id: 1, name: 'Electronics' },
}

function mountCard() {
  return mount(ProductCard, {
    props: { product },
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn })],
      stubs: { 'router-link': { template: '<a><slot /></a>' } },
    },
  })
}

describe('ProductCard', () => {
  it('renders name, category and formatted price', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Test Product')
    expect(wrapper.text()).toContain('Electronics')
    expect(wrapper.text()).toContain('19.99')
  })

  it('renders the product image', () => {
    const wrapper = mountCard()
    const img = wrapper.find('img')
    expect(img.attributes('src')).toBe(product.image_url)
    expect(img.attributes('alt')).toBe(product.name)
  })
})
