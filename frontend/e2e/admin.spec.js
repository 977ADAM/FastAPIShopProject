import { test, expect } from '@playwright/test'

// The app resolves its API the same way (see src/services/api.js).
const API_BASE = process.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

test('admin can log in and reach the dashboard', async ({ page }) => {
  await page.goto('/admin/login')
  await page.getByLabel('Логин').fill('admin')
  await page.getByLabel('Пароль').fill('admin')
  await page.getByRole('button', { name: 'Войти' }).click()

  await expect(page).toHaveURL(/\/admin$/)
  await expect(page.getByText('Товары').first()).toBeVisible()
})

test('unauthenticated admin route redirects to login', async ({ page }) => {
  await page.goto('/admin')
  await expect(page).toHaveURL(/\/admin\/login$/)
})

test('admin can create a category', async ({ page, request }) => {
  await page.goto('/admin/login')
  await page.getByLabel('Логин').fill('admin')
  await page.getByLabel('Пароль').fill('admin')
  await page.getByRole('button', { name: 'Войти' }).click()
  await expect(page).toHaveURL(/\/admin$/)

  const unique = Date.now()
  const name = `E2E Cat ${unique}`
  const slug = `e2e-cat-${unique}`
  const catForm = page.locator('form', {
    has: page.getByRole('button', { name: 'Добавить категорию' }),
  })
  await catForm.getByLabel('Название').fill(name)
  await catForm.getByLabel('Slug').fill(slug)
  await catForm.getByRole('button', { name: 'Добавить категорию' }).click()

  // Assert within the category form to avoid matching the hidden <option>
  // that also appears in the product form's category <select>.
  await expect(catForm.getByText(name)).toBeVisible()

  // Clean up: delete the category we just created so repeated e2e runs
  // don't accumulate "E2E Cat …" rows in the dev database.
  const token = (
    await (
      await request.post(`${API_BASE}/auth/login`, {
        data: { username: 'admin', password: 'admin' },
      })
    ).json()
  ).access_token
  const categories = await (await request.get(`${API_BASE}/categories`)).json()
  const created = categories.find((c) => c.slug === slug)
  expect(created, 'created category should be retrievable via API').toBeTruthy()
  const del = await request.delete(`${API_BASE}/categories/${created.id}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  expect(del.ok()).toBeTruthy()
})
