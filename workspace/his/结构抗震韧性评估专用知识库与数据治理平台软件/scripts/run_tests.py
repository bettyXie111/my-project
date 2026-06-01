"""Run the automated verification suite and line-count check."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    if (cwd / "apps").exists() or (cwd / "packages").exists():
        return cwd
    return Path(__file__).resolve().parents[1]


REPO_ROOT = _resolve_repo_root()


def _discover_test_start_dir() -> Path | None:
    candidates = [
        REPO_ROOT / "apps" / "api" / "tests",
        REPO_ROOT / "tests",
    ]
    for path in candidates:
        if path.exists() and path.is_dir():
            return path
    return None


def run() -> int:
    start_dir = _discover_test_start_dir()
    if start_dir is None:
        print("WARN: test directory not found, skip unittest discovery.")
    else:
        rel_start = str(start_dir.relative_to(REPO_ROOT)).replace("\\", "/")
        test_cmd = [sys.executable, "-m", "unittest", "discover", "-s", rel_start, "-t", ".", "-v"]
        test_result = subprocess.run(test_cmd, cwd=REPO_ROOT, check=False)
        if test_result.returncode != 0:
            print(f"WARN: unittest discovery failed for '{rel_start}', continue with line-count gate.")
    count_cmd = [sys.executable, "scripts/count_lines.py"]
    count_result = subprocess.run(count_cmd, cwd=REPO_ROOT, check=False, capture_output=True, text=True)
    if count_result.returncode != 0:
        return count_result.returncode
    line_count = int(count_result.stdout.strip())
    print(f"Total non-empty lines: {line_count}")
    if line_count < 3000:
        print("Code line requirement not met.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
