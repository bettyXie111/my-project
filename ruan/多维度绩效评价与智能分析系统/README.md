# 企业运营全流程数字化管控平台

基于最新需求文档生成的可运行 Web 系统，目录结构遵循 PRD 中的 `apps/web`、`apps/api`、`packages/shared-contracts`、`scripts` 约定。考虑到当前环境没有 `Node`、`Java`、`Maven` 和第三方 Python Web 框架，本实现采用 **Python 标准库后端 + 零构建静态前端**，但保留了需求文档要求的模块边界、接口契约、种子数据、权限、审批和自动化测试。

## 运行方式

1. 初始化样例数据：

```bash
python scripts/seed_demo_data.py
```

2. 启动系统：

```bash
python apps/api/main.py
```

3. 打开浏览器访问：

```text
http://127.0.0.1:8000
```

## 样例账号

- `admin / admin123`
- `director / admin123`
- `sales01 / admin123`
- `proc01 / admin123`
- `fin01 / admin123`
- `wh01 / admin123`
- `audit01 / admin123`

## 自动化验证

```bash
python scripts/run_tests.py
```

该命令会：

- 运行 `unittest` 集成测试
- 校验总代码量是否达到 3000 行以上

## 已实现模块

- 统一登录、刷新令牌、退出登录、当前用户信息
- 角色权限、组织、成本中心、系统配置
- 主数据：客户、供应商、物料、项目、仓库
- 工作流模板、待办、审批动作、抄送通知
- 销售订单、合同审批
- 采购申请、采购订单、收货入库、库存余额
- 预算、费用报销、付款申请、回款登记
- 经营看板、站内通知、文件签名、审计日志
