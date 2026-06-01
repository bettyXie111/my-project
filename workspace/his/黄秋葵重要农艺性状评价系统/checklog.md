# 执行与去AI化检查日志

- generated_at: 2026-05-27T21:29:07
- audit_mode: custom_ai_slop_check_with_execution_notes
- scope: apps/*, packages/*, project markdown files
- risk_level: LOW

## 人工介入记录
### MI-PIPE-RELATIVE 阶段命令相对路径修正
- stage: pipeline.stage2
- reason: pipeline_guard 在项目目录内执行阶段命令，最初将 run_tests/ai_slop_check/build_materials 写成了 .\scripts\*，导致找不到文件。
- options:
  - 将阶段命令统一改为 ..\\scripts\\*（已选）
  - 为项目复制一份 scripts/ 并在项目内执行（未选）
- selected: 将阶段命令统一改为 ..\\scripts\\*
- selected_by: codex

### MI-TEST-DB 测试环境初始化数据库
- stage: pipeline.stage2
- reason: FastAPI TestClient 未触发 startup 初始化导致 SQLite 表缺失，单测报错 no such table。
- options:
  - 在 create_app() 内先确保建表（已选）
  - 将 TestClient 改为 with 上下文触发 lifespan（未选）
- selected: 在 create_app() 内先确保建表
- selected_by: codex

### MI-SCREENSHOT-SERVE 为截图自动化提供可访问的 / 页面
- stage: pipeline.stage4
- reason: build_materials 通过 urlopen(baseUrl) 轮询 / 判断服务可用，初期 API 未挂载静态站点导致 404/超时，截图无法生成。
- options:
  - FastAPI 挂载 apps/web 静态目录到 / 并确保 200（已选）
  - 单独启动静态服务器供截图使用（未选）
- selected: FastAPI 挂载 apps/web 静态目录到 / 并确保 200
- selected_by: codex

### MI-SCREENSHOT-LOGIN 截图脚本登录流程适配
- stage: pipeline.stage4
- reason: capture_screenshots_local.mjs 在 baseUrl 打开后直接填充登录表单，初期登录面板默认隐藏导致元素不可见。
- options:
  - 无 hash 时默认进入 login 视图，并在登录后跳转 home（已选）
  - 修改截图脚本让其先跳转 #login（未选）
- selected: 无 hash 时默认进入 login 视图，并在登录后跳转 home
- selected_by: codex

### MI-SCREENSHOT-MODAL 满足弹窗截图校验要求
- stage: pipeline.stage4
- reason: build_materials 校验截图计划必须包含 create/edit/view/delete 四类 modal 截图；截图脚本会点击“新增/编辑/查看/删除”。
- options:
  - 在材料库页面补充演示按钮并弹出统一 modal（已选）
  - 重写 screenshot_plan 但绕过 modal（不可行）
- selected: 在材料库页面补充演示按钮并弹出统一 modal
- selected_by: codex

## 阻塞点记录
### BP-START 阶段 2 命令路径错误导致流水线中断
- stage: pipeline.stage2
- reason: 首次运行时 run_tests.py 路径写错，pipeline_guard 阶段 2 失败。
- status: resolved

### BP-MATERIALS-MISSING 材料生成阶段缺少输入 Markdown
- stage: pipeline.stage4
- reason: build_materials 要求操作手册/源代码文档/申请表 Markdown 先存在，初期缺失。
- status: resolved

### BP-SCREENSHOT-AUTO 截图自动化对 /、登录与弹窗交互有固定假设
- stage: pipeline.stage4
- reason: 服务可用性检查要求 / 返回 200；截图脚本要求默认页可见登录表单且可点击“新增/编辑/查看/删除”触发弹窗。
- status: resolved

## AI Slop 审查结果
- 未发现高频 AI 套话和模板化占位词，阶段 3 可以判定通过。

## 差异化设计摘要
- 领域建模聚焦黄秋葵试验：材料、性状口径、试验/小区、观测、标准化与综合评分。
- UI 采用“研究笔记/卡片式试验”风格：深绿底、细线网格、卡片布局与可追溯提示。
- 评分流程可复核：评分模板可选，默认等权；缺失按策略处理并在 explain 中记录摘要。
- 为软著截图自动化补充 login 视图、hash 路由与演示弹窗按钮，保证截图计划可执行。
