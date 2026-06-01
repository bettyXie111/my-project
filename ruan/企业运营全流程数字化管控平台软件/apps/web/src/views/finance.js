import { api } from "../api.js";

export async function renderFinance(root, app) {
  const [budgets, expenses, payments, receipts] = await Promise.all([
    api.budgets(),
    api.expenses(),
    api.payments(),
    api.receipts(),
  ]);
  const firstBudget = budgets.items[0];
  const firstExpense = expenses.items[0];
  const firstContractReceipt = receipts.items[0];
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">FINANCE CONTROL</p>
        <h2>预算、报销、付款与回款</h2>
      </div>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>新增预算</h3></header>
        <form id="budget-form" class="grid-form inline-4">
          <input name="budgetYear" type="number" value="2026" />
          <input name="budgetMonth" type="number" value="11" />
          <input name="budgetAmount" type="number" value="150000" />
          <input name="budgetKey" placeholder="预算键" />
          <button class="primary-button" type="submit">新增预算</button>
        </form>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>发起费用报销</h3></header>
        <form id="expense-form" class="grid-form inline-4">
          <input name="claimUserId" value="${app.state.user?.id || ""}" />
          <input name="costCenterId" value="${firstBudget?.cost_center_id || ""}" />
          <input name="budgetKey" value="${firstBudget?.budget_key || ""}" />
          <input name="amountTotal" type="number" value="3200" />
          <button class="secondary-button" type="submit">提交报销</button>
        </form>
      </article>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>创建付款申请</h3></header>
        <form id="payment-form" class="grid-form inline-4">
          <input name="sourceType" value="EXPENSE_CLAIM" />
          <input name="sourceId" value="${firstExpense?.id || ""}" />
          <input name="payeeName" placeholder="收款方" value="广州分公司" />
          <input name="amountTotal" type="number" value="3200" />
          <button class="secondary-button" type="submit">发起付款</button>
        </form>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>登记回款</h3></header>
        <form id="receipt-form" class="grid-form inline-4">
          <input name="contractId" value="${receipts.items[0]?.contract_id || ""}" />
          <input name="amount" type="number" value="5000" />
          <input name="receiptDate" type="date" />
          <input name="method" value="BANK_TRANSFER" />
          <button class="secondary-button" type="submit">登记回款</button>
        </form>
      </article>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>预算</h3></header>
        <div class="table-shell">
          <table>
            <thead><tr><th>预算键</th><th>预算额</th><th>已用</th><th>控制模式</th></tr></thead>
            <tbody>
              ${budgets.items
                .map(
                  (item) => `
                  <tr>
                    <td>${item.budget_key}</td>
                    <td>${item.budget_amount}</td>
                    <td>${item.used_amount}</td>
                    <td>${item.control_mode}</td>
                  </tr>
                `
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>费用与付款</h3></header>
        <div class="table-shell">
          <table>
            <thead><tr><th>编号</th><th>金额</th><th>状态</th><th>类型</th></tr></thead>
            <tbody>
              ${expenses.items
                .slice(0, 4)
                .map(
                  (item) => `
                  <tr>
                    <td>${item.claim_no}</td>
                    <td>${item.amount_total}</td>
                    <td>${item.status}</td>
                    <td>${item.expense_type}</td>
                  </tr>
                `
                )
                .join("")}
              ${payments.items
                .slice(0, 4)
                .map(
                  (item) => `
                  <tr>
                    <td>${item.payment_no}</td>
                    <td>${item.amount_total}</td>
                    <td>${item.status}</td>
                    <td>${item.source_type}</td>
                  </tr>
                `
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  `;

  root.querySelector("#budget-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createBudget({
        budgetYear: Number(formData.get("budgetYear")),
        budgetMonth: Number(formData.get("budgetMonth")),
        orgUnitId: firstBudget.org_unit_id,
        costCenterId: firstBudget.cost_center_id,
        budgetAmount: Number(formData.get("budgetAmount")),
        budgetKey: formData.get("budgetKey"),
      });
      app.showSuccess("预算创建成功");
      await renderFinance(root, app);
    } catch (error) {
      app.showError(error);
    }
  });

  root.querySelector("#expense-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createExpense({
        claimUserId: formData.get("claimUserId"),
        costCenterId: formData.get("costCenterId"),
        amountTotal: Number(formData.get("amountTotal")),
        expenseType: "TRAVEL",
        budgetKey: formData.get("budgetKey"),
        attachments: [{ name: "交通票据.pdf" }],
      });
      app.showSuccess("报销单已提交审批");
      await renderFinance(root, app);
    } catch (error) {
      app.showError(error);
    }
  });

  root.querySelector("#payment-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createPayment({
        sourceType: formData.get("sourceType"),
        sourceId: formData.get("sourceId"),
        payeeName: formData.get("payeeName"),
        amountTotal: Number(formData.get("amountTotal")),
        plannedDate: new Date().toISOString().slice(0, 10),
      });
      app.showSuccess("付款申请已创建");
      await renderFinance(root, app);
    } catch (error) {
      app.showError(error);
    }
  });

  root.querySelector("#receipt-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createReceipt({
        contractId: formData.get("contractId"),
        amount: Number(formData.get("amount")),
        receiptDate: formData.get("receiptDate"),
        method: formData.get("method"),
      });
      app.showSuccess("回款登记成功");
      await renderFinance(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
}
