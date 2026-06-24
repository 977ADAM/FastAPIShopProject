import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect, vi } from 'vitest'
import AppToast from '@/components/AppToast.vue'
import { useUiStore } from '@/stores/ui'

describe('AppToast', () => {
  it('shows nothing when toast is empty', () => {
    const wrapper = mount(AppToast, {
      global: { plugins: [createTestingPinia({ createSpy: vi.fn })] },
    })
    expect(wrapper.text()).toBe('')
  })

  it('renders the toast message', () => {
    const wrapper = mount(AppToast, {
      global: {
        plugins: [createTestingPinia({ createSpy: vi.fn, stubActions: true })],
      },
    })
    const ui = useUiStore()
    ui.toast = 'Added to cart'
    return wrapper.vm.$nextTick().then(() => {
      expect(wrapper.text()).toContain('Added to cart')
    })
  })
})
