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

function planOptions(items) {
  return items.map((item) => `<option value="${item.id}">${item.planNo} / ${item.employeeName}</option>`).join("");
}

function userOptions(items) {
  return items.map((item) => `<option value="${item.id}">${item.display_name}</option>`).join("");
}

export async function renderAnalytics(root, app) {
  const [analytics, actions, plans, users] = await Promise.all([
    api.analytics(),
    api.improvementActions(),
    api.plans(),
    api.users(),
  ]);
  const completedPlans = (plans.items || []).filter((item) => item.status === "COMPLETED");
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">INSIGHT & ACTION</p>
        <h2>智能分析、低分预警与改进动作</h2>
      </div>
    </section>
    <section class="metric-grid">
      <article class="metric-card"><span class="metric-title">绩效计划总量</span><strong class="metric-value">${analytics.metrics.totalPlans}</strong></article>
      <article class="metric-card"><span class="metric-title">已完成评价</span><strong class="metric-value">${analytics.metrics.completedPlans}</strong></article>
      <article class="metric-card"><span class="metric-title">待经理评价</span><strong class="metric-value">${analytics.metrics.managerReviewPending}</strong></article>
      <article class="metric-card"><span class="metric-title">平均得分</span><strong class="metric-value">${analytics.metrics.avgScore}</strong></article>
      <article class="metric-card"><span class="metric-title">改进动作</span><strong class="metric-value">${analytics.metrics.openActions}</strong></article>
      <article class="metric-card"><span class="metric-title">待员工自评</span><strong class="metric-value">${analytics.metrics.selfReviewPending}</strong></article>
    </section>
    <section class="panel-grid">
      ${table("等级分布", analytics.gradeDistribution, [{ key: "grade", label: "等级" }, { key: "count", label: "数量" }])}
      ${table("部门排名", analytics.departmentRanking, [{ key: "orgName", label: "组织" }, { key: "planCount", label: "计划数" }, { key: "avgScore", label: "平均分" }])}
    </section>
    <section class="panel-grid">
      ${table("低分预警名单", analytics.lowScorePlans, [{ key: "planNo", label: "计划编号" }, { key: "employeeName", label: "员工" }, { key: "totalScore", label: "得分" }, { key: "grade", label: "等级" }])}
      ${table("进行中的改进动作", analytics.openImprovements, [{ key: "actionNo", label: "动作编号" }, { key: "title", label: "标题" }, { key: "dueDate", label: "到期日" }, { key: "status", label: "状态" }])}
    </section>
    <section class="panel-card">
      <header class="panel-head"><h3>创建改进动作</h3></header>
      <form id="improvement-form" class="grid-form">
        <label><span>绩效计划</span><select name="planId">${planOptions(completedPlans)}</select></label>
        <label><span>责任人</span><select name="ownerUserId">${userOptions(users.items)}</select></label>
        <label><span>发起人</span><select name="sponsorUserId">${userOptions(users.items)}</select></label>
        <label><span>到期日</span><input name="dueDate" type="date" /></label>
        <input name="actionTitle" placeholder="动作标题" value="低分项专项改进计划" />
        <textarea name="actionDetail" placeholder="动作详情">围绕低分项建立周跟踪机制，明确辅导节奏和责任闭环。</textarea>
        <button class="primary-button" type="submit">创建改进动作</button>
      </form>
    </section>
    <section class="panel-card">
      <header class="panel-head"><h3>改进动作台账</h3></header>
      <div class="table-shell">
        <table>
          <thead><tr><th>动作编号</th><th>计划编号</th><th>员工</th><th>责任人</th><th>到期日</th><th>状态</th></tr></thead>
          <tbody>
            ${(actions.items || [])
              .map(
                (item) => `
                <tr>
                  <td>${item.actionNo}</td>
                  <td>${item.planNo}</td>
                  <td>${item.employeeName}</td>
                  <td>${item.ownerName}</td>
                  <td>${item.dueDate}</td>
                  <td><span class="status-pill">${item.status}</span></td>
                </tr>
              `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;

  root.querySelector("#improvement-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createImprovementAction({
        planId: formData.get("planId"),
        ownerUserId: formData.get("ownerUserId"),
        sponsorUserId: formData.get("sponsorUserId"),
        dueDate: formData.get("dueDate"),
        actionTitle: formData.get("actionTitle"),
        actionDetail: formData.get("actionDetail"),
      });
      app.showSuccess("改进动作已创建");
      await renderAnalytics(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
}
