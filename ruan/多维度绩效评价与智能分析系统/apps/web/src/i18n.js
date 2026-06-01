export const messages = {
  zhCN: {
    brand: "多维度绩效评价与智能分析系统",
    loginTitle: "让绩效计划、评价执行与改进闭环回到同一个系统",
    loginSubtitle: "覆盖指标库、绩效周期、审批、自评、经理评价、智能分析与改进行动",
    loginUser: "账号",
    loginPassword: "密码",
    loginAction: "登录系统",
    logout: "退出登录",
    navDashboard: "绩效看板",
    navMasterdata: "组织与指标库",
    navPlans: "绩效计划",
    navReviews: "评价执行",
    navAnalytics: "分析与改进",
    navWorkflow: "审批中心",
    navAudit: "审计与通知",
    dashboardTitle: "绩效总览",
    emptyState: "暂无数据，请先创建一条业务记录。",
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
