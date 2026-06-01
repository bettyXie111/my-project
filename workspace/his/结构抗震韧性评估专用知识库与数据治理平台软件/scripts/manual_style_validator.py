# -*- coding: utf-8 -*-
"""
Project-local compatibility shim for workspace shared rules.

公共文件：规则校验归 workspace/scripts/manual_style_validator.py
单需求目录仅保留同名模块，供生成脚本 import，避免规则分叉。
"""

from __future__ import annotations

import runpy
from pathlib import Path


_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "manual_style_validator.py"
if not _SCRIPT.exists():
    raise FileNotFoundError(f"workspace manual_style_validator.py missing: {_SCRIPT}")

globals().update(runpy.run_path(str(_SCRIPT)))

