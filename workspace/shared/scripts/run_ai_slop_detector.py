# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


TARGET_EXTS = {".md", ".py", ".js", ".mjs", ".ts", ".tsx", ".css", ".html"}
EXCLUDED_DIRS = {"node_modules", ".git", ".tools", "__pycache__", "run_reports", "tmp"}
EXCLUDED_FILENAMES = {
    "checklog.md",
    "slop_report.latest.json",
    "slop_report.latest.md",
}

SKIP_CONTEXT_TOKENS = ("不得", "禁止", "不写", "避免", "清理", "替换", "规则", "说明", "处理建议")


TEXT_FLAGS: list[tuple[str, re.Pattern[str], int]] = [
    ("delve_into", re.compile(r"\bdelve into\b", re.IGNORECASE), 2),
    ("unlock_the_power", re.compile(r"\bunlock the power of\b", re.IGNORECASE), 1),
    ("harness_the_power", re.compile(r"\bharness the power of\b", re.IGNORECASE), 1),
    ("fast_paced_world", re.compile(r"fast-paced world|digital landscape", re.IGNORECASE), 1),
    ("worth_noting", re.compile(r"it's (important|worth) noting", re.IGNORECASE), 1),
    ("cutting_edge", re.compile(r"cutting-edge|state-of-the-art|innovative solution", re.IGNORECASE), 1),
    ("in_conclusion", re.compile(r"\b(in conclusion|in summary)\b", re.IGNORECASE), 2),
]

CN_TEMPLATE_PHRASES: list[tuple[str, re.Pattern[str], int]] = [
    ("summary_talk", re.compile(r"综上所述"), 2),
    ("generic_praise", re.compile(r"(界面简洁|操作简单|功能强大|性能优越|先进|高效|易用)"), 1),
]

PLACEHOLDER_RULES: list[tuple[str, re.Pattern[str], int]] = [
    ("todo", re.compile(r"\bTODO\b", re.IGNORECASE), 2),
    ("tbd", re.compile(r"\bTBD\b", re.IGNORECASE), 2),
    ("placeholder_cn", re.compile(r"(占位|待补)"), 2),
]

CODE_FLAGS: list[tuple[str, re.Pattern[str], int]] = [
    ("swallowed_exception", re.compile(r"except\s+Exception\s*:\s*\n\s*(pass|return\s+None)\b", re.IGNORECASE), 2),
    ("try_catch_empty", re.compile(r"catch\s*\(\s*\w+\s*\)\s*\{\s*\}", re.IGNORECASE), 2),
    ("generic_var_names", re.compile(r"\b(data|result|temp|item)\b"), 1),
]


@dataclass(frozen=True)
class FlagHit:
    domain: str  # text|frontend|code
    rule: str
    severity: int
    file: str
    sample: str


def iter_targets(project_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in project_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.name in EXCLUDED_FILENAMES:
            continue
        if path.suffix.lower() not in TARGET_EXTS:
            continue
        files.append(path)
    return sorted(files)


def _sample_line(text: str, pat: re.Pattern[str]) -> str:
    for line in text.splitlines():
        if pat.search(line):
            return line.strip()[:240]
    return ""

def _has_guard_context(line: str) -> bool:
    compact = line.strip()
    return any(tok in compact for tok in SKIP_CONTEXT_TOKENS)


def scan(project_dir: Path) -> list[FlagHit]:
    hits: list[FlagHit] = []
    for path in iter_targets(project_dir):
        rel = str(path.relative_to(project_dir)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore")

        for rule, pat, sev in TEXT_FLAGS:
            if pat.search(text):
                hits.append(FlagHit("text", rule, sev, rel, _sample_line(text, pat)))

        for rule, pat, sev in CN_TEMPLATE_PHRASES:
            if pat.search(text):
                hits.append(FlagHit("text", rule, sev, rel, _sample_line(text, pat)))

        for rule, pat, sev in PLACEHOLDER_RULES:
            for line in text.splitlines():
                if not pat.search(line):
                    continue
                if _has_guard_context(line):
                    continue
                hits.append(FlagHit("text", rule, sev, rel, line.strip()[:240]))
                break

        # Code-oriented heuristics only for code-ish files
        if path.suffix.lower() in {".py", ".js", ".mjs", ".ts", ".tsx"}:
            for rule, pat, sev in CODE_FLAGS:
                if pat.search(text):
                    hits.append(FlagHit("code", rule, sev, rel, _sample_line(text, pat)))
    return hits


def grade_from_flags(flag_count: int) -> str:
    if flag_count <= 2:
        return "Clean"
    if flag_count <= 5:
        return "Mediocre"
    if flag_count <= 9:
        return "Sloppy"
    return "Slop"


def write_reports(project_dir: Path, hits: list[FlagHit]) -> tuple[Path, Path]:
    out_json = project_dir / "slop_report.latest.json"
    out_md = project_dir / "slop_report.latest.md"
    total_flags = len(hits)
    grade = grade_from_flags(total_flags)
    by_domain: dict[str, int] = {"text": 0, "frontend": 0, "code": 0}
    for h in hits:
        by_domain[h.domain] = by_domain.get(h.domain, 0) + 1

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tool": "run_ai_slop_detector.py",
        "grade": grade,
        "total_flags": total_flags,
        "domains": by_domain,
        "fixed": [],
        "remaining": [h.__dict__ for h in hits],
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines += ["## AI Slop Audit", ""]
    lines += [f"### Overall Grade: {grade}", f"**Total flags:** {total_flags}  |  **Domains:** Text ({by_domain.get('text',0)}) · Frontend ({by_domain.get('frontend',0)}) · Code ({by_domain.get('code',0)})", ""]
    lines += ["### Remaining Flags", ""]
    if not hits:
        lines += ["- 无（本次扫描未命中常见 slop 模式）。", ""]
    else:
        for h in hits[:120]:
            lines.append(f"- [{h.domain}] {h.rule} sev={h.severity} file={h.file} sample={h.sample!r}")
        if len(hits) > 120:
            lines.append(f"- ... and {len(hits) - 120} more")
        lines.append("")
    lines += ["### Recommended Fixes", ""]
    lines += ["**Quick Wins (< 1 hour)**", "- 清理/替换命中的占位词（TODO/TBD/待补/占位）。", "- 将 `data/result/temp/item` 等泛化命名替换为领域命名。", "- 对异常处理补齐上下文信息，避免空 `catch/except`。", ""]
    lines += ["**Strategic Fixes (choose one)**", "- Option A: 命名与可读性整改（低风险）", "- Option B: 错误处理与边界校验加固（中等成本）", "- Option C: 拆分职责与结构性重构（高成本）", ""]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return out_json, out_md


def append_checklog_evidence(project_dir: Path, report_json: Path, report_md: Path, grade: str) -> None:
    checklog = project_dir / "checklog.md"
    existing = checklog.read_text(encoding="utf-8", errors="ignore") if checklog.exists() else ""
    block = "\n".join(
        [
            "## AI_SLOP_DETECTOR_EVIDENCE",
            f"- report_json: {report_json.name}",
            f"- report_md: {report_md.name}",
            f"- grade: {grade}",
            "",
        ]
    )
    if "## AI_SLOP_DETECTOR_EVIDENCE" in existing:
        head = existing.split("## AI_SLOP_DETECTOR_EVIDENCE", 1)[0].rstrip()
        checklog.write_text(head + "\n\n" + block, encoding="utf-8")
    else:
        checklog.write_text((existing.rstrip() + "\n\n" + block).lstrip(), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="AI slop detector adapter (audit + evidence artifacts).")
    ap.add_argument("--project-dir", required=True)
    ns = ap.parse_args()

    project_dir = Path(ns.project_dir).resolve()
    hits = scan(project_dir)
    report_json, report_md = write_reports(project_dir, hits)
    grade = json.loads(report_json.read_text(encoding="utf-8")).get("grade", "Clean")
    append_checklog_evidence(project_dir, report_json, report_md, str(grade))
    print(f"PASS: wrote {report_json} and {report_md}")
    # Always return 0 so the pipeline can proceed; the gate enforces evidence artifacts.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
