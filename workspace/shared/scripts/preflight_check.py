# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_PRD_SECTIONS = [
    "行业背景",
    "用户角色",
    "核心业务流程",
    "数据模型",
    "功能列表",
    "边界约束",
    "验收标准",
    "视觉风格关键词",
]

CODE_DIRS = ("apps", "packages")
CODE_SUFFIXES = {".py", ".js", ".mjs", ".ts", ".tsx", ".css", ".html", ".sql", ".json", ".md"}
EXCLUDED_PARTS = {"__pycache__", "node_modules", ".git", ".tools", "_rollback"}


def count_visible_chars(text: str) -> int:
    return len("".join(text.split()))


def normalize_utf8(path: Path) -> tuple[bool, str]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = path.read_text(encoding="utf-8-sig", errors="strict")
    had_replacement = "\ufffd" in text
    if had_bom:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True, "bom_removed"
    if had_replacement:
        return False, "replacement_char_found"
    return True, "ok"


def scan_text_files(paths: list[Path]) -> list[str]:
    problems: list[str] = []
    for path in paths:
        try:
            _, status = normalize_utf8(path)
            if status == "replacement_char_found":
                problems.append(f"replacement:{path}")
        except UnicodeDecodeError:
            problems.append(f"decode_error:{path}")
        except Exception as exc:
            problems.append(f"error:{path}:{exc}")
    return problems


def collect_targets(project_dir: Path) -> list[Path]:
    targets: list[Path] = []
    for top in CODE_DIRS:
        base = project_dir / top
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            if path.suffix.lower() in CODE_SUFFIXES:
                targets.append(path)
    return targets


def has_code_files(project_dir: Path) -> bool:
    return bool(collect_targets(project_dir))


def validate_prd(prd_path: Path, min_chars: int) -> tuple[bool, str]:
    if not prd_path.exists():
        return False, f"PRD missing: {prd_path}"
    content = prd_path.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_PRD_SECTIONS if section not in content]
    if missing:
        return False, f"PRD missing required sections: {', '.join(missing)}"
    visible_chars = count_visible_chars(content)
    if visible_chars < min_chars:
        return False, f"PRD too short: {visible_chars} < {min_chars}"
    return True, f"PRD ok, chars={visible_chars}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight guard: UTF-8 cleanup + PRD first gate.")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--requirement-name", required=True)
    parser.add_argument("--min-prd-chars", type=int, default=2200)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    prd_path = project_dir / f"{args.requirement_name}需求规格说明书.md"

    targets = [
        project_dir / "automation_prompt.md",
        project_dir / "pipeline_guard.py",
        project_dir / "scripts" / "build_materials.py",
    ]
    manual = next(project_dir.rglob("manual_style_validator.py"), None)
    if manual:
        targets.append(manual)
    skill = Path(r"C:/Users/31556/.codex/skills/custom/chinese-copyright-application/SKILL.md")
    if skill.exists():
        targets.append(skill)

    issues = scan_text_files([p for p in targets if p.exists()])
    if issues:
        print("FAIL: encoding issues found.")
        for issue in issues:
            print(issue)
        return 2

    code_exists = has_code_files(project_dir)
    prd_ok, prd_msg = validate_prd(prd_path, args.min_prd_chars)
    if code_exists and not prd_ok:
        print(f"FAIL: coding-first violation. code exists but PRD invalid. {prd_msg}")
        return 2

    print(f"PASS: preflight ok. code_exists={code_exists}. {prd_msg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
