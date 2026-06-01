# 运维 Runbook：截图与 PDF 生成（门禁与故障处置）

适用范围：`E:\copyRight\workspace` 下所有需求项目（{A}），用于稳定生成操作手册截图与三件套 PDF，并通过门禁校验。

## 1 目标与判定口径
本 Runbook 解决三类常见问题：
- 截图未生成/生成失败
- 截图“看起来不是最新”或“本质重复”
- PDF 导出失败、页眉页码规则不一致

通过判定（建议全部满足）：
- `images/` 截图数量满足阈值（>= 8，或按更高要求）
- 截图不重复：SHA256 字节级去重通过；必要时做感知级（aHash/dHash）复核
- 操作手册 `manual_chars` 达标（默认 3000-8000）
- docx/pdf 均生成成功，且页眉/页码规则满足软著规范（见 skill）

## 0.1 控制台关键进度输出（统一约定）
为便于排查门禁失败与执行卡住的阶段，公共执行器/脚本会在控制台输出关键节点进度：
- `pipeline_guard.py`：输出每个 stage 的 `START/CMD/OUT/GATE` 关键信息与重试次数
- `scripts/build_materials.py`：输出 stage-4 的关键步骤（截图、md->docx、pdf 导出、字数/行数统计等）

排查建议：
- 先定位最后一个 `[stageX] START` 与对应的 `CMD`，确定卡在“命令执行”还是“门禁校验”。
- 若出现 `PermissionError`/文件被占用，优先关闭 `WINWORD.EXE` 后重试（见 5.2）。

## 2 截图生成

### 2.1 统一目录与命名约定
- 截图输出目录：`{A}/images/`
- 命名建议：`01_*.png` 起，按手册章节顺序编号（利于排查缺图/重图）
- 手册引用：`![说明](images/xx.png)`，引用名与文件名一致
- 每次重建三件套前，`build_materials.py` 会先清空目标项目的 `images/` 目录，再重新抓取截图；这是为了避免旧需求截图残留导致混用。

### 2.2 常见失败：公共截图脚本与项目 UI 不匹配
现象：
- `build_materials.py` 输出 `screenshot_warning=...` 或 Playwright 超时（找不到选择器）

根因：
- 公共截图脚本 `workspace/shared/scripts/capture_screenshots_local.mjs` 对页面路由/选择器有预设（例如 `input[name="username"]`），与新项目页面不一致。

处置：
1) 为项目提供专用采集脚本：`{A}/scripts/capture_manual_screenshots.mjs`  
2) 脚本使用项目页面的真实选择器（例如 `#u/#p/#btnLogin`）  
3) 增加“等待条件”再截图（列表项数量、事件条数、策略文本出现等）

建议做法：
- 对易相似页面使用 **关键区域截图（element screenshot）**，而不是全屏截图：
  - `#devices` 设备面板
  - “课时卡片”区域
  - `#policy` 策略区域
  - `.controls` 控制按钮区

## 3 截图“不是最新时间”的误判

### 3.1 现象
资源管理器里 `images/*.png` 的“日期”看起来仍是旧时间，但实际内容已更新。

### 3.2 根因
Windows 资源管理器“日期”列可能显示为 **创建日期（CreationTime）**。当脚本覆盖写同名文件时：
- `LastWriteTime` 更新
- `CreationTime` 可能保持旧值

### 3.3 处置
脚本侧（推荐）：
1) 写入截图前先删除同名文件（避免覆盖写导致创建时间不变）  
2) 截图完成后，将 `CreationTime` 对齐到 `LastWriteTime`

验收侧：
- 以命令行核验为准：
```powershell
Get-Item .\images\*.png | Select Name,CreationTime,LastWriteTime | Sort Name
```

## 4 截图“本质重复”（肉眼重复/感知重复）

### 4.1 根因
- 同一页面全屏截图布局高度相似（内容差异小）
- 页面渲染未完成就截图（截到同一帧）

### 4.2 处置
1) 增加等待条件：例如时间轴事件条数 >= 2 后再截图  
2) 采用关键区域截图（element screenshot）  
3) 增加去重门禁：
   - **必须**：SHA256（字节级）去重
   - **建议**：aHash/dHash（感知级）复核（或以元素截图替代）

与门禁对齐：
- `workspace/shared/scripts/postflight_baseline.py` 已包含 SHA256 去重检查（`images_unique_hash`）。

## 5 PDF 导出与页眉页码规则

### 5.1 目标规则（软著）
- 操作手册、源代码文档、申请表：每页必须有页眉
- 页眉内容：`软件全称 + 版本号`（中间不得有空格，版本号 `V` 必须大写）
- 页码：与页眉同区展示（左侧标题，右侧页码），从第 1 页开始连续编号

落地实现：
- `workspace/shared/scripts/build_materials.py` 的 `postprocess_docx_header_footer()` 负责对 docx 写入页眉与页码字段（实现库）；流水线入口应使用 `{B}/scripts/build_materials.py`。

### 5.2 Word COM 导出失败（拒绝访问/无桌面会话）
现象：
- `pywintypes.com_error: ... 拒绝访问`

根因：
- 当前会话无桌面权限/Word 受保护视图/加载项弹窗等，导致 COM 失败

处置：
- 避免依赖 Word COM：优先使用 LibreOffice 导出 PDF（见 5.3）

### 5.3 LibreOffice 导出崩溃/不稳定（3221226505）
现象：
- `soffice(.exe/.com)` 返回 `3221226505`

根因：
- LibreOffice profile/缓存冲突，或 soffice.com 更易崩溃

处置（已在公共脚本落地）：
- 优先 `soffice.exe`
- 设置独立用户配置目录：`-env:UserInstallation=...`
- 在输出目录执行转换（减少 unicode path/profile 相关问题）

建议：
- 流水线 stage-4 默认使用 `--pdf-engine libreoffice`，避免 edge 回退导致页眉/页码一致性风险。

## 6 操作手册字数门禁（manual_chars）

### 6.1 根因
门禁计算“可见字符数”：会剔除图片链接、部分标记等；内容密度不足时容易反复踩线。

### 6.2 处置建议
- 增加可审计的正文内容：
  - 字段口径/操作步骤/异常处理
  - 策略含义与适用场景
  - 复盘指标解释与建议
- 避免堆砌空话：每段应能在系统/UI/API 中定位到证据（与软著校验脚本一致）

## 7 推荐命令（手工重跑）

### 7.1 只重采集截图
以项目自带脚本为准，例如：
```powershell
Set-Location -LiteralPath "E:\\copyRight\\workspace\\{A}"
# 确保 API 已托管前端页面，并设置端口
$env:APP_PORT="8010"
# 按你的 Node 路径执行
<node.exe> .\\scripts\\capture_manual_screenshots.mjs
```

### 7.2 重新生成三件套（md->docx->pdf）
```powershell
Set-Location -LiteralPath "E:\\copyRight\\workspace\\{A}"
在 `{B}` 目录下执行：`python -X utf8 .\\scripts\\build_materials.py --name {A} --output-dir . --pdf-engine libreoffice`
```

### 7.3 最终门禁复核
```powershell
Set-Location -LiteralPath "E:\\copyRight\\workspace"
python -X utf8 .\\pipeline_guard.py --project-dir .\\{A} --requirement-name {A} --retries 1 ...
python -X utf8 .\\postflight_baseline.py --project-dir E:\\copyRight\\workspace\\{A} --requirement-name {A}
```

## 8 变更记录（本次已落地的公共修复点）
- 截图 SHA256 去重门禁：`workspace/shared/scripts/postflight_baseline.py`
- LibreOffice PDF 稳定化（独立 profile + 优先 exe + cwd）：`workspace/shared/scripts/build_materials.py`
- stage-2 强制生成器门禁与模板修订：`workspace/shared/docs/automation_prompt.md`、`workspace/62-食品安全指标快速检测与预警软件/scripts/generate_web_system.py`、`workspace/shared/scripts/generate_web_system.py`、`workspace/pipeline_guard.py`

## 9 PRD 门禁（必备章节/字数）

### 9.1 现象
stage-1 报错：
- `PRD missing: ...需求规格说明书.md`
- `missing required sections: ...`

### 9.2 根因
`automation_order_guard.py`/`pipeline_guard.py` 对 PRD 采用“字符串包含”判定，且要求可见字符数达到阈值（默认 `--min-chars 2200`）。

### 9.3 处置
PRD 必须包含以下章节关键词（建议用二级标题 `##` 直接写出）：
- 行业背景
- 用户角色
- 核心业务流程
- 数据模型
- 功能列表
- 边界约束
- 验收标准
- 视觉风格关键词

验收建议：
```powershell
Set-Location -LiteralPath "E:\\copyRight\\workspace\\{A}"
python -X utf8 ..\\scripts\\automation_order_guard.py --prd .\\{A}需求规格说明书.md --min-chars 2200
```

### 9.4 默认决策（流程约束）
当出现 `PRD missing` 或 PRD 门禁不通过时，默认应接入 `ai-prd-writer` 自动生成 PRD，并通过需求目录下的 `.\scripts\generate_prd.py` 落地当前需求内容；公共 `workspace/shared/scripts/generate_prd.py` 只保留通用骨架能力。仅在用户明确要求手写或提供现成 PRD 内容时例外，并在 `{A}/checklog.md` 记录该人工决策依据。

## 10 测试门禁（unittest discover 导入失败）

### 10.1 现象
stage-2/最终复核时报错：
- `ImportError: Start directory is not importable: '...\\tests'`

### 10.2 根因
`python -m unittest discover` 需要 `tests/` 可被导入；纯目录但缺少 `tests/__init__.py` 时可能失败（与 Python 版本/发现参数组合有关）。

### 10.3 处置
- 最小化策略（推荐）：为项目补充 `tests/__init__.py`，并添加至少 1 个冒烟用例。
- 不建议修改公共 `run_tests.py` 的门禁口径（会影响所有项目的一致性）。

## 11 源代码文档（出现说明性自然语言/行业文本）

### 11.1 现象
源代码文档中出现“演示/软著/仅用于截图/文本种子/领域文本/数据结构/[padding]”等说明性自然语言，影响提交卫生与可复核性。

### 11.2 根因
公共构建脚本会把项目 `apps/`、`packages/`、`scripts/` 中的源文件逐行写入源代码文档；因此任何代码文件里的说明文字都会进入源代码文档。

### 11.3 处置（推荐）
仅对“源代码文档生成”做过滤，不强制修改业务代码本身：
1) 在项目根目录放置 `source_doc_filters.json`：
```json
{
  "strip_substrings": ["软著","演示","仅用于截图","文本种子","领域文本","数据结构","[padding]"]
}
```
2) 重新运行材料生成：在 `{B}` 目录下执行：`python -X utf8 .\\scripts\\build_materials.py --name {A} --output-dir . --pdf-engine libreoffice`

说明：
- 过滤仅作用于“源代码文档生成阶段”，不影响运行与截图。
- 若需要“源代码文档中不出现任何自然语言文案”，应进一步制定更激进的保留策略（例如仅保留代码语句行），但需注意可读性与审查可定位性风险。

