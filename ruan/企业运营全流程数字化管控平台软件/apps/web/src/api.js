import { clearSession, state } from "./state.js";

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    const text = await response.text();
    if (!response.ok) {
      throw new Error(text || "请求失败");
    }
    return text;
  }
  const payload = await response.json();
  if (!response.ok || payload.code !== "OK") {
    const message = payload.message || "请求失败";
    const error = new Error(message);
    error.payload = payload;
    throw error;
  }
  return payload.data;
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  const response = await fetch(path, {
    ...options,
    headers,
  });
  if (response.status === 401 && state.refreshToken) {
    try {
      const refresh = await fetch("/api/v1/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refreshToken: state.refreshToken }),
      });
      const refreshPayload = await parseResponse(refresh);
      state.token = refreshPayload.accessToken;
      localStorage.setItem("ops-platform-session", JSON.stringify(state));
      return request(path, options);
    } catch (error) {
      clearSession();
      throw error;
    }
  }
  return parseResponse(response);
}

function idempotentHeaders() {
  return { "Idempotency-Key": `${Date.now()}-${Math.random().toString(16).slice(2)}` };
}

export const api = {
  login(payload) {
    return request("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  logout(payload) {
    return request("/api/v1/auth/logout", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  me() {
    return request("/api/v1/users/me");
  },
  dashboard() {
    return request("/api/v1/dashboard/operations");
  },
  summary() {
    return request("/api/v1/masterdata/summary");
  },
  customers() {
    return request("/api/v1/customers?pageSize=8");
  },
  suppliers() {
    return request("/api/v1/suppliers?pageSize=8");
  },
  items() {
    return request("/api/v1/items?pageSize=10");
  },
  projects() {
    return request("/api/v1/projects?pageSize=8");
  },
  warehouses() {
    return request("/api/v1/warehouses?pageSize=8");
  },
  createCustomer(payload) {
    return request("/api/v1/customers", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  procurementRequests() {
    return request("/api/v1/procurement/requests?pageSize=8");
  },
  purchaseOrders() {
    return request("/api/v1/procurement/orders?pageSize=8");
  },
  createProcurementRequest(payload) {
    return request("/api/v1/procurement/requests", {
      method: "POST",
      headers: idempotentHeaders(),
      body: JSON.stringify(payload),
    });
  },
  createPurchaseOrder(payload) {
    return request("/api/v1/procurement/orders", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  receiveInventory(payload) {
    return request("/api/v1/inventory/receipts", {
      method: "POST",
      headers: idempotentHeaders(),
      body: JSON.stringify(payload),
    });
  },
  stockBalances() {
    return request("/api/v1/inventory/balances?pageSize=8");
  },
  salesOrders() {
    return request("/api/v1/sales/orders?pageSize=8");
  },
  contracts() {
    return request("/api/v1/contracts?pageSize=8");
  },
  createSalesOrder(payload) {
    return request("/api/v1/sales/orders", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  createContract(payload) {
    return request("/api/v1/contracts", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  budgets() {
    return request("/api/v1/finance/budgets?pageSize=8");
  },
  expenses() {
    return request("/api/v1/finance/expenses?pageSize=8");
  },
  payments() {
    return request("/api/v1/finance/payment-requests?pageSize=8");
  },
  receipts() {
    return request("/api/v1/finance/receipts?pageSize=8");
  },
  createBudget(payload) {
    return request("/api/v1/finance/budgets", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  createExpense(payload) {
    return request("/api/v1/finance/expenses", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  createPayment(payload) {
    return request("/api/v1/finance/payment-requests", {
      method: "POST",
      headers: idempotentHeaders(),
      body: JSON.stringify(payload),
    });
  },
  createReceipt(payload) {
    return request("/api/v1/finance/receipts", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  workflowTemplates() {
    return request("/api/v1/workflows/templates");
  },
  approvalTasks(view = "todo") {
    return request(`/api/v1/approvals/tasks?view=${view}`);
  },
  actTask(taskId, payload) {
    return request(`/api/v1/approvals/tasks/${taskId}/actions`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  auditLogs() {
    return request("/api/v1/audit-logs");
  },
  notifications() {
    return request("/api/v1/notifications");
  },
  markNotificationRead(notificationId) {
    return request(`/api/v1/notifications/${notificationId}/read`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  },
};
