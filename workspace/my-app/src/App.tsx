import { useEffect } from 'react'
import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import './App.css'
import { useAppStore } from './stores/useAppStore'
import { AlertsPage } from './pages/AlertsPage'
import { HomePage } from './pages/HomePage'
import { ReportsPage } from './pages/ReportsPage'
import { SamplesPage } from './pages/SamplesPage'

const navigationItems = [
  { label: '首页', path: '/' },
  { label: '样本管理', path: '/samples' },
  { label: '预警中心', path: '/alerts' },
  { label: '统计报表', path: '/reports' },
]

function Layout() {
  const location = useLocation()
  const syncRoute = useAppStore((state) => state.syncRoute)
  const activeMenu = useAppStore((state) => state.activeMenu)
  const visits = useAppStore((state) => state.visits)

  useEffect(() => {
    syncRoute(location.pathname)
  }, [location.pathname, syncRoute])

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand__title">食品安全指标快速检测与预警软件</div>
          <div className="brand__subtitle">前端工程演示骨架</div>
        </div>

        <nav className="nav">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                ['nav__item', isActive || activeMenu === item.path ? 'nav__item--active' : '']
                  .filter(Boolean)
                  .join(' ')
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <section className="status-card">
          <div className="status-card__label">访问次数</div>
          <div className="status-card__value">{visits}</div>
          <div className="status-card__hint">由 zustand 维护的全局状态</div>
        </section>
      </aside>

      <main className="content">
        <header className="content__header">
          <div>
            <h1>控制台</h1>
            <p>当前页面路径：<code>{location.pathname}</code></p>
          </div>
        </header>

        <section className="content__body">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/samples" element={<SamplesPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </section>
      </main>
    </div>
  )
}

export default function App() {
  return <Layout />
}
