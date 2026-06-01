import { useEffect, useState } from 'react'
import { getSamples, type SampleRecord } from '../api'
import { useAppStore } from '../stores/useAppStore'

export function SamplesPage() {
  const selectedSampleId = useAppStore((state) => state.selectedSampleId)
  const selectSample = useAppStore((state) => state.selectSample)
  const [samples, setSamples] = useState<SampleRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true

    const loadSamples = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await getSamples()
        if (!alive) return
        setSamples(data)
        if (data.length > 0) {
          selectSample(data[0].sample_id)
        }
      } catch (loadError) {
        if (!alive) return
        setError(loadError instanceof Error ? loadError.message : '样本列表加载失败')
      } finally {
        if (alive) {
          setLoading(false)
        }
      }
    }

    void loadSamples()

    return () => {
      alive = false
    }
  }, [selectSample])

  return (
    <article className="panel">
      <h2>样本管理</h2>
      <p>这里通过 `axios` 从后端拉取样本列表，并用 `zustand` 记录选中项。</p>
      {loading ? <p>正在加载样本列表……</p> : null}
      {error ? <p role="alert">加载失败：{error}</p> : null}
      <div className="table">
        {samples.map((row) => (
          <button
            key={row.sample_id}
            type="button"
            className={row.sample_id === selectedSampleId ? 'table__row table__row--active' : 'table__row'}
            onClick={() => selectSample(row.sample_id)}
          >
            <span>{row.sample_code}</span>
            <span>{row.owner}</span>
            <span>{row.created_at}</span>
          </button>
        ))}
        {!loading && samples.length === 0 ? <p>暂无样本数据。</p> : null}
      </div>
    </article>
  )
}
