export const messages = {
  zhCN: {
    brand: "企业运营全流程数字化管控平台",
    loginTitle: "统一经营台账与流程控制",
    loginSubtitle: "覆盖销售、采购、库存、预算、费用、回款与审计",
    loginUser: "账号",
    loginPassword: "密码",
    loginAction: "登录系统",
    logout: "退出登录",
    navDashboard: "经营看板",
    navMasterdata: "主数据",
    navProcurement: "采购与库存",
    navSales: "销售与合同",
    navFinance: "费用与预算",
    navWorkflow: "待办与流程",
    navAudit: "审计与通知",
    dashboardTitle: "经营总览",
    emptyState: "暂无数据，先创建一条业务记录。",
    retry: "重试",
    save: "保存",
    create: "创建",
    approve: "通过",
    reject: "驳回",
    markRead: "设为已读",
  },
};

export function t(key) {
  return messages.zhCN[key] || key;
}
