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

function kpiBar(label, amount, maxReference) {
  const percent = Math.min((amount / maxReference) * 100, 100);
  return `
    <div class="bar-row">
      <span>${label}</span>
      <div><i class="bar-fill" data-percent="${percent.toFixed(2)}"></i></div>
      <strong>${amount}</strong>
    </div>
  `;
}

export async function renderDashboard(root) {
  const dashboardData = await api.dashboard();
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">OPERATIONS COMMAND</p>
        <h2>${t("dashboardTitle")}</h2>
      </div>
    </section>
    <section class="metric-grid">
      ${metricCard("销售订单数", dashboardData.salesKpi.orderCount, `合同 ${dashboardData.salesKpi.contractCount} 份`)}
      ${metricCard("采购申请数", dashboardData.procurementKpi.requestCount, `待审 ${dashboardData.procurementKpi.pendingRequestCount} 条`)}
      ${metricCard("库存 SKU", dashboardData.inventoryKpi.stockSkuCount, `库存总量 ${dashboardData.inventoryKpi.stockQty}`)}
      ${metricCard("报销单数", dashboardData.expenseKpi.claimCount, `回款金额 ${dashboardData.expenseKpi.receiptAmount}`)}
      ${metricCard("我的待办", dashboardData.todoKpi.todoCount, `已办 ${dashboardData.todoKpi.doneCount}`)}
      ${metricCard("未读通知", dashboardData.todoKpi.unreadNotifications, "站内信与预警")}
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>经营金额概览</h3></header>
        <div class="bar-stack">
          ${kpiBar("销售", dashboardData.salesKpi.orderAmount, 2000)}
          ${kpiBar("采购", dashboardData.procurementKpi.poAmount, 2000)}
          ${kpiBar("回款", dashboardData.expenseKpi.receiptAmount, 2000)}
        </div>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>风险提示</h3></header>
        <ul class="alert-list">
          ${(dashboardData.alerts || []).map(alertItem).join("") || `<li class="muted">${t("emptyState")}</li>`}
        </ul>
      </article>
    </section>
  `;

  root.querySelectorAll(".bar-fill").forEach((element) => {
    element.style.width = `${element.dataset.percent || "0"}%`;
  });
}
