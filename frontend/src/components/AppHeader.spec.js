import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import AppHeader from '@/components/AppHeader.vue'
import { useProductsStore } from '@/stores/products'
import { useUiStore } from '@/stores/ui'

// Stub vue-router so the header mounts without a real router.
const push = vi.fn()
vi.mock('vue-router', () => ({
  RouterLink: { template: '<a><slot /></a>' },
  useRouter: () => ({ push }),
  useRoute: () => ({ name: 'home' }),
}))

function mountHeader() {
  return mount(AppHeader, {
    global: {
      plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: false })],
    },
  })
}

describe('AppHeader', () => {
  it('typing in the search box updates the products store', async () => {
    const wrapper = mountHeader()
    const products = useProductsStore()
    await wrapper.find('[data-test="search"]').setValue('степлер')
    expect(products.searchTerm).toBe('степлер')
  })

  it('the bag button opens the cart drawer', async () => {
    const wrapper = mountHeader()
    const ui = useUiStore()
    ui.openCart = vi.fn()
    await wrapper.find('[data-test="open-cart"]').trigger('click')
    expect(ui.openCart).toHaveBeenCalled()
  })
})
