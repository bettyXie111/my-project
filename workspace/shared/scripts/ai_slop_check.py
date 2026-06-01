# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from json import JSONDecodeError
from datetime import datetime
from pathlib import Path


TARGET_EXTS = {".py", ".js", ".mjs", ".css", ".html", ".md"}
WEAK_SEQUENCE_PHRASES = ("首先", "其次", "最后")
STRONG_PHRASES = ("综上所述", "可以非常方便地")
TEMPLATE_MARKER_RULES = (
    ("TODO", re.compile(r"\bTODO\b", re.IGNORECASE)),
    ("TBD", re.compile(r"\bTBD\b", re.IGNORECASE)),
    ("待补", re.compile(r"(?:^|[：:>\-\s])待补(?:$|[，。；,\s])")),
    ("占位", re.compile(r"(?:^|[：:>\-\s])(占位|占位符|占位内容|占位文本|占位图片|占位图)(?:$|[，。；,\s])")),
)
MARKER_SKIP_TOKENS = ("不得", "禁止", "不写", "避免", "清理", "替换", "规则", "说明", "处理建议")
EXCLUDED_PARTS = {"__pycache__", "node_modules", ".git", ".tools", "scripts"}


def iter_targets(project_dir: Path) -> list[Path]:
    roots = [project_dir / "apps", project_dir / "packages", project_dir]
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TARGET_EXTS:
                continue
            if any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            if path.name == "checklog.md":
                continue
            if path.parent == project_dir and path.name.endswith("源代码文档.md"):
                continue
            if path.parent == project_dir and path.suffix.lower() == ".md":
                files.append(path)
                continue
            if not any(part in {"apps", "packages"} for part in path.parts):
                continue
            files.append(path)
    uniq: dict[str, Path] = {}
    for path in files:
        uniq[str(path.resolve())] = path
    return sorted(uniq.values(), key=lambda item: str(item))


def line_has_guard_context(line: str) -> bool:
    compact = line.strip()
    return any(token in compact for token in MARKER_SKIP_TOKENS)


def scan_files(files: list[Path]) -> tuple[list[str], list[str]]:
    phrase_hits: list[str] = []
    marker_hits: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.name

        weak_hits = [phrase for phrase in WEAK_SEQUENCE_PHRASES if phrase in text]
        if len(weak_hits) >= 2:
            phrase_hits.extend(f"{rel}: {phrase}" for phrase in weak_hits)

        for phrase in STRONG_PHRASES:
            if phrase in text:
                phrase_hits.append(f"{rel}: {phrase}")

        for label, pattern in TEMPLATE_MARKER_RULES:
            for line in text.splitlines():
                if not pattern.search(line):
                    continue
                if line_has_guard_context(line):
                    continue
                marker_hits.append(f"{rel}: {label}")
                break
    return phrase_hits, marker_hits


def load_notes(project_dir: Path) -> dict[str, object]:
    notes_path = project_dir / "execution_notes.json"
    if not notes_path.exists():
        return {}
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            return json.loads(notes_path.read_text(encoding=encoding))
        except (UnicodeDecodeError, JSONDecodeError):
            continue
    return {}


def render_notes_checklog(project_dir: Path, notes: dict[str, object], phrase_hits: list[str], marker_hits: list[str]) -> Path:
    checklog = project_dir / "checklog.md"
    risk = "LOW"
    if marker_hits:
        risk = "HIGH"
    elif phrase_hits:
        risk = "MEDIUM"

    lines = [
        "# 执行与去AI化检查日志",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- audit_mode: custom_ai_slop_check_with_execution_notes",
        "- scope: apps/*, packages/*, project markdown files",
        f"- risk_level: {risk}",
        "",
        "## 人工介入记录",
    ]

    interventions = [item for item in notes.get("manual_interventions", []) if isinstance(item, dict)]
    if interventions:
        for item in interventions:
            code = item.get("code") or item.get("id") or "MI-UNKNOWN"
            title = item.get("title", "")
            lines.extend(
                [
                    f"### {code} {title}".rstrip(),
                    f"- stage: {item.get('stage', '')}",
                    f"- reason: {item.get('reason', '')}",
                    "- options:",
                ]
            )
            for option in item.get("options", []):
                lines.append(f"  - {option}")
            lines.append(f"- selected: {item.get('selected', '')}")
            lines.append(f"- selected_by: {item.get('selected_by', '')}")
            lines.append("")
    else:
        lines.append("- 无。")
        lines.append("")

    lines.append("## 阻塞点记录")
    blockers = notes.get("blockers")
    if blockers is None:
        blockers = notes.get("blocking_points", [])
    blockers = [item for item in blockers if isinstance(item, dict)]
    if blockers:
        for item in blockers:
            code = item.get("code") or item.get("id") or "BP-UNKNOWN"
            title = item.get("title", "")
            lines.extend(
                [
                    f"### {code} {title}".rstrip(),
                    f"- stage: {item.get('stage', '')}",
                    f"- reason: {item.get('reason', '')}",
                    f"- status: {item.get('status', '')}",
                    "",
                ]
            )
    else:
        lines.append("- 无。")
        lines.append("")

    lines.append("## AI Slop 审查结果")
    if not phrase_hits and not marker_hits:
        lines.append("- 未发现高频 AI 套话和模板化占位词，阶段 3 可以判定通过。")
    else:
        for hit in phrase_hits:
            lines.append(f"- phrase_hit: {hit}")
        for hit in marker_hits:
            lines.append(f"- marker_hit: {hit}")
        lines.append("- 处理建议：替换套话并清理占位词后重跑阶段 3。")
    lines.append("")

    lines.append("## 差异化设计摘要")
    design_summary = notes.get("design_summary", [])
    if design_summary:
        for item in design_summary:
            lines.append(f"- {item}")
    else:
        lines.append("- 无。")

    checklog.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checklog


def render_simple_checklog(project_dir: Path, phrase_hits: list[str], marker_hits: list[str]) -> Path:
    checklog = project_dir / "checklog.md"
    risk = "LOW"
    if marker_hits:
        risk = "HIGH"
    elif phrase_hits:
        risk = "MEDIUM"

    lines = [
        "# AI Slop 审查记录",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- audit_mode: automated_ai_slop_check",
        "- scope: apps/*, packages/*, project markdown files",
        f"- risk_level: {risk}",
        "",
        "## 审查结果",
    ]
    if not phrase_hits and not marker_hits:
        lines.append("- 未发现模板化占位词与高频 AI 套话，阶段 3 可判定通过。")
    else:
        lines.append("- 发现风险项，已记录如下：")
        for hit in phrase_hits:
            lines.append(f"- phrase_hit: {hit}")
        for hit in marker_hits:
            lines.append(f"- marker_hit: {hit}")
        lines.append("- 处理建议：替换套话、清理占位词后重跑阶段 3。")

    checklog.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checklog


def render_simple_checklog_text(phrase_hits: list[str], marker_hits: list[str]) -> str:
    risk = "LOW"
    if marker_hits:
        risk = "HIGH"
    elif phrase_hits:
        risk = "MEDIUM"

    lines = [
        "# AI Slop 审查记录",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- audit_mode: automated_ai_slop_check",
        "- scope: apps/*, packages/*, project markdown files",
        f"- risk_level: {risk}",
        "",
        "## 审查结果",
    ]
    if not phrase_hits and not marker_hits:
        lines.append("- 未发现模板化占位词与高频 AI 套话，阶段 3 可判定通过。")
    else:
        lines.append("- 发现风险项，已记录如下：")
        for hit in phrase_hits:
            lines.append(f"- phrase_hit: {hit}")
        for hit in marker_hits:
            lines.append(f"- marker_hit: {hit}")
        lines.append("- 处理建议：替换套话、清理占位词后重跑阶段 3。")
    return "\n".join(lines) + "\n"


def write_checklog(project_dir: Path, phrase_hits: list[str], marker_hits: list[str]) -> Path:
    notes = load_notes(project_dir)
    if notes:
        return render_notes_checklog(project_dir, notes, phrase_hits, marker_hits)
    # Preserve existing execution checklog content if present, and append/refresh slop section.
    checklog = project_dir / "checklog.md"
    existing = checklog.read_text(encoding="utf-8", errors="ignore") if checklog.exists() else ""
    slop_text = render_simple_checklog_text(phrase_hits, marker_hits).strip()
    if not existing:
        checklog.write_text(slop_text + "\n", encoding="utf-8")
        return checklog
    # If the checklog is already a pure slop report, replace it.
    if existing.lstrip().startswith("# AI Slop 审查记录"):
        checklog.write_text(slop_text + "\n", encoding="utf-8")
        return checklog
    # Otherwise, append slop report as a section at the end, replacing any previous appended slop block.
    start_mark = "\n## AI_SLOP_REPORT\n"
    if start_mark in existing:
        existing = existing.split(start_mark, 1)[0].rstrip() + "\n"
    merged = existing.rstrip() + start_mark + slop_text + "\n"
    checklog.write_text(merged, encoding="utf-8")
    return checklog


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ai-slop checks and write checklog.md")
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    files = iter_targets(project_dir)
    phrase_hits, marker_hits = scan_files(files)
    checklog = write_checklog(project_dir, phrase_hits, marker_hits)
    print(f"Wrote {checklog}")
    return 2 if marker_hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
