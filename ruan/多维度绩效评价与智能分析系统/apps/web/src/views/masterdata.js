import { api } from "../api.js";

function table(title, items, columns) {
  const head = columns.map((column) => `<th>${column.label}</th>`).join("");
  const rows = items
    .map(
      (item) => `
        <tr>
          ${columns.map((column) => `<td>${item[column.key] ?? ""}</td>`).join("")}
        </tr>
      `
    )
    .join("");
  return `
    <article class="panel-card">
      <header class="panel-head"><h3>${title}</h3></header>
      <div class="table-shell">
        <table>
          <thead><tr>${head}</tr></thead>
          <tbody>${rows || `<tr><td colspan="${columns.length}">暂无数据</td></tr>`}</tbody>
        </table>
      </div>
    </article>
  `;
}

export async function renderMasterdata(root, app) {
  const [summary, orgUnits, users, indicators, cycles] = await Promise.all([
    api.masterdataSummary(),
    api.orgUnits(),
    api.users(),
    api.indicators(),
    api.cycles(),
  ]);
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">FOUNDATION LAYER</p>
        <h2>组织、员工、指标库与绩效周期</h2>
      </div>
    </section>
    <section class="metric-grid compact">
      <article class="metric-card"><span class="metric-title">组织单元</span><strong class="metric-value">${summary.orgUnits}</strong></article>
      <article class="metric-card"><span class="metric-title">员工账号</span><strong class="metric-value">${summary.employees}</strong></article>
      <article class="metric-card"><span class="metric-title">绩效指标</span><strong class="metric-value">${summary.indicators}</strong></article>
      <article class="metric-card"><span class="metric-title">绩效周期</span><strong class="metric-value">${summary.cycles}</strong></article>
      <article class="metric-card"><span class="metric-title">绩效计划</span><strong class="metric-value">${summary.plans}</strong></article>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>新增绩效指标</h3></header>
        <form id="indicator-form" class="grid-form">
          <input name="code" placeholder="指标编码，例如 KPI-GROWTH" />
          <input name="name" placeholder="指标名称" />
          <input name="dimension" placeholder="指标维度，例如 结果业绩" />
          <input name="weight" type="number" min="1" max="100" value="20" />
          <input name="scoringRule" placeholder="评分规则" />
          <button class="primary-button" type="submit">创建指标</button>
        </form>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>新增绩效周期</h3></header>
        <form id="cycle-form" class="grid-form">
          <input name="cycleCode" placeholder="周期编码，例如 2026H2" />
          <input name="cycleName" placeholder="周期名称" />
          <input name="periodType" value="HALF_YEAR" placeholder="周期类型" />
          <label><span>开始日期</span><input name="startDate" type="date" /></label>
          <label><span>结束日期</span><input name="endDate" type="date" /></label>
          <label><span>自评截止</span><input name="selfReviewDeadline" type="date" /></label>
          <label><span>经理评价截止</span><input name="managerReviewDeadline" type="date" /></label>
          <button class="primary-button" type="submit">创建周期</button>
        </form>
      </article>
    </section>
    <section class="panel-grid">
      ${table("组织架构", orgUnits.slice(0, 8), [{ key: "name", label: "名称" }, { key: "unit_type", label: "类型" }, { key: "status", label: "状态" }])}
      ${table("员工账号", users.items.slice(0, 8), [{ key: "display_name", label: "姓名" }, { key: "username", label: "账号" }, { key: "status", label: "状态" }])}
    </section>
    <section class="panel-grid">
      ${table("绩效指标库", indicators.items, [{ key: "code", label: "编码" }, { key: "name", label: "名称" }, { key: "dimension", label: "维度" }, { key: "weight", label: "权重" }])}
      ${table("绩效周期", cycles.items, [{ key: "cycle_code", label: "编码" }, { key: "cycle_name", label: "名称" }, { key: "period_type", label: "类型" }, { key: "self_review_deadline", label: "自评截止" }])}
    </section>
  `;
  root.querySelector("#indicator-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createIndicator({
        code: formData.get("code"),
        name: formData.get("name"),
        dimension: formData.get("dimension"),
        weight: Number(formData.get("weight")),
        scoringRule: formData.get("scoringRule"),
      });
      app.showSuccess("绩效指标创建成功");
      await renderMasterdata(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
  root.querySelector("#cycle-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createCycle({
        cycleCode: formData.get("cycleCode"),
        cycleName: formData.get("cycleName"),
        periodType: formData.get("periodType"),
        startDate: formData.get("startDate"),
        endDate: formData.get("endDate"),
        selfReviewDeadline: formData.get("selfReviewDeadline"),
        managerReviewDeadline: formData.get("managerReviewDeadline"),
      });
      app.showSuccess("绩效周期创建成功");
      await renderMasterdata(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
}
