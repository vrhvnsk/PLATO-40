import { test, expect } from '@playwright/test'

test('guided demo loads without a fatal client error', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('/demo')
  await expect(page.locator('body')).not.toBeEmpty()
  await expect(page.locator('body')).toContainText(/PLATO|demo|scenario/i)
  expect(errors).toEqual([])
})

test('main application loads', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('body')).not.toBeEmpty()
})
