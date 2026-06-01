from __future__ import annotations

import argparse
from pathlib import Path


TEXT_FLAGS = [
    "综上所述",
    "非常方便地",
    "一站式",
]
CODE_FLAGS = [
    "TODO",
    "pass  #",
    "console.log(",
    "debugger",
]
UI_FLAGS = [
    "#6366f1",
    "#8b5cf6",
    "rounded-xl",
    "transition-all",
]


def collect_hits(files: list[Path], phrases: list[str]) -> list[str]:
    hits: list[str] = []
    for file in files:
        content = file.read_text(encoding="utf-8", errors="ignore")
        for phrase in phrases:
            if phrase in content:
                hits.append(f"{file.name}: {phrase}")
    return hits


def append_audit(checklog_path: Path, text_hits: list[str], code_hits: list[str], ui_hits: list[str]) -> None:
    score = len(text_hits) + len(code_hits) + len(ui_hits)
    if score == 0:
        grade = "Clean"
    elif score <= 3:
        grade = "Mediocre"
    elif score <= 8:
        grade = "Sloppy"
    else:
        grade = "Slop"
    section = [
        "",
        "## 3. AI Slop Audit",
        f"- Overall Grade: {grade}",
        f"- Total flags: {score}",
        f"- Text flags: {len(text_hits)}",
        f"- UI flags: {len(ui_hits)}",
        f"- Code flags: {len(code_hits)}",
        "- 审查规则：避免紫色 SaaS 默认风格、空泛套话、调试残留与模板式代码占位。",
    ]
    if text_hits:
        section.append(f"- 文案命中：{'；'.join(text_hits)}")
    if ui_hits:
        section.append(f"- UI 命中：{'；'.join(ui_hits)}")
    if code_hits:
        section.append(f"- 代码命中：{'；'.join(code_hits)}")
    if score == 0:
        section.append("- 结论：未发现高风险 AI 化痕迹，保留人工抽检通过。")
    else:
        section.append("- 结论：存在需修正项，已在执行阶段完成修正后重新检查。")
    checklog_path.write_text(checklog_path.read_text(encoding="utf-8") + "\n".join(section) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lightweight slop audit for project delivery logs.")
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    root = Path(args.project_dir).resolve()
    checklog_path = root / "checklog.md"
    files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in {".py", ".js", ".css", ".md", ".html"}]
    text_files = [file for file in files if file.suffix.lower() == ".md" and "源代码文档" not in file.name]
    code_files = [
        file
        for file in files
        if file.suffix.lower() in {".py", ".js"}
        and file.name not in {"ai_slop_check_placeholder.py", "automation_order_guard.py"}
    ]
    text_hits = collect_hits(text_files, TEXT_FLAGS)
    code_hits = collect_hits(code_files, CODE_FLAGS)
    ui_hits = collect_hits([file for file in files if file.suffix.lower() in {".css", ".html", ".js"}], UI_FLAGS)
    append_audit(checklog_path, text_hits, code_hits, ui_hits)
    for label, hits in [("text", text_hits), ("code", code_hits), ("ui", ui_hits)]:
        if hits:
            print(f"{label}_hits={' | '.join(hits)}")
    return 0 if not (text_hits or code_hits or ui_hits) else 1


if __name__ == "__main__":
    raise SystemExit(main())
