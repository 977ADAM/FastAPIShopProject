import { test, expect } from '@playwright/test'

test('adding a product shows a toast and updates the bag', async ({ page }) => {
  await page.goto('/')
  await page.locator('[data-test="add-to-cart"]').first().click()
  const toast = page.locator('[data-test="toast"]')
  await expect(toast).toBeVisible()
  await expect(toast).toContainText('Добавлено в корзину')
  await page.locator('[data-test="open-cart"]').click()
  await expect(page.locator('[data-test="cart-drawer"]')).toBeVisible()
})
