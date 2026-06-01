import { useEffect, useState } from 'react'
import { getHealthStatus, getSamples, type SampleRecord } from '../api'

export function HomePage() {
  const [healthStatus, setHealthStatus] = useState('未检查')
  const [healthHint, setHealthHint] = useState('页面加载后会通过 axios 请求后端健康检查接口。')
  const [sampleCount, setSampleCount] = useState(0)
  const [latestSample, setLatestSample] = useState<SampleRecord | null>(null)

  useEffect(() => {
    let alive = true

    const loadHomeData = async () => {
      try {
        const [healthData, sampleData] = await Promise.all([getHealthStatus(), getSamples()])
        if (!alive) return
        setHealthStatus(healthData.status)
        setHealthHint('已通过 `axios` 连接后端健康检查接口和样本列表接口。')
        setSampleCount(sampleData.length)
        setLatestSample(sampleData[0] ?? null)
      } catch (error) {
        if (!alive) return
        setHealthStatus('不可用')
        setHealthHint(error instanceof Error ? error.message : '请求失败')
        setSampleCount(0)
        setLatestSample(null)
      }
    }

    void loadHomeData()

    return () => {
      alive = false
    }
  }, [])

  return (
    <article className="panel">
      <h2>首页总览</h2>
      <p>当前前端工程已接入 React Router 与 zustand，可用于页面路由和全局状态管理。</p>
      <div className="card">
        <h3>后端连通性</h3>
        <p>健康状态：{healthStatus}</p>
        <p>{healthHint}</p>
        <p>样本总数：{sampleCount}</p>
        <p>最新样本：{latestSample ? `${latestSample.sample_code} / ${latestSample.owner}` : '暂无'}</p>
      </div>
      <div className="grid">
        <section className="card">
          <h3>路由能力</h3>
          <p>支持首页、样本管理、预警中心和统计报表四个入口。</p>
        </section>
        <section className="card">
          <h3>状态能力</h3>
          <p>访问次数、当前菜单和样本选中状态由 zustand 统一维护。</p>
        </section>
        <section className="card">
          <h3>测试能力</h3>
          <p>Playwright 已纳入工程，可用于端到端回归验证。</p>
        </section>
      </div>
    </article>
  )
}
