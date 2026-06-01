export const routes = [
  { key: "dashboard", label: "经营看板" },
  { key: "masterdata", label: "主数据" },
  { key: "procurement", label: "采购与库存" },
  { key: "sales", label: "销售与合同" },
  { key: "finance", label: "费用与预算" },
  { key: "workflow", label: "待办与流程" },
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
