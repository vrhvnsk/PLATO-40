import { test, expect } from '@playwright/test'

test('main application loads', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('body')).not.toBeEmpty()
})
