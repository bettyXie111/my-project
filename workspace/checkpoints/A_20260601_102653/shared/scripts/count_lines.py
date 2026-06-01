"""Count effective source-code lines for the generated project.

Rules:
- Exclude blank/whitespace-only lines.
- Exclude "invalid/filler" lines that are too short to be meaningful:
  - a single visible character (after trimming), e.g. "#"
  - a single non-alphanumeric character, e.g. "{", "}", ";"
- Exclude lines that contain only invisible/formatting characters.
"""

from __future__ import annotations

import argparse
import re
import unicodedata
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


_NON_MEANINGFUL_SINGLE_CHAR = re.compile(r"^[^0-9A-Za-z\u4e00-\u9fff]$")


def is_effective_line(raw: str) -> bool:
    s = raw.strip()
    if not s:
        return False
    # Remove "format" category characters (includes NBSP, zero-width spaces, etc.)
    # to detect lines that are visually empty / invalid.
    stripped = "".join(ch for ch in s if unicodedata.category(ch) != "Cf")
    if not stripped.strip():
        return False
    if len(stripped) == 1:
        # Single char is only counted if it's alnum or CJK (e.g., "a", "1", "中")
        if _NON_MEANINGFUL_SINGLE_CHAR.match(stripped):
            return False
    return True


def count_lines(*, effective: bool = True) -> int:
    total = 0
    for path in iter_source_files():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if effective:
            total += sum(1 for line in content.splitlines() if is_effective_line(line))
        else:
            total += sum(1 for line in content.splitlines() if line.strip())
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Count source-code lines.")
    ap.add_argument(
        "--mode",
        choices=["effective", "non_empty"],
        default="effective",
        help="effective: exclude blanks + single-char filler/invalid lines; non_empty: exclude blanks only.",
    )
    ns = ap.parse_args()
    print(count_lines(effective=(ns.mode == "effective")))
