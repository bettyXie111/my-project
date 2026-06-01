import { expect, test } from '@playwright/test'

test('首页能正常渲染并切换路由', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: '首页总览' })).toBeVisible()

  await page.getByRole('link', { name: '样本管理' }).click()
  await expect(page.getByRole('heading', { name: '样本管理' })).toBeVisible()

  await page.getByRole('link', { name: '预警中心' }).click()
  await expect(page.getByRole('heading', { name: '预警中心' })).toBeVisible()
})

test('预警列表加载并可确认预警', async ({ page }) => {
  await page.goto('/alerts')

  await expect(page.getByRole('heading', { name: '预警中心' })).toBeVisible()
  await expect(page.getByText('正在加载预警列表……')).toHaveCount(0)
  await expect(page.getByText('ALT-0001')).toBeVisible()
  await expect(page.getByRole('button', { name: '确认预警' }).first()).toBeEnabled()

  await page.getByRole('button', { name: '确认预警' }).first().click()
  await expect(page.getByText('已确认')).toBeVisible()
})

test('首页健康状态和样本统计来自后端', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: '首页总览' })).toBeVisible()
  await expect(page.getByText('健康状态：ok')).toBeVisible()
  await expect(page.getByText('样本总数：2')).toBeVisible()
  await expect(page.getByText('最新样本：S-0002 / 示例单位')).toBeVisible()
})
