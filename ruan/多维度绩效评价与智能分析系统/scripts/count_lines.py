"""Count non-empty code lines for the generated project."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_SUFFIXES = {".py", ".js", ".css", ".html", ".sql", ".md", ".json"}


def count_lines() -> int:
  total = 0
  for path in REPO_ROOT.rglob("*"):
    if path.is_dir() or path.suffix.lower() not in TARGET_SUFFIXES:
      continue
    try:
      content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
      continue
    total += sum(1 for line in content.splitlines() if line.strip())
  return total


if __name__ == "__main__":
  print(count_lines())
