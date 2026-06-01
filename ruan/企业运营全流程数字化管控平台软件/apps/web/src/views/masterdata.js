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
  const [summary, customers, suppliers, items, projects, warehouses] = await Promise.all([
    api.summary(),
    api.customers(),
    api.suppliers(),
    api.items(),
    api.projects(),
    api.warehouses(),
  ]);
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">MASTER DATA</p>
        <h2>主数据与组织基线</h2>
      </div>
    </section>
    <section class="metric-grid compact">
      <article class="metric-card"><span class="metric-title">客户</span><strong class="metric-value">${summary.customers}</strong></article>
      <article class="metric-card"><span class="metric-title">供应商</span><strong class="metric-value">${summary.suppliers}</strong></article>
      <article class="metric-card"><span class="metric-title">物料</span><strong class="metric-value">${summary.items}</strong></article>
      <article class="metric-card"><span class="metric-title">项目</span><strong class="metric-value">${summary.projects}</strong></article>
      <article class="metric-card"><span class="metric-title">仓库</span><strong class="metric-value">${summary.warehouses}</strong></article>
    </section>
    <section class="action-form panel-card">
      <header class="panel-head"><h3>快速创建客户</h3></header>
      <form id="customer-form" class="grid-form inline-3">
        <input name="code" placeholder="客户编码，如 CUST900" />
        <input name="name" placeholder="客户名称" />
        <input name="industry" placeholder="行业，如 制造" />
        <button class="primary-button" type="submit">新增客户</button>
      </form>
    </section>
    <section class="panel-grid">
      ${table("客户", customers.items, [{ key: "code", label: "编码" }, { key: "name", label: "名称" }, { key: "industry", label: "行业" }])}
      ${table("供应商", suppliers.items, [{ key: "code", label: "编码" }, { key: "name", label: "名称" }, { key: "category", label: "类别" }])}
    </section>
    <section class="panel-grid">
      ${table("物料", items.items, [{ key: "code", label: "编码" }, { key: "name", label: "名称" }, { key: "item_type", label: "类型" }, { key: "safety_stock", label: "安全库存" }])}
      ${table("项目与仓库", [...projects.items.slice(0, 4), ...warehouses.items.slice(0, 4)], [{ key: "code", label: "编码" }, { key: "name", label: "名称" }, { key: "status", label: "状态" }])}
    </section>
  `;
  root.querySelector("#customer-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createCustomer({
        code: formData.get("code"),
        name: formData.get("name"),
        industry: formData.get("industry"),
      });
      app.showSuccess("客户创建成功");
      await renderMasterdata(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
}
