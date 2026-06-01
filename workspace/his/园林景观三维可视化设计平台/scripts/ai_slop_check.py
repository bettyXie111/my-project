# -*- coding: utf-8 -*-
from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    script = workspace_root / "scripts" / "ai_slop_check.py"
    if not script.exists():
        raise FileNotFoundError(f"Missing workspace script: {script}")
    sys.path.insert(0, str(workspace_root / "scripts"))
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()

