"""Run the automated verification suite and line-count check."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run() -> int:
    test_cmd = [sys.executable, "-m", "unittest", "discover", "apps/api/tests", "-v"]
    test_result = subprocess.run(test_cmd, cwd=REPO_ROOT, check=False)
    if test_result.returncode != 0:
        return test_result.returncode
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
