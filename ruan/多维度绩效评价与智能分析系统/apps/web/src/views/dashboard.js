import { api } from "../api.js";
import { t } from "../i18n.js";

function metricCard(title, value, hint) {
  return `
    <article class="metric-card">
      <span class="metric-title">${title}</span>
      <strong class="metric-value">${value}</strong>
      <span class="metric-hint">${hint}</span>
    </article>
  `;
}

function alertItem(item) {
  return `
    <li class="alert-item">
      <strong>${item.type}</strong>
      <span>${item.label}</span>
      <em>${item.value}</em>
    </li>
  `;
}

export async function renderDashboard(root) {
  const dashboardData = await api.dashboard();
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">PERFORMANCE COMMAND</p>
        <h2>${t("dashboardTitle")}</h2>
      </div>
    </section>
    <section class="metric-grid">
      ${metricCard("有效周期", dashboardData.planKpi.cycleCount, "当前可执行的绩效考核周期")}
      ${metricCard("待审批计划", dashboardData.planKpi.approvalCount, `草稿 ${dashboardData.planKpi.draftCount} 份`)}
      ${metricCard("待员工自评", dashboardData.reviewKpi.selfReviewPendingCount, "审批通过后待员工提交")}
      ${metricCard("待经理评价", dashboardData.reviewKpi.managerReviewPendingCount, "员工自评完成后待经理打分")}
      ${metricCard("平均得分", dashboardData.reviewKpi.avgScore, `低分计划 ${dashboardData.reviewKpi.lowScoreCount} 份`)}
      ${metricCard("改进动作", dashboardData.improvementKpi.openActionCount, `逾期 ${dashboardData.improvementKpi.overdueActionCount} 条`)}
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>当前重点预警</h3></header>
        <ul class="alert-list">
          ${(dashboardData.alerts || []).map(alertItem).join("") || `<li class="muted">${t("emptyState")}</li>`}
        </ul>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>我的工作节奏</h3></header>
        <div class="task-list">
          <div class="task-card">
            <strong>待审批任务</strong>
            <span>系统已分配到当前账号的审批事项</span>
            <em>${dashboardData.improvementKpi.todoCount} 条</em>
          </div>
          <div class="task-card">
            <strong>未读通知</strong>
            <span>绩效计划、评价完成与改进动作提醒</span>
            <em>${dashboardData.improvementKpi.notificationCount} 条</em>
          </div>
          <div class="task-card">
            <strong>已完成评价</strong>
            <span>本系统内已形成最终得分和等级的绩效计划</span>
            <em>${dashboardData.planKpi.completedCount} 份</em>
          </div>
        </div>
      </article>
    </section>
  `;
}
