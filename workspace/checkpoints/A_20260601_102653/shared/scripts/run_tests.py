"""Run automated verification and the line-count gate.

Execution model
---------------
This script is executed from inside a generated project directory by `pipeline_guard.py`.
The generated project usually contains `apps/` and/or `packages/`, while the shared helper
scripts live in the workspace-level `scripts/` directory (this file).

Test strategy
-------------
Prefer `pytest` when available and when tests exist, but always provide a `unittest`
fallback so the pipeline stays runnable in minimal environments.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class TestRunResult:
    framework: str  # pytest|unittest|none
    attempted: bool
    passed: bool
    exit_code: int | None
    message: str


def _resolve_repo_root() -> Path:
    # Workspace root that contains this `scripts/` directory.
    return Path(__file__).resolve().parents[1]


REPO_ROOT = _resolve_repo_root()


def _discover_test_start_dir(project_root: Path) -> Path | None:
    candidates = [
        project_root / "apps" / "api" / "tests",
        project_root / "tests",
    ]
    for path in candidates:
        if path.exists() and path.is_dir():
            return path
    return None


def _pytest_available() -> bool:
    try:
        import pytest  # noqa: F401

        return True
    except Exception:
        return False


def _has_pytest_tests(project_root: Path, start_dir: Path) -> bool:
    # Heuristics: treat as pytest-based if config exists OR there are pytest-style test files.
    config_candidates = [
        project_root / "pytest.ini",
        project_root / "pyproject.toml",
        project_root / "setup.cfg",
        project_root / "tox.ini",
    ]
    if any(p.exists() for p in config_candidates):
        return True
    for p in start_dir.rglob("test_*.py"):
        if p.is_file():
            return True
    return False


def _run_pytest(project_root: Path, start_dir: Path) -> TestRunResult:
    rel_start = str(start_dir.relative_to(project_root)).replace("\\", "/")
    cmd = [sys.executable, "-m", "pytest", rel_start, "-q"]
    proc = subprocess.run(cmd, cwd=project_root, check=False, capture_output=True, text=True)
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    merged = "\n".join([s for s in [out, err] if s]).strip()
    ok = proc.returncode == 0
    return TestRunResult(
        framework="pytest",
        attempted=True,
        passed=ok,
        exit_code=proc.returncode,
        message=merged or ("PASS" if ok else f"FAIL(exit={proc.returncode})"),
    )


def _run_unittest(project_root: Path, start_dir: Path) -> TestRunResult:
    rel_start = str(start_dir.relative_to(project_root)).replace("\\", "/")
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", rel_start, "-t", ".", "-v"]
    proc = subprocess.run(cmd, cwd=project_root, check=False, capture_output=True, text=True)
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    merged = "\n".join([s for s in [out, err] if s]).strip()
    ok = proc.returncode == 0
    return TestRunResult(
        framework="unittest",
        attempted=True,
        passed=ok,
        exit_code=proc.returncode,
        message=merged or ("PASS" if ok else f"FAIL(exit={proc.returncode})"),
    )


def run() -> int:
    project_root = Path.cwd().resolve()
    start_dir = _discover_test_start_dir(project_root)
    if start_dir is None:
        print("WARN: test directory not found, skip unittest discovery.")
    else:
        results: list[TestRunResult] = []

        # 1) Prefer pytest when it is available *and* pytest tests are detected.
        if _pytest_available() and _has_pytest_tests(project_root, start_dir):
            r = _run_pytest(project_root, start_dir)
            results.append(r)
            print(f"[tests] pytest attempted exit={r.exit_code} passed={r.passed}")
            if not r.passed:
                print("[tests] pytest output (truncated):")
                print((r.message[:1200] + ("..." if len(r.message) > 1200 else "")).rstrip())

        # 2) Fallback: unittest discover (also runs when pytest is unavailable, or no pytest tests detected).
        if not results or (results and not results[-1].passed):
            r = _run_unittest(project_root, start_dir)
            results.append(r)
            print(f"[tests] unittest attempted exit={r.exit_code} passed={r.passed}")
            if not r.passed:
                print("[tests] unittest output (truncated):")
                print((r.message[:1200] + ("..." if len(r.message) > 1200 else "")).rstrip())
                print("[tests] FAIL: test execution failed.")
                return 1

        # If pytest was attempted and failed but unittest passed, the pipeline should still fail.
        if any(r.framework == "pytest" and r.attempted and not r.passed for r in results):
            print("[tests] FAIL: pytest attempted but did not pass.")
            return 1

    count_cmd = [sys.executable, str(REPO_ROOT / "scripts" / "count_lines.py")]
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
