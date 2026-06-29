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

test('header search filters the catalog', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Ручка гелевая Pilot G-2').first()).toBeVisible()

  await page.locator('[data-test="search"]').fill('степлер')

  // Catalog narrows to the single matching product, with a result count.
  await expect(page.getByText(/Найдено:\s*1/)).toBeVisible()
  await expect(page.getByText('Степлер №24/6')).toBeVisible()

  // A non-matching query shows the empty state.
  await page.locator('[data-test="search"]').fill('zzzzz')
  await expect(page.getByText('Ничего не найдено.')).toBeVisible()
})
