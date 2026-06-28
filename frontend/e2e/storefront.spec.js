import { test, expect } from '@playwright/test'

test('storefront loads and shows seeded products', async ({ page }) => {
  await page.goto('/')
  // NOTE: the document <title> is still set from English route meta in
  // router/index.js (e.g. "Shop - Home"); the visible storefront copy is RU.
  await expect(page).toHaveTitle(/Shop/)
  // The Russian hero copy should be rendered.
  await expect(page.getByText('Соберись').first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'В КАТАЛОГ →' })).toBeVisible()
  // A seeded product should be rendered from the API.
  await expect(page.getByText('Ручка гелевая Pilot G-2').first()).toBeVisible()
})

test('cart page is reachable', async ({ page }) => {
  await page.goto('/cart')
  await expect(page.getByRole('heading', { name: /корзина/i })).toBeVisible()
})
