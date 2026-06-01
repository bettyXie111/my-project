export function ReportsPage() {
  return (
    <article className="panel">
      <h2>统计报表</h2>
      <p>用于展示路由切换后的汇总视图，可作为后续接入后端接口的占位页面。</p>
      <div className="grid">
        <section className="card">
          <h3>样本总数</h3>
          <p>128</p>
        </section>
        <section className="card">
          <h3>异常预警</h3>
          <p>4</p>
        </section>
        <section className="card">
          <h3>已闭环</h3>
          <p>124</p>
        </section>
      </div>
    </article>
  )
}
