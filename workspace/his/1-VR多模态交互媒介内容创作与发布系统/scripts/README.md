# scripts（本需求专用）

本目录用于放置“每个需求项目都会修改/更新”的脚本入口或局部覆盖配置。

- 共享实现（尽量不做需求级修改）：`workspace/scripts/`
- 本需求的构建入口：`scripts/build_materials.py`（包装调用共享实现库 `workspace/scripts/build_materials.py`；流程入口以本目录脚本为准）

约定：
- 需求级差异优先通过 `{A}/source_doc_filters.json`、`{A}/screenshot_plan.json` 等配置实现；
- 只有当需求间差异不可配置化时，才在本目录新增需求级脚本，并保持“最薄封装”。
