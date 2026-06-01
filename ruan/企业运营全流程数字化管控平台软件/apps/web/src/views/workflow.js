import { api } from "../api.js";

function taskActions(task) {
  return `
    <button class="mini-button" data-action="approve" data-task="${task.id}">通过</button>
    <button class="mini-button ghost" data-action="reject" data-task="${task.id}">驳回</button>
  `;
}

export async function renderWorkflow(root, app) {
  const [templates, todoTasks, doneTasks, initiated] = await Promise.all([
    api.workflowTemplates(),
    api.approvalTasks("todo"),
    api.approvalTasks("done"),
    api.approvalTasks("initiated"),
  ]);
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">WORKFLOW HUB</p>
        <h2>流程模板、待办与已办</h2>
      </div>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>待办任务</h3></header>
        <div class="task-list">
          ${todoTasks
            .map(
              (task) => `
              <div class="task-card">
                <strong>${task.node_name}</strong>
                <span>${task.biz_type} / ${task.biz_id}</span>
                <em>截至 ${task.due_at}</em>
                <div class="task-actions">${taskActions(task)}</div>
              </div>
            `
            )
            .join("") || `<p class="muted">暂无待办</p>`}
        </div>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>已办任务</h3></header>
        <div class="task-list">
          ${doneTasks
            .map(
              (task) => `
              <div class="task-card done">
                <strong>${task.node_name}</strong>
                <span>${task.biz_type} / ${task.biz_id}</span>
                <em>动作 ${task.action || "-"}</em>
              </div>
            `
            )
            .join("") || `<p class="muted">暂无已办</p>`}
        </div>
      </article>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>我的发起</h3></header>
        <div class="task-list">
          ${initiated
            .map(
              (wf) => `
              <div class="task-card">
                <strong>${wf.title}</strong>
                <span>${wf.biz_type} / ${wf.biz_id}</span>
                <em>${wf.status}</em>
              </div>
            `
            )
            .join("") || `<p class="muted">暂无发起记录</p>`}
        </div>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>流程模板</h3></header>
        <div class="task-list">
          ${templates
            .map(
              (template) => `
              <div class="task-card">
                <strong>${template.name}</strong>
                <span>${template.biz_type}</span>
                <em>${(template.definition?.nodes || []).length} 个节点</em>
              </div>
            `
            )
            .join("")}
        </div>
      </article>
    </section>
  `;
  root.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await api.actTask(button.dataset.task, {
          action: button.dataset.action === "approve" ? "APPROVE" : "REJECT",
          comment: button.dataset.action === "approve" ? "页面快速通过" : "页面快速驳回",
        });
        app.showSuccess("审批动作已提交");
        await renderWorkflow(root, app);
      } catch (error) {
        app.showError(error);
      }
    });
  });
}
