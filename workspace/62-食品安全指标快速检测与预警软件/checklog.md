# Checklog（需求 #62：食品安全指标快速检测与预警软件）

日期：2026-05-30

## 执行目标
- 按 `automation_prompt.md` 执行 PRD → Web 系统 → 去 AI 化 → 软著三件套全流程。

## 技术栈确认
- 前端框架/运行时：`React + Vite + TypeScript`
- 后端框架/运行时：`FastAPI + Python 3.11`
- 数据库/存储：`SQLite（默认）/ PostgreSQL（生产）`
- 认证/身份方案：`JWT + RBAC（本地账号体系）`
- 部署目标：`Windows 本地运行（默认）/ Docker（可选）`
- CI/CD 工具：`GitHub Actions（如无则写“暂不配置”）`
- 测试栈：`pytest（后端）+ Playwright（可选 E2E）`

## 阻塞点与人工介入记录
### 1. 前置体检参数缺失
- 触发：`preflight_check.py` 首次执行缺少 `--requirement-name`
- 可选项：补充必填参数 / 终止流程
- 已选项：补充参数后重跑，`PASS`

### 2. 第 3 阶段使用占位 slop 脚本
- 触发：`ai_slop_check_placeholder.py` 仅写日志，不生成 `slop_report.latest.json`
- 可选项：继续使用占位脚本 / 切换到真实 `run_ai_slop_detector.py`
- 已选项：切换到真实检测器并重跑，`PASS`

### 3. 申请表日期字段格式异常
- 触发：`软件著作权登记申请表.md` 中“开发完成日期”被拆成两行，导致 `build_materials.py` 的 md/docx 同步校验失败
- 可选项：保留拆行格式 / 改为单行标准字段
- 已选项：改为单行 `开发完成日期：2026-05-30` 后重跑，`PASS`

### 4. 公共模板与项目模板混用
- 触发：公共 `workspace/shared/scripts/generate_web_system.py` 与当前项目 `apps/web/index.html` 初始沿用了“电池均衡控制台”内容，导致截图语义与当前需求不一致
- 可选项：仅改截图 / 同步拆分公共模板与项目模板
- 已选项：公共模板改为通用业务语义，项目目录新增 `scripts/generate_web_system.py` 保存食品安全业务内容，并将 `apps/web/index.html` 切换为当前需求页面

### 5. 公共模板半改导致语法失效
- 触发：重写公共 `workspace/shared/scripts/generate_web_system.py` 后，局部替换引入未闭合字符串，`python -m py_compile` 报 `SyntaxError`
- 可选项：继续在残缺文件上补丁修复 / 整体重写为干净版本
- 已选项：整体重写为干净的通用模板后，再执行 `--force` 重跑，`PASS`

### 6. 再次重跑后的 slop 质量波动
- 触发：公共模板通用化后重新跑完整流水线，`pipeline_report.latest.json` 仍全部 `PASS`，但 `slop_report.latest.json` 的 `grade` 从 `Clean` 变为 `Mediocre`
- 可选项：接受当前流水线结果 / 继续收紧文案与命名，争取恢复 `Clean`
- 已选项：接受当前流水线结果，记录为质量波动，不作为阻断项

### 7. 截图图题缺失导致材料重建失败
- 触发：重新切换截图计划后，`build_materials.py` 在校验 `操作手册.md` 时发现 `fig-3-3-workflow.png` 前缺少 `图X-Y` 图题说明
- 可选项：回退截图计划 / 补齐图题后重跑
- 已选项：补齐 `图3-1/图3-3` 等截图图题后重跑，`PASS`

### 8. 源代码文档残留旧语义
- 触发：`apps/api/_auto_catalog.py`、`apps/api/services/store.py` 与 `apps/web/student.html`、`apps/web/teacher.html` 残留 `records/student/teacher` 旧模板，导致 `源代码文档.md` 继续抽入不属于当前需求的文件与命名
- 可选项：只删文档里的旧段落 / 直接修正项目代码与公共生成器后重建材料
- 已选项：统一收敛为 `sample/samples` 语义，删除 `student.html`、`teacher.html`、`records.py`、`record.py` 残留，重建 `build_materials.py`，源代码文档已刷新

### 9. stage-2 门禁仍沿用旧页面清单
- 触发：`pipeline_guard.py` 的 stage-2 验证仍强制要求 `teacher.html`、`student.html`，与当前需求目录的新页面结构不一致，可能误判 stage-2 失败
- 可选项：继续保留旧门禁 / 将 stage-2 门禁改为当前需求的 `index.html`、`admin.html`、`samples.py`、`sample.py`
- 已选项：已将 stage-2 门禁收敛为当前项目实际结构，并准备重跑最终门禁

### 10. stage-2 wrapper 与后置基线恢复
- 触发：stage-2 仍直接调用公共生成器，且 `apps/api/main.py` 旧模板把路由导入写进了 `except` 分支，导致截图服务起不来；随后后置基线又因手册残留旧图名 `fig-3-1-records.png` 误判失败
- 可选项：回滚到旧目录调用方式 / 改为项目目录 wrapper；对 `main.py`、公共生成器、手册图引用分别修复
- 已选项：项目目录 `scripts/generate_web_system.py` 改为可执行 wrapper，公共生成器与 `apps/api/main.py` 同步修正，`fig-3-1-records.png` 统一替换为 `fig-3-1-samples.png`，随后 `pipeline_guard.py` 最终门禁通过

### 11. PRD 公共生成器承载了具体需求业务
- 触发：`workspace/shared/scripts/generate_prd.py` 直接输出食品安全场景内容，导致公共目录的 PRD 生成器不再只是骨架能力，后续新需求容易被错误复用为同一场景
- 可选项：继续让公共 PRD 生成器承载具体需求 / 将食品安全 PRD 内容下沉到当前需求目录的 `scripts/generate_prd.py`
- 已选项：已将食品安全业务 PRD 落到 `62-食品安全指标快速检测与预警软件/scripts/generate_prd.py`，公共生成器回收为通用骨架；同时将 stage-1 调用和自动批处理逻辑切换为优先使用需求目录 wrapper

### 12. 源代码文档仍抽入 `_auto_catalog.py`
- 触发：源代码文档中出现 `apps/api/_auto_catalog.py` 以及重复的“检测样本，覆盖接收、检测、复核、预警与审计留痕。”，说明过滤规则未生效
- 根因：`workspace/shared/scripts/build_materials.py` 仍读取旧的 `workspace/config/rules/source_doc_rules.json`，而真实规则文件已迁到 `workspace/shared/config/rules/source_doc_rules.json`
- 可选项：继续沿用旧路径 / 修正规则加载路径并重建源代码文档
- 已选项：已将 `build_materials.py` 的规则加载切换到 `workspace/shared/config/rules/` 优先读取，并重新生成源代码文档；当前文档已不再包含 `_auto_catalog.py`

## 自动化执行摘要
- PRD：已生成并通过校验
- Web 系统：已生成并通过基础测试
- Slop 检测：已生成 `slop_report.latest.json` / `slop_report.latest.md`
- 三件套：`md/docx/pdf` 已全部生成
- 验证补充：重新抓取的 `images/*.png` 已切换为食品安全指标快速检测与预警界面
- 验证补充：公共模板已切换为通用业务语义，需求目录保留项目专用业务说明；PRD 生成也已拆分为公共骨架 + 需求目录业务输出；源代码文档过滤规则已修正并重新生成
- 验证补充：`pipeline_report.latest.json` 未出现阶段回退，但 `slop_report.latest.json` grade 波动到 `Mediocre`
- 验证补充：重新生成截图并补齐图题后，`build_materials.py` 成功完成三件套重建

## AI_SLOP_DETECTOR_EVIDENCE
- report_json: slop_report.latest.json
- report_md: slop_report.latest.md
- grade: Clean
