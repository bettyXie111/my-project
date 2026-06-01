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
  const response = await fetch(path, { ...options, headers });
  if (response.status === 401 && state.refreshToken) {
    try {
      const refresh = await fetch("/api/v1/auth/refresh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refreshToken: state.refreshToken }),
      });
      const refreshPayload = await parseResponse(refresh);
      state.token = refreshPayload.accessToken;
      localStorage.setItem("performance-platform-session", JSON.stringify(state));
      return request(path, options);
    } catch (error) {
      clearSession();
      throw error;
    }
  }
  return parseResponse(response);
}

export const api = {
  login(payload) {
    return request("/api/v1/auth/login", { method: "POST", body: JSON.stringify(payload) });
  },
  logout(payload) {
    return request("/api/v1/auth/logout", { method: "POST", body: JSON.stringify(payload) });
  },
  me() {
    return request("/api/v1/users/me");
  },
  dashboard() {
    return request("/api/v1/dashboard/performance");
  },
  orgUnits() {
    return request("/api/v1/org-units");
  },
  users() {
    return request("/api/v1/users?pageSize=20");
  },
  masterdataSummary() {
    return request("/api/v1/performance/masterdata/summary");
  },
  indicators() {
    return request("/api/v1/performance/indicators?pageSize=20");
  },
  cycles() {
    return request("/api/v1/performance/cycles?pageSize=20");
  },
  createIndicator(payload) {
    return request("/api/v1/performance/indicators", { method: "POST", body: JSON.stringify(payload) });
  },
  createCycle(payload) {
    return request("/api/v1/performance/cycles", { method: "POST", body: JSON.stringify(payload) });
  },
  plans() {
    return request("/api/v1/performance/plans?pageSize=20");
  },
  createPlan(payload) {
    return request("/api/v1/performance/plans", { method: "POST", body: JSON.stringify(payload) });
  },
  submitPlan(planId) {
    return request(`/api/v1/performance/plans/${planId}/submit`, { method: "POST", body: JSON.stringify({}) });
  },
  selfReview(planId, payload) {
    return request(`/api/v1/performance/plans/${planId}/self-review`, { method: "POST", body: JSON.stringify(payload) });
  },
  managerReview(planId, payload) {
    return request(`/api/v1/performance/plans/${planId}/manager-review`, { method: "POST", body: JSON.stringify(payload) });
  },
  analytics() {
    return request("/api/v1/performance/analytics/overview");
  },
  improvementActions() {
    return request("/api/v1/performance/improvement-actions?pageSize=20");
  },
  createImprovementAction(payload) {
    return request("/api/v1/performance/improvement-actions", { method: "POST", body: JSON.stringify(payload) });
  },
  workflowTemplates() {
    return request("/api/v1/workflows/templates");
  },
  approvalTasks(view = "todo") {
    return request(`/api/v1/approvals/tasks?view=${view}`);
  },
  actTask(taskId, payload) {
    return request(`/api/v1/approvals/tasks/${taskId}/actions`, { method: "POST", body: JSON.stringify(payload) });
  },
  auditLogs() {
    return request("/api/v1/audit-logs");
  },
  notifications() {
    return request("/api/v1/notifications");
  },
  markNotificationRead(notificationId) {
    return request(`/api/v1/notifications/${notificationId}/read`, { method: "POST", body: JSON.stringify({}) });
  },
};
