import { test, expect } from '@playwright/test'

test('storefront loads and shows seeded products', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/Канцелярия/)
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
