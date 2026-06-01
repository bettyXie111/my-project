# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LAYOUT_KEYWORDS = ["不得在 pipeline_guard.py 内实现", "不得在 automation_prompt.md 内重复维护"]
REQUIRED_PRD_SECTIONS = ["行业背景", "用户角色", "核心业务流程", "数据模型", "功能列表", "边界约束", "验收标准", "视觉风格关键词"]
TARGET_SUFFIXES = {".py", ".js", ".mjs", ".css", ".html", ".json", ".md"}
EXCLUDED_PARTS = {"__pycache__", "node_modules", ".git", ".tools", "_rollback"}


def visible_chars(text: str) -> int:
    return len("".join(text.split()))


def path_within_root(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def utf8_health(path: Path) -> tuple[bool, str]:
    try:
        raw = path.read_bytes()
        had_bom = raw.startswith(b"\xef\xbb\xbf")
        text = path.read_text(encoding="utf-8-sig", errors="strict")
        if "\ufffd" in text:
            return False, "replacement_char_found"
        if had_bom:
            path.write_text(text, encoding="utf-8", newline="\n")
            return True, "bom_removed"
        return True, "ok"
    except UnicodeDecodeError:
        return False, "decode_error"
    except Exception as exc:
        return False, f"error:{exc}"


def scan_code_files(project_dir: Path) -> list[Path]:
    files: list[Path] = []
    for root_name in ("apps", "packages", "scripts"):
        root = project_dir / root_name
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in TARGET_SUFFIXES:
                continue
            if any(part in EXCLUDED_PARTS for part in p.parts):
                continue
            files.append(p)
    return files


def run(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    workspace_dir = Path(args.workspace_dir).resolve()
    report: dict[str, object] = {"passed": True, "checks": []}

    within_workspace = path_within_root(workspace_dir, project_dir)
    if not within_workspace:
        report["passed"] = False
        report["checks"].append({"name": "project_dir_location", "passed": False, "message": f"must stay under workspace root: {project_dir}"})
    elif not project_dir.exists():
        report["passed"] = False
        report["checks"].append({"name": "project_dir", "passed": False, "message": f"missing: {project_dir}"})
    else:
        report["checks"].append({"name": "project_dir", "passed": True, "message": str(project_dir)})

    prompt = workspace_dir / "automation_prompt.md"
    if prompt.exists():
        text = prompt.read_text(encoding="utf-8", errors="ignore")
        hits = [k for k in LAYOUT_KEYWORDS if k in text]
        ok = not hits
        report["checks"].append({"name": "prompt_rule_leak", "passed": ok, "message": "ok" if ok else f"keywords: {hits}"})
        report["passed"] = report["passed"] and ok

    prd = project_dir / f"{args.requirement_name}需求规格说明书.md"
    # NOTE: preflight baseline should not block the pipeline before PRD/code generation stages run.
    # PRD validity and code existence are enforced by later pipeline gates.
    if prd.exists():
        t = prd.read_text(encoding="utf-8", errors="ignore")
        missing = [s for s in REQUIRED_PRD_SECTIONS if s not in t]
        chars = visible_chars(t)
        ok = not missing and chars >= args.min_prd_chars
        msg = f"chars={chars}, missing={missing}" if not ok else f"chars={chars}"
        report["checks"].append({"name": "prd_optional", "passed": ok, "message": msg})
    else:
        report["checks"].append({"name": "prd_optional", "passed": True, "message": "missing (allowed before stage-1)"})

    targets = [prompt, workspace_dir / "pipeline_guard.py", workspace_dir / "scripts" / "build_materials.py", workspace_dir / "scripts" / "manual_style_validator.py"]
    for p in targets:
        if not p.exists():
            continue
        ok, msg = utf8_health(p)
        report["checks"].append({"name": f"utf8:{p.name}", "passed": ok, "message": msg})
        report["passed"] = report["passed"] and ok

    code_files = scan_code_files(project_dir)
    has_any = bool(code_files)
    report["checks"].append(
        {"name": "code_files_optional", "passed": True, "message": f"count={len(code_files)} (allowed before stage-2)"}
    )
    report["checks"].append({"name": "code_files_present", "passed": has_any, "message": f"count={len(code_files)}"})

    out = Path(args.report_json).resolve() if args.report_json else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Reusable preflight baseline checks")
    parser.add_argument("--workspace-dir", default=r"E:\copyRight\workspace")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--requirement-name", required=True)
    parser.add_argument("--min-prd-chars", type=int, default=2200)
    parser.add_argument("--report-json", default="")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
