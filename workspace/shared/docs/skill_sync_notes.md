# Skill/规范同步说明（需同步到技能仓库的内容）

> 说明：本仓库可写目录为 `E:\copyRight\workspace`。以下条目属于对公共规则/skill 的补充或收束，建议同步回对应 skill 文档（如 `chinese-copyright-application/SKILL.md`）以避免规则分叉。

## chinese-copyright-application（软著三件套）

### 操作手册模板骨架门禁（新增）
- 公共实现：`workspace/shared/scripts/manual_style_validator.py`
- 门禁要点：
  1) `{A}操作手册.md` 必须包含模板关键章节标题（允许章节编号偏移；“一级功能模块与二级菜单操作”允许简化为“一级功能模块”）。
  2) 每张 `images/*.png` 引用后，必须在附近出现图题说明行：`图X-Y 描述`（支持 `图3-2a`）。
- 调用点：生成入口使用 `{B}/scripts/build_materials.py`；其内部会调用实现库 `workspace/shared/scripts/build_materials.py` 在生成 docx/pdf 前强制校验。

### 源代码文档纯度门禁（新增）
- 生成阶段过滤：实现库 `workspace/shared/scripts/build_materials.py` 默认过滤 PRD/行业叙述/占位类关键词行（入口仍为 `{B}/scripts/build_materials.py`）。
- 交付门禁：`workspace/shared/scripts/postflight_baseline.py` 增加 `source_doc_purity` 检查，命中关键词直接 FAIL。

### 操作手册字数阈值对齐（调整）
- 公共实现库：`workspace/shared/scripts/build_materials.py`（流水线入口：`{B}/scripts/build_materials.py`）
- 调整：操作手册默认字数范围改为 `3000-8000`，以 `workspace/shared/config/manual_rules.json` 为准。

