from __future__ import annotations

import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / f"{ROOT.name}源代码文档.md"
SOURCE_ROOTS = [ROOT / "apps", ROOT / "packages", ROOT / "scripts"]
TARGET_SUFFIXES = {".py", ".js", ".mjs", ".css", ".html", ".json"}
MAX_LINES = 3000
# Keep a conservative width to prevent Word auto-wrap in 10pt monospace
# under normal margins, otherwise visible rows per page can drop below 50.
MAX_TOTAL_DISPLAY_WIDTH = 52
MAX_CONTENT_DISPLAY_WIDTH = MAX_TOTAL_DISPLAY_WIDTH
MIN_SPLIT_DISPLAY_WIDTH = 24
BREAK_AFTER_CHARS = set(",锛屻€傦紱;:锛?]}>+-*/=&|")
ENTRY_HINTS = (
    "main.",
    "app.",
    "index.",
    "server.",
    "wsgi.",
    "asgi.",
    "__main__.",
)
ROUTE_HINTS = ("router", "route", "routes", "page", "pages", "view", "views", "controller")
CONFIG_HINTS = ("config", "settings", "env", "utils", "tool", "tools", "const", "constants")


def iter_source_files() -> list[Path]:
    items: list[Path] = []
    for base in SOURCE_ROOTS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_dir() or path.suffix.lower() not in TARGET_SUFFIXES:
                continue
            if "__pycache__" in path.parts or "node_modules" in path.parts:
                continue
            items.append(path)
    return items


def classify_path(path: Path) -> tuple[int, str]:
    rel = path.relative_to(ROOT).as_posix().lower()
    name = path.name.lower()
    stem = path.stem.lower()
    if name.startswith(ENTRY_HINTS) or stem in {"main", "app", "index", "server", "__main__"}:
        return (0, rel)
    if any(part in ROUTE_HINTS for part in path.parts) or any(h in stem for h in ROUTE_HINTS):
        return (1, rel)
    if any(part in CONFIG_HINTS for part in path.parts) or any(h in stem for h in CONFIG_HINTS):
        return (3, rel)
    return (2, rel)


def char_display_width(char: str) -> int:
    if char == "\t":
        return 4
    return 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1


def text_display_width(text: str) -> int:
    return sum(char_display_width(char) for char in text)


def visible_prefix_by_width(text: str, max_width: int) -> str:
    total = 0
    end = 0
    for index, char in enumerate(text):
        char_width = char_display_width(char)
        if total + char_width > max_width:
            break
        total += char_width
        end = index + 1
    return text[:end]


def find_split_index(window: str) -> int:
    punctuation_index = -1
    whitespace_index = -1
    for index, char in enumerate(window):
        prefix_width = text_display_width(window[: index + 1])
        if prefix_width < MIN_SPLIT_DISPLAY_WIDTH:
            continue
        if char in BREAK_AFTER_CHARS:
            punctuation_index = index + 1
        elif char.isspace():
            whitespace_index = index
    if punctuation_index > 0:
        return punctuation_index
    if whitespace_index > 0:
        return whitespace_index
    return len(window)


def split_long_line(line: str) -> list[str]:
    stripped = line.rstrip("\n").replace("\t", "    ")
    if not stripped:
        return []
    remaining = stripped
    chunks: list[str] = []
    while text_display_width(remaining) > MAX_CONTENT_DISPLAY_WIDTH:
        window = visible_prefix_by_width(remaining, MAX_CONTENT_DISPLAY_WIDTH)
        split_at = find_split_index(window)
        chunk = remaining[:split_at].rstrip()
        if not chunk:
            chunk = window
            split_at = len(window)
        chunks.append(chunk)
        remaining = remaining[split_at:].lstrip()
    chunks.append(remaining)
    return chunks


def validate_line_widths(lines: list[str]) -> None:
    violations = [(index, text_display_width(line), line) for index, line in enumerate(lines, start=1) if text_display_width(line) > MAX_TOTAL_DISPLAY_WIDTH]
    if violations:
        sample = "\n".join(f"{index}: width={width} {line[:160]}" for index, width, line in violations[:5])
        raise ValueError(f"Source document lines exceed max display width {MAX_TOTAL_DISPLAY_WIDTH}.\n{sample}")


def collect_source_lines() -> list[str]:
    stream: list[str] = []
    ordered_files = sorted(iter_source_files(), key=classify_path)
    for path in ordered_files:
        relative = path.relative_to(ROOT).as_posix()
        stream.append(f"[{relative}]")
        for source_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not source_line.strip():
                continue
            for chunk in split_long_line(source_line):
                stream.append(chunk)

    if not stream:
        raise RuntimeError("No source files found for source-code document generation.")

    if len(stream) > MAX_LINES:
        head = stream[: MAX_LINES // 2]
        tail = stream[-(MAX_LINES // 2) :]
        return head + tail
    if len(stream) < MAX_LINES:
        stream.extend(["[padding]"] * (MAX_LINES - len(stream)))
    return stream


def main() -> None:
    lines = collect_source_lines()[:MAX_LINES]
    validate_line_widths(lines)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"output={OUTPUT}")
    print(f"line_count={len(lines)}")
    print("page_count=60")
    print("page_size=50")


if __name__ == "__main__":
    main()

