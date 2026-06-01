# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REQUIREMENT_NAME = "食品安全指标快速检测与预警软件"


def main() -> int:
    parser = argparse.ArgumentParser(description="Project wrapper for generating the web system.")
    parser.add_argument("--project-dir", default=".", help="Project directory, default current directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    workspace_root = Path(__file__).resolve().parents[2]
    shared_generator = workspace_root / "shared" / "scripts" / "generate_web_system.py"
    cmd = [
        sys.executable,
        "-X",
        "utf8",
        str(shared_generator),
        "--project-dir",
        str(project_dir),
        "--requirement-name",
        REQUIREMENT_NAME,
    ]
    if args.force:
        cmd.append("--force")
    completed = subprocess.run(cmd, check=False)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
