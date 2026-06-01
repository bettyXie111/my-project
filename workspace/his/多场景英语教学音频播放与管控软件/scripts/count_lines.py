"""Count non-empty source-code lines for the generated project.

This is a project-local copy used by the gated pipeline.
"""

from __future__ import annotations

from pathlib import Path


def _resolve_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    if (cwd / "apps").exists() or (cwd / "packages").exists():
        return cwd
    return Path(__file__).resolve().parents[1]


REPO_ROOT = _resolve_repo_root()
SOURCE_ROOTS = [REPO_ROOT / "apps", REPO_ROOT / "packages", REPO_ROOT / "scripts"]
TARGET_SUFFIXES = {".py", ".js", ".mjs", ".css", ".html", ".sql", ".json"}
EXCLUDED_DIRS = {
    ".git",
    ".tools",
    "__pycache__",
    "node_modules",
    "run_reports",
    "tmp",
    "copyright-application-materials",
}


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in TARGET_SUFFIXES:
                continue
            files.append(path)
    return sorted(files)


def count_lines() -> int:
    total = 0
    for path in iter_source_files():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        total += sum(1 for line in content.splitlines() if line.strip())
    return total


if __name__ == "__main__":
    print(count_lines())

