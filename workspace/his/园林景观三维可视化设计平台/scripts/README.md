# scripts 说明

本目录放置“项目内”辅助脚本，用于本地自检与维护。

## 文件列表
- `count_lines.py`：统计本项目代码非空行数（门禁用）。
- `api_self_check.py`：启动本地服务并对关键 API 做快速自检。
- `data_tools.py`：对 `project_state.json` 做字段校验与排序规范化。
- `ai_slop_check.py`：调用工作区公共脚本进行去模板化审查。
- `build_materials.py`：调用工作区公共脚本生成三件套材料。

## 使用建议
- 日常修改后可先运行 `python scripts/api_self_check.py` 做快速回归。
- 需要稳定 diff 时可运行 `python scripts/data_tools.py` 规范化 state 文件排序。

