import { api } from "./api.js";
import { t } from "./i18n.js";
import { getCurrentRoute, navigate, routes } from "./router.js";
import { clearSession, persistState, setFlash, setUserContext, state } from "./state.js";
import { renderAudit } from "./views/audit.js";
import { renderDashboard } from "./views/dashboard.js";
import { renderAnalytics } from "./views/finance.js";
import { renderLogin } from "./views/login.js";
import { renderMasterdata } from "./views/masterdata.js";
import { renderPlans } from "./views/procurement.js";
import { renderReviews } from "./views/sales.js";
import { renderWorkflow } from "./views/workflow.js";

const viewMap = {
  dashboard: renderDashboard,
  masterdata: renderMasterdata,
  plans: renderPlans,
  reviews: renderReviews,
  analytics: renderAnalytics,
  workflow: renderWorkflow,
  audit: renderAudit,
};

const app = {
  state,
  navigate(routeKey) {
    navigate(routeKey);
  },
  async bootstrapUser() {
    const payload = await api.me();
    setUserContext(payload);
  },
  showSuccess(message) {
    setFlash("success", message);
    render();
  },
  showError(error) {
    const requestId = error?.payload?.requestId ? `（请求号：${error.payload.requestId}）` : "";
    setFlash("error", `${error.message || "请求失败"}${requestId}`);
    render();
  },
};

function renderFlash() {
  if (!state.flash) {
    return "";
  }
  return `<div class="flash ${state.flash.type}">${state.flash.text}</div>`;
}

function renderSidebar() {
  const activeRoute = state.route;
  return `
    <aside class="sidebar">
      <div class="brand-block">
        <strong>${t("brand")}</strong>
        <span>统一绩效计划、审批、自评、经理评价、智能预警与改进行动</span>
      </div>
      <nav class="nav-list">
        ${routes
          .map(
            (route) => `
            <a href="#${route.key}" class="nav-item ${route.key === activeRoute ? "active" : ""}">
              ${route.label}
            </a>
          `
          )
          .join("")}
      </nav>
      <div class="sidebar-footer">
        <div class="user-card">
          <strong>${state.user?.displayName || "-"}</strong>
          <span>${(state.user?.roleCodes || []).join(" / ")}</span>
        </div>
        <button id="logout-button" class="mini-button ghost">${t("logout")}</button>
      </div>
    </aside>
  `;
}

async function renderAuthenticated() {
  const root = document.getElementById("app");
  root.innerHTML = `
    <div class="app-shell">
      ${renderSidebar()}
      <main class="main-view">
        ${renderFlash()}
        <div id="view-root" class="view-root"></div>
      </main>
    </div>
  `;
  root.querySelector("#logout-button").addEventListener("click", async () => {
    try {
      await api.logout({ refreshToken: state.refreshToken });
    } catch (error) {
      console.warn(error);
    } finally {
      clearSession();
      setFlash("success", "已退出登录");
      render();
    }
  });
  const renderer = viewMap[state.route] || renderDashboard;
  try {
    await renderer(root.querySelector("#view-root"), app);
  } catch (error) {
    app.showError(error);
  }
}

async function render() {
  state.route = getCurrentRoute();
  persistState();
  if (!state.token) {
    renderLogin(document.getElementById("app"), app);
    return;
  }
  await renderAuthenticated();
}

window.addEventListener("hashchange", render);

(async () => {
  if (state.token) {
    try {
      await app.bootstrapUser();
    } catch (error) {
      clearSession();
    }
  }
  await render();
})();
