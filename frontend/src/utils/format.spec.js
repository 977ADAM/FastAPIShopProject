import { describe, it, expect } from 'vitest'
import { formatPrice } from '@/utils/format'

describe('formatPrice', () => {
  it('appends ₽ and groups thousands', () => {
    expect(formatPrice(1250)).toBe('1 250 ₽')
  })
  it('renders whole rubles without decimals', () => {
    expect(formatPrice(89.0)).toBe('89 ₽')
  })
  it('handles zero and undefined', () => {
    expect(formatPrice(0)).toBe('0 ₽')
    expect(formatPrice(undefined)).toBe('0 ₽')
  })
})
