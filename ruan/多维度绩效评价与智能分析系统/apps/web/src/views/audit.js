import { api } from "../api.js";

export async function renderAudit(root, app) {
  const [auditLogs, notifications] = await Promise.all([api.auditLogs(), api.notifications()]);
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">AUDIT & ALERTS</p>
        <h2>审计日志与站内通知</h2>
      </div>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>审计日志</h3></header>
        <div class="table-shell">
          <table>
            <thead><tr><th>动作</th><th>业务类型</th><th>业务 ID</th><th>请求号</th></tr></thead>
            <tbody>
              ${(auditLogs.items || [])
                .slice(0, 10)
                .map(
                  (item) => `
                  <tr>
                    <td>${item.action_type}</td>
                    <td>${item.biz_type}</td>
                    <td>${item.biz_id}</td>
                    <td>${item.request_id}</td>
                  </tr>
                `
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>通知中心</h3></header>
        <div class="task-list">
          ${notifications
            .map(
              (item) => `
              <div class="task-card ${item.read_at ? "done" : ""}">
                <strong>${item.title}</strong>
                <span>${item.content}</span>
                <em>${item.biz_ref_type || "SYSTEM"}</em>
                ${item.read_at ? `<span class="muted">已读</span>` : `<button class="mini-button" data-read="${item.id}">设为已读</button>`}
              </div>
            `
            )
            .join("")}
        </div>
      </article>
    </section>
  `;
  root.querySelectorAll("[data-read]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await api.markNotificationRead(button.dataset.read);
        app.showSuccess("通知已设为已读");
        await renderAudit(root, app);
      } catch (error) {
        app.showError(error);
      }
    });
  });
}
