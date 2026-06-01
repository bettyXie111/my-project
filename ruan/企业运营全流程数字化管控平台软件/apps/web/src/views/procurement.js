import { api } from "../api.js";

function requestRows(items) {
  return items
    .map(
      (item) => `
        <tr>
          <td>${item.request_no}</td>
          <td>${item.amount_total}</td>
          <td>${item.need_date}</td>
          <td><span class="status-pill">${item.status}</span></td>
        </tr>
      `
    )
    .join("");
}

function orderRows(items) {
  return items
    .map(
      (item) => `
        <tr>
          <td>${item.po_no}</td>
          <td>${item.amount_total}</td>
          <td>${item.execution_rate}%</td>
          <td><span class="status-pill">${item.status}</span></td>
        </tr>
      `
    )
    .join("");
}

export async function renderProcurement(root, app) {
  const [requests, orders, items, suppliers, warehouses, balances] = await Promise.all([
    api.procurementRequests(),
    api.purchaseOrders(),
    api.items(),
    api.suppliers(),
    api.warehouses(),
    api.stockBalances(),
  ]);
  const firstItem = items.items[0];
  const firstSupplier = suppliers.items[0];
  const firstWarehouse = warehouses.items[0];
  root.innerHTML = `
    <section class="page-header">
      <div>
        <p class="eyebrow">PROCUREMENT & INVENTORY</p>
        <h2>采购申请、采购订单与收货入库</h2>
      </div>
    </section>
    <section class="panel-card">
      <header class="panel-head"><h3>发起采购申请</h3></header>
      <form id="request-form" class="grid-form inline-4">
        <input name="requestOrgId" value="org_dummy_replaced" placeholder="申请组织 ID" />
        <input name="costCenterId" value="cc_dummy_replaced" placeholder="成本中心 ID" />
        <input name="budgetKey" placeholder="预算键" />
        <input name="needDate" type="date" />
        <button class="primary-button" type="submit">提交申请</button>
      </form>
      <p class="muted">默认将使用样例物料 ${firstItem?.name || ""} 生成申请明细。</p>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>采购申请</h3></header>
        <div class="table-shell">
          <table>
            <thead><tr><th>申请单号</th><th>金额</th><th>需求日期</th><th>状态</th></tr></thead>
            <tbody>${requestRows(requests.items)}</tbody>
          </table>
        </div>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>采购订单</h3></header>
        <div class="table-shell">
          <table>
            <thead><tr><th>订单号</th><th>金额</th><th>执行率</th><th>状态</th></tr></thead>
            <tbody>${orderRows(orders.items)}</tbody>
          </table>
        </div>
      </article>
    </section>
    <section class="panel-grid">
      <article class="panel-card">
        <header class="panel-head"><h3>生成采购订单</h3></header>
        <form id="po-form" class="grid-form inline-3">
          <input name="requestId" placeholder="审批通过的采购申请 ID" />
          <input name="supplierId" value="${firstSupplier?.id || ""}" placeholder="供应商 ID" />
          <input name="expectedReceiptDate" type="date" />
          <button class="secondary-button" type="submit">创建采购订单</button>
        </form>
      </article>
      <article class="panel-card">
        <header class="panel-head"><h3>收货入库</h3></header>
        <form id="receipt-form" class="grid-form inline-3">
          <input name="purchaseOrderId" placeholder="采购订单 ID" />
          <input name="warehouseId" value="${firstWarehouse?.id || ""}" placeholder="仓库 ID" />
          <input name="qty" type="number" min="1" value="5" />
          <button class="secondary-button" type="submit">执行入库</button>
        </form>
      </article>
    </section>
    <section class="panel-card">
      <header class="panel-head"><h3>库存余额</h3></header>
      <div class="table-shell">
        <table>
          <thead><tr><th>库存记录 ID</th><th>仓库</th><th>物料</th><th>现存量</th></tr></thead>
          <tbody>
            ${balances.items
              .map(
                (item) => `
                <tr>
                  <td>${item.id}</td>
                  <td>${item.warehouse_id}</td>
                  <td>${item.item_id}</td>
                  <td>${item.qty_on_hand}</td>
                </tr>
              `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
  const presetOrg = requests.items[0]?.request_org_id || "";
  const presetCostCenter = requests.items[0]?.cost_center_id || "";
  root.querySelector("input[name='requestOrgId']").value = presetOrg;
  root.querySelector("input[name='costCenterId']").value = presetCostCenter;
  root.querySelector("input[name='budgetKey']").value = requests.items[0]?.budget_key || "";

  root.querySelector("#request-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createProcurementRequest({
        requestOrgId: formData.get("requestOrgId"),
        costCenterId: formData.get("costCenterId"),
        budgetKey: formData.get("budgetKey"),
        needDate: formData.get("needDate"),
        items: [{ itemId: firstItem.id, qty: 3, unitPrice: firstItem.unit_price || 120 }],
      });
      app.showSuccess("采购申请已提交并进入审批");
      await renderProcurement(root, app);
    } catch (error) {
      app.showError(error);
    }
  });

  root.querySelector("#po-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.createPurchaseOrder({
        requestId: formData.get("requestId"),
        supplierId: formData.get("supplierId"),
        expectedReceiptDate: formData.get("expectedReceiptDate"),
      });
      app.showSuccess("采购订单已生成");
      await renderProcurement(root, app);
    } catch (error) {
      app.showError(error);
    }
  });

  root.querySelector("#receipt-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    try {
      await api.receiveInventory({
        purchaseOrderId: formData.get("purchaseOrderId"),
        warehouseId: formData.get("warehouseId"),
        items: [{ itemId: firstItem.id, qty: Number(formData.get("qty")) }],
      });
      app.showSuccess("入库成功");
      await renderProcurement(root, app);
    } catch (error) {
      app.showError(error);
    }
  });
}
