$ErrorActionPreference = "Stop"

$path = "C:\Users\31556\.codex\skills\custom\chinese-copyright-application\SKILL.md"
$marker = "## 工作区实现补充（同步自公共规则）"

$text = Get-Content -LiteralPath $path -Raw
if ($text -like "*$marker*") {
  Get-Item -LiteralPath $path | Select-Object FullName,Length,LastWriteTime
  exit 0
}

$append = @'

## 工作区实现补充（同步自公共规则）

> 说明：以下内容同步自工作区公共规则与脚本实现（`E:\copyRight\workspace`），用于减少“skill 规范”与“自动化实现”之间的分叉。若与本文件其他条款冲突，以本文件更严格条款或用户当前会话明确要求为准。

### 1）操作手册模板骨架门禁（强制）
- `{A}操作手册.md` 必须包含模板关键章节标题：
  - 系统入口与登录
  - 首页操作
  - 一级功能模块与二级菜单操作（允许简化为“一级功能模块”）
  - 端到端操作流程演示
  - 附录
- “章节编号”允许前置插入“文档定位与适用对象”等章节，但不得缺失上述模板章节标题。
- 每张 `images/*.png` 的 Markdown 引用后，必须在附近出现图题说明行，格式形如：`图X-Y 描述`（支持 `图3-2a`）。
- 对应实现与门禁：`workspace/shared/scripts/manual_style_validator.py`；生成阶段调用点：`workspace/shared/scripts/build_materials.py`（在 md→docx/pdf 前强制校验）。

### 2）源代码文档纯度门禁（强制）
为避免“行业领域叙述/PRD 章节/运营文案”从 HTML/README 等渗入源代码文档：
- 生成阶段过滤（默认启用）：`workspace/shared/scripts/build_materials.py` 会过滤 `行业背景/用户角色/核心业务流程/数据模型/功能列表/边界约束/验收标准/视觉风格关键词/版本快照/发布留痕/资源清单/交互摘要/占位页面` 等关键词行。
- 交付门禁：`workspace/shared/scripts/postflight_baseline.py` 增加 `source_doc_purity` 检查，若 `{A}源代码文档.md` 命中上述关键词直接判定 FAIL。
- 项目仍可按需新增 `source_doc_filters.json` 做更精细的补充过滤，但不得削弱上述公共门禁。

### 3）操作手册字数阈值对齐（强制）
- 默认字数阈值对齐为不少于 6000（以 `workspace/shared/scripts/build_materials.py` 的 `MIN_MANUAL_CHARS` 为准）。
'@

$text = $text.TrimEnd() + $append + "`r`n"
Set-Content -LiteralPath $path -Value $text -Encoding UTF8
Get-Item -LiteralPath $path | Select-Object FullName,Length,LastWriteTime


