import { api } from "../api.js";

export async function renderSales(root, app) {
  const [orders, contracts, customers, items] = await Promise.all([
    api.salesOrders(),
    api.contracts(),
    api.customers(),
    api.items(),
  ]);
  const firstCustomer = customers.items[0];
  const firstItem = items.items[0];
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">SALES & CONTRACT</p>
        <h2>销售订单与合同审批</h2>
      </div>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>创建销售订单</h3></header>
        <form id="sales-form" class="grid-form inline-3">
          <input name="customerId" value="${firstCustomer?.id || ""}" placeholder="客户 ID" />
          <input name="deliveryDate" type="date" />
          <input name="amountTotal" type="number" min="1" value="12000" />
          <button class="primary-button" type="submit">新建销售订单</button>
        </form>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>创建合同</h3></header>
        <form id="contract-form" class="grid-form inline-3">
          <input name="salesOrderId" placeholder="销售订单 ID" />
          <input name="expireDate" type="date" />
          <input name="amountTotal" type="number" min="1" value="18000" />
          <button class="secondary-button" type="submit">发起合同审批</button>
        </form>
      </article>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>销售订单</h3></header>
        <div class="table-shell">
          <table>
            <thead><tr><th>订单号</th><th>客户</th><th>金额</th><th>状态</th></tr></thead>
            <tbody>
              ${orders.items
                .map(
                  (item) => `
                  <tr>
                    <td>${item.order_no}</td>
                    <td>${item.customer_id}</td>
                    <td>${item.amount_total}</td>
                    <td><span class="status-pill">${item.status}</span></td>
                  </tr>
                `
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>合同</h3></header>
        <div class="table-shell">
          <table>
            <thead><tr><th>合同号</th><th>金额</th><th>回款进度</th><th>状态</th></tr></thead>
            <tbody>
              ${contracts.items
                .map(
                  (item) => `
                  <tr>
                    <td>${item.contract_no}</td>
                    <td>${item.amount_total}</td>
                    <td>${item.receipt_progress}%</td>
                    <td><span class="status-pill">${item.status}</span></td>
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
  root.querySelector("#sales-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createSalesOrder({
        customerId: formData.get("customerId"),
        deliveryDate: formData.get("deliveryDate"),
        amountTotal: Number(formData.get("amountTotal")),
        items: [{ itemId: firstItem.id, qty: 10, unitPrice: firstItem.unit_price || 200 }],
      });
      app.showSuccess("销售订单创建成功");
      await renderSales(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
  root.querySelector("#contract-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createContract({
        salesOrderId: formData.get("salesOrderId"),
        expireDate: formData.get("expireDate"),
        amountTotal: Number(formData.get("amountTotal")),
        attachments: [{ name: "样例合同.pdf" }],
      });
      app.showSuccess("合同已提交审批");
      await renderSales(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
}
