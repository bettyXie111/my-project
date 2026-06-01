import { api } from "../api.js";

function userOptions(items) {
  return items.map((item) => `<option value="${item.id}">${item.display_name} / ${item.username}</option>`).join("");
}

function orgOptions(items) {
  return items.map((item) => `<option value="${item.id}">${item.name}</option>`).join("");
}

function cycleOptions(items) {
  return items.map((item) => `<option value="${item.id}">${item.cycle_name}</option>`).join("");
}

export async function renderPlans(root, app) {
  const [plans, cycles, users, orgUnits] = await Promise.all([api.plans(), api.cycles(), api.users(), api.orgUnits()]);
  const employeeCandidates = users.items.filter((item) => !["admin", "director"].includes(item.username));
  const managerCandidates = users.items.filter((item) => ["fin01", "director", "admin"].includes(item.username));
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">PLAN FACTORY</p>
        <h2>绩效计划创建、草稿留存与审批发起</h2>
      </div>
    </section>
    <section class="panel-card">
      <header class="panel-head"><h3>新增绩效计划</h3></header>
      <form id="plan-form" class="grid-form">
        <label><span>绩效周期</span><select name="cycleId">${cycleOptions(cycles.items)}</select></label>
        <label><span>被评价员工</span><select name="employeeUserId">${userOptions(employeeCandidates)}</select></label>
        <label><span>直属经理</span><select name="managerUserId">${userOptions(managerCandidates)}</select></label>
        <label><span>所属组织</span><select name="orgUnitId">${orgOptions(orgUnits)}</select></label>
        <input name="title" value="季度绩效计划" placeholder="计划标题" />
        <button class="primary-button" type="submit">创建计划</button>
      </form>
      <p class="muted">若未显式选择指标卡，系统将自动使用当前生效的绩效指标库生成默认评分卡。</p>
    </section>
    <section class="panel-card">
      <header class="panel-head"><h3>绩效计划列表</h3></header>
      <div class="table-shell">
        <table>
          <thead><tr><th>计划编号</th><th>周期</th><th>员工</th><th>直属经理</th><th>状态</th><th>得分</th><th>操作</th></tr></thead>
          <tbody>
            ${(plans.items || [])
              .map(
                (item) => `
                <tr>
                  <td>${item.planNo}</td>
                  <td>${item.cycleName}</td>
                  <td>${item.employeeName}</td>
                  <td>${item.managerName}</td>
                  <td><span class="status-pill">${item.status}</span></td>
                  <td>${item.totalScore || 0}</td>
                  <td>
                    ${item.status === "DRAFT" ? `<button class="mini-button" data-submit-plan="${item.id}">提交审批</button>` : `<span class="muted">-</span>`}
                  </td>
                </tr>
              `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;

  root.querySelector("#plan-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createPlan({
        cycleId: formData.get("cycleId"),
        employeeUserId: formData.get("employeeUserId"),
        managerUserId: formData.get("managerUserId"),
        orgUnitId: formData.get("orgUnitId"),
        title: formData.get("title"),
      });
      app.showSuccess("绩效计划草稿已创建");
      await renderPlans(root, app);
    } catch (error) {
      app.showError(error);
    }
  });

  root.querySelectorAll("[data-submit-plan]").forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        await api.submitPlan(button.dataset.submitPlan);
        app.showSuccess("绩效计划已提交审批");
        await renderPlans(root, app);
      } catch (error) {
        app.showError(error);
      }
    });
  });
}
