import { useEffect, useState } from 'react'
import { acknowledgeAlert as acknowledgeAlertRequest, getAlerts, type AlertRecord } from '../api'
import { useAppStore } from '../stores/useAppStore'

export function AlertsPage() {
  const markAcknowledged = useAppStore((state) => state.acknowledgeAlert)
  const acknowledgedCount = useAppStore((state) => state.alertAcknowledgedCount)
  const [alerts, setAlerts] = useState<AlertRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true

    const loadAlerts = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await getAlerts()
        if (!alive) {
          return
        }
        setAlerts(data)
      } catch (loadError) {
        if (!alive) {
          return
        }
        setError(loadError instanceof Error ? loadError.message : '预警列表加载失败')
      } finally {
        if (alive) {
          setLoading(false)
        }
      }
    }

    void loadAlerts()

    return () => {
      alive = false
    }
  }, [])

  const handleAcknowledge = async (alertId: string) => {
    try {
      await acknowledgeAlertRequest(alertId)
      markAcknowledged()
      setLoading(true)
      const data = await getAlerts()
      setAlerts(data)
    } catch (ackError) {
      setError(ackError instanceof Error ? ackError.message : '预警确认失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <article className="panel">
      <h2>预警中心</h2>
      <p>这里通过 `axios` 从后端拉取预警列表，并支持对单条预警执行确认操作。</p>
      <div className="card">
        <h3>已确认次数</h3>
        <p>{acknowledgedCount}</p>
      </div>
      {loading ? <p>正在加载预警列表……</p> : null}
      {error ? <p role="alert">加载失败：{error}</p> : null}
      <div className="table">
        {alerts.map((alert) => (
          <div key={alert.alert_id} className="table__row">
            <span>{alert.alert_id}</span>
            <span>{alert.alert_level} / {alert.reason}</span>
            <span>{alert.status}</span>
            <button
              type="button"
              className="primary-button"
              disabled={alert.status === '已确认'}
              onClick={() => void handleAcknowledge(alert.alert_id)}
            >
              {alert.status === '已确认' ? '已确认' : '确认预警'}
            </button>
          </div>
        ))}
        {!loading && alerts.length === 0 ? <p>暂无预警数据。</p> : null}
      </div>
    </article>
  )
}
