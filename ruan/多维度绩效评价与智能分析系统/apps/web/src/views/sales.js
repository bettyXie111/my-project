import { api } from "../api.js";

const SCORE_CODES = [
  { code: "KPI-DELIVERY", label: "目标达成率" },
  { code: "KPI-COLLAB", label: "跨部门协同" },
  { code: "KPI-QUALITY", label: "交付质量" },
  { code: "KPI-INNOVATION", label: "改进创新" },
  { code: "KPI-CUSTOMER", label: "客户满意度" },
];

function planOptions(items) {
  return items
    .map((item) => `<option value="${item.id}">${item.planNo} / ${item.employeeName} / ${item.status}</option>`)
    .join("");
}

function scoreInputs(prefix) {
  return SCORE_CODES.map(
    (item) => `
      <label>
        <span>${item.label}</span>
        <input type="number" name="${prefix}_${item.code}" min="0" max="100" value="85" />
      </label>
    `
  ).join("");
}

function buildScores(formData, prefix) {
  return SCORE_CODES.map((item) => ({
    code: item.code,
    score: Number(formData.get(`${prefix}_${item.code}`)),
    comment: `${item.label}评分已提交`,
  }));
}

export async function renderReviews(root, app) {
  const plans = await api.plans();
  const selfCandidates = (plans.items || []).filter((item) => item.status === "APPROVED");
  const managerCandidates = (plans.items || []).filter((item) => item.status === "SELF_REVIEW_SUBMITTED");
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">REVIEW EXECUTION</p>
        <h2>员工自评、经理评价与结果归档</h2>
      </div>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>提交员工自评</h3></header>
        <form id="self-review-form" class="grid-form">
          <label><span>绩效计划</span><select name="planId">${planOptions(selfCandidates)}</select></label>
          ${scoreInputs("self")}
          <textarea name="summary" placeholder="填写本周期自评总结">本周期围绕目标达成、协同效率和客户满意度完成了既定任务。</textarea>
          <button class="primary-button" type="submit">提交自评</button>
        </form>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>提交经理评价</h3></header>
        <form id="manager-review-form" class="grid-form">
          <label><span>绩效计划</span><select name="planId">${planOptions(managerCandidates)}</select></label>
          ${scoreInputs("manager")}
          <textarea name="summary" placeholder="填写经理评价结论">总体表现稳定，建议保留优势项并持续改进跨部门协同能力。</textarea>
          <button class="primary-button" type="submit">提交经理评价</button>
        </form>
      </article>
    </section>
    <section class="panel-card">
      <header class="panel-head"><h3>绩效结果总览</h3></header>
      <div class="table-shell">
        <table>
          <thead><tr><th>计划编号</th><th>员工</th><th>状态</th><th>总分</th><th>等级</th></tr></thead>
          <tbody>
            ${(plans.items || [])
              .map(
                (item) => `
                <tr>
                  <td>${item.planNo}</td>
                  <td>${item.employeeName}</td>
                  <td><span class="status-pill">${item.status}</span></td>
                  <td>${item.totalScore || 0}</td>
                  <td>${item.finalGrade || "-"}</td>
                </tr>
              `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;

  root.querySelector("#self-review-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.selfReview(formData.get("planId"), {
        summary: formData.get("summary"),
        scores: buildScores(formData, "self"),
      });
      app.showSuccess("员工自评已提交");
      await renderReviews(root, app);
    } catch (error) {
      app.showError(error);
    }
  });

  root.querySelector("#manager-review-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.managerReview(formData.get("planId"), {
        summary: formData.get("summary"),
        scores: buildScores(formData, "manager"),
      });
      app.showSuccess("经理评价已提交");
      await renderReviews(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
}
