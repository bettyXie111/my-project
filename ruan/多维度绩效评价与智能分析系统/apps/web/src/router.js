export const routes = [
  { key: "dashboard", label: "绩效看板" },
  { key: "masterdata", label: "组织与指标库" },
  { key: "plans", label: "绩效计划" },
  { key: "reviews", label: "评价执行" },
  { key: "analytics", label: "分析与改进" },
  { key: "workflow", label: "审批中心" },
  { key: "audit", label: "审计与通知" },
];

export function getCurrentRoute() {
  const hash = window.location.hash.replace("#", "").trim();
  if (!hash) {
    return "dashboard";
  }
  return hash;
}

export function navigate(routeKey) {
  window.location.hash = routeKey;
}
