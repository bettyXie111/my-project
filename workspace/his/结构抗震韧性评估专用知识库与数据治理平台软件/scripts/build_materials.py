# -*- coding: utf-8 -*-
"""
Project-local entrypoint that delegates to the workspace shared generator.

Why:
- 公共文件：生成逻辑归 workspace/scripts/build_materials.py
- 单需求目录只保留可执行入口，避免规则/实现分叉
"""

from __future__ import annotations

import runpy
from pathlib import Path


def _workspace_script() -> Path:
    # .../<project>/scripts/build_materials.py -> .../<workspace>/scripts/build_materials.py
    return Path(__file__).resolve().parents[2] / "scripts" / "build_materials.py"


if __name__ == "__main__":
    script = _workspace_script()
    if not script.exists():
        raise FileNotFoundError(f"workspace build_materials.py missing: {script}")
    runpy.run_path(str(script), run_name="__main__")

