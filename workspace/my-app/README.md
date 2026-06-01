# my-app

这是一个基于 `React + Vite + TypeScript` 的前端工程样板，当前已经把以下包真正接入源码：

- `react`
- `react-dom`
- `react-router-dom`
- `zustand`
- `axios`
- `playwright`

## 当前源码引用点

- `src/main.tsx`：通过 `BrowserRouter` 挂载路由
- `src/App.tsx`：使用 `Routes`、`Route`、`NavLink` 完成页面切换
- `src/api/http.ts`、`src/api/health.api.ts`、`src/api/samples.api.ts`：通过 `axios` 请求后端健康检查接口和样本列表
- `src/api/samples.api.ts`、`src/pages/SamplesPage.tsx`：通过 `axios` 请求后端样本列表
- `src/api/alerts.api.ts`、`src/pages/AlertsPage.tsx`：通过 `axios` 请求后端预警列表并执行确认
- `src/stores/useAppStore.ts`：使用 `zustand` 管理全局状态
- `tests/e2e/app.spec.ts`：使用 `playwright` 做端到端回归
- `playwright.config.ts`：配置本地开发服务器和浏览器测试入口

## 可用命令

```bash
npm run dev
npm run build
npm run lint
npm run test:e2e
```

## 说明

- 当前工程可以直接 `import axios`、`import { BrowserRouter } from 'react-router-dom'`、`import { create } from 'zustand'`、`import { test, expect } from '@playwright/test'`
- 开发环境下 `'/api'` 会代理到 `http://127.0.0.1:8000`
- Playwright 运行时会同时启动后端 `uvicorn` 服务和前端 `vite` 服务，首页 E2E 会直接校验后端健康状态与样本统计
- 如果浏览器环境尚未下载，可先执行 `npx playwright install`
