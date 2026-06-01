import { api } from "../api.js";
import { setFlash, setSession } from "../state.js";
import { t } from "../i18n.js";

export function renderLogin(root, app) {
  root.innerHTML = `
    <section class="login-shell">
      <div class="login-card">
        <div class="hero-kicker">B2B OPERATIONS CONTROL</div>
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
          <span>样例账号：admin / admin123</span>
          <span>审批账号：director / admin123</span>
          <span>财务账号：fin01 / admin123</span>
        </div>
      </div>
      <div class="login-panel">
        <div class="panel-card">
          <strong>首期覆盖模块</strong>
          <ul>
            <li>统一登录、角色权限、组织与成本中心</li>
            <li>采购申请、采购订单、收货入库、库存余额</li>
            <li>销售订单、合同审批、回款登记</li>
            <li>预算控制、费用报销、付款申请、审计通知</li>
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
