# AI Slop 审查记录

- generated_at: 2026-05-27T20:48:43
- audit_mode: automated_ai_slop_check
- scope: apps/*, packages/*, project markdown files
- risk_level: LOW

## 审查结果
- 未发现模板化占位词与高频 AI 套话，阶段 3 可判定通过。

### 公共文件归属整理（规则/流程/生成）
- 2026-05-27：将生成逻辑统一收敛到 `E:\copyRight\workspace\scripts\build_materials.py`，项目内 `scripts/build_materials.py` 调整为委派入口，避免多项目分叉。
- 2026-05-27：将操作手册规则校验统一收敛到 `E:\copyRight\workspace\scripts\manual_style_validator.py`，项目内同名文件调整为 shim，仅用于 import 兼容。
- 2026-05-27：将截图执行脚本的通用修复同步到 `E:\copyRight\workspace\scripts\capture_screenshots_local.mjs`，避免项目内独有修复导致新需求复现。
- 规则归 SKILL：通用字体映射等规则已写入 `E:\copyRight\workspace\CodeDocumentGenerationRules.md`（由生成器执行落地）。
- 流程归 automation_prompt + pipeline_guard：未在单需求目录重复维护。
