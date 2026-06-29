import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useProductsStore } from '@/stores/products'
import { productsAPI } from '@/services/api'

vi.mock('@/services/api', () => ({
  productsAPI: { getAll: vi.fn() },
  categoriesAPI: { getAll: vi.fn() },
}))

const sample = [
  { id: 1, name: 'Ручка гелевая Pilot G-2', brand: 'Pilot', sku: 'PIL-G2-BL', category_id: 1 },
  { id: 2, name: 'Тетрадь 48 л.', brand: 'ErichKrause', sku: 'EK-48-KL', category_id: 2 },
  { id: 3, name: 'Степлер №24/6', brand: 'KW-trio', sku: 'KW-24-6', category_id: 2 },
]

describe('products store search', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('returns all products when search is empty', () => {
    const store = useProductsStore()
    store.products = sample
    expect(store.filteredProducts).toHaveLength(3)
  })

  it('filters by name (case-insensitive)', () => {
    const store = useProductsStore()
    store.products = sample
    store.setSearch('тетрадь')
    expect(store.filteredProducts.map((p) => p.id)).toEqual([2])
  })

  it('filters by brand', () => {
    const store = useProductsStore()
    store.products = sample
    store.setSearch('pilot')
    expect(store.filteredProducts.map((p) => p.id)).toEqual([1])
  })

  it('filters by sku', () => {
    const store = useProductsStore()
    store.products = sample
    store.setSearch('kw-24')
    expect(store.filteredProducts.map((p) => p.id)).toEqual([3])
  })

  it('combines category and search filters', () => {
    const store = useProductsStore()
    store.products = sample
    store.setCategory(2)
    store.setSearch('степлер')
    expect(store.filteredProducts.map((p) => p.id)).toEqual([3])
  })
})

describe('products store fetch', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('populates products and clears error on success', async () => {
    productsAPI.getAll.mockResolvedValueOnce({ data: { products: sample } })
    const store = useProductsStore()
    await store.fetchProducts()
    expect(store.products).toHaveLength(3)
    expect(store.error).toBeNull()
    expect(store.loading).toBe(false)
  })

  it('sets an error and stops loading when the request fails', async () => {
    productsAPI.getAll.mockRejectedValueOnce(new Error('network down'))
    const store = useProductsStore()
    await store.fetchProducts()
    expect(store.error).toBeTruthy()
    expect(store.loading).toBe(false)
  })
})
