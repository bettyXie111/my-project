import { api } from "../api.js";
import { setFlash, setSession } from "../state.js";
import { t } from "../i18n.js";

export function renderLogin(root, app) {
  root.innerHTML = `
    <section class="login-shell">
      <div class="login-card">
        <div class="hero-kicker">PERFORMANCE INTELLIGENCE</div>
        <h1>${t("loginTitle")}</h1>
        <p class="muted">${t("loginSubtitle")}</p>
        <form id="login-form" class="grid-form">
          <label>
            <span>${t("loginUser")}</span>
            <input name="username" value="admin" autocomplete="username" />
          </label>
          <label>
            <span>${t("loginPassword")}</span>
            <input type="password" name="password" value="admin123" autocomplete="current-password" />
          </label>
          <button class="primary-button" type="submit">${t("loginAction")}</button>
        </form>
        <div class="tip-strip">
          <span>系统管理员：admin / admin123</span>
          <span>绩效负责人：director / admin123</span>
          <span>直属经理：fin01 / admin123</span>
          <span>员工自评：sales01 / admin123</span>
        </div>
      </div>
      <div class="login-panel">
        <div class="panel-card">
          <strong>本期覆盖模块</strong>
          <ul>
            <li>组织与用户、绩效指标库、绩效周期</li>
            <li>绩效计划创建、审批流转与待办处理</li>
            <li>员工自评、经理评价、自动算分与等级判定</li>
            <li>智能预警、部门排名、低分改进动作与审计通知</li>
          </ul>
        </div>
      </div>
    </section>
  `;
  root.querySelector("#login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      const payload = await api.login({
        username: formData.get("username"),
        password: formData.get("password"),
      });
      setSession(payload);
      setFlash("success", "登录成功");
      await app.bootstrapUser();
      app.navigate("dashboard");
    } catch (error) {
      app.showError(error);
    }
  });
}
