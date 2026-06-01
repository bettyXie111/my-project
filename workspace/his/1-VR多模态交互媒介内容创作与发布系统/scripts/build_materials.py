# -*- coding: utf-8 -*-
"""
Per-requirement build entrypoint.

Policy:
- Requirement-specific adjustments live under `{A}/` (this directory tree).
- Shared/immutable implementation lives under `workspace/scripts/`.

This wrapper delegates to the shared generator while keeping an explicit,
project-local entrypoint for reproducibility.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Build copyright materials (per-requirement wrapper).")
    ap.add_argument("--name", required=True, help="Requirement/software name (must match the directory naming).")
    ap.add_argument(
        "--output-dir",
        default="..",
        help="Requirement directory containing markdown inputs (default: parent directory).",
    )
    ap.add_argument("--pdf-engine", default="word", choices=["libreoffice", "word", "edge"])
    ap.add_argument("--allow-pdf-fallback", action="store_true")
    ap.add_argument("--require-word-pdf", action="store_true")
    ap.add_argument("--kill-winword-before-pdf", action="store_true")
    ap.add_argument("--touch-md", action="store_true")
    ns, unknown = ap.parse_known_args()

    req_dir = (Path(__file__).resolve().parent / ns.output_dir).resolve()
    workspace_root = Path(__file__).resolve().parents[2]
    shared = workspace_root / "scripts" / "build_materials.py"
    if not shared.exists():
        raise FileNotFoundError(f"Shared build script not found: {shared}")

    cmd = [
        sys.executable,
        "-X",
        "utf8",
        str(shared),
        "--name",
        ns.name,
        "--output-dir",
        str(req_dir),
        "--pdf-engine",
        ns.pdf_engine,
    ]
    if ns.allow_pdf_fallback:
        cmd.append("--allow-pdf-fallback")
    if ns.require_word_pdf:
        cmd.append("--require-word-pdf")
    if ns.kill_winword_before_pdf:
        cmd.append("--kill-winword-before-pdf")
    if ns.touch_md:
        cmd.append("--touch-md")
    cmd.extend(unknown)

    cp = subprocess.run(cmd, cwd=workspace_root)
    return int(cp.returncode)


if __name__ == "__main__":
    raise SystemExit(main())

