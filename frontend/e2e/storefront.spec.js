import { test, expect } from '@playwright/test'

test('storefront loads and shows seeded products', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/Shop/)
  // A seeded product should be rendered from the API.
  await expect(page.getByText('Wireless Headphones').first()).toBeVisible()
})

test('cart page is reachable', async ({ page }) => {
  await page.goto('/cart')
  await expect(page.getByRole('heading', { name: /cart/i })).toBeVisible()
})
