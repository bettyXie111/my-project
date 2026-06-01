from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


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

LAYOUT_RULE_KEYWORDS = [
    "不得在 pipeline_guard.py 内实现",
    "不得在 automation_prompt.md 内重复维护",
]

SENSITIVE_KEYWORDS = [
    "截图脚本",
    "占位",
    "TODO",
]


@dataclass
class StageResult:
    stage: str
    passed: bool
    message: str
    command: str = ""
    command_exit_code: int | None = None
    retries: int = 0


def _shorten(text: str, limit: int = 240) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def count_visible_chars(text: str) -> int:
    return len("".join(text.split()))


def path_within_root(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def run_command(command: str, cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip()


def run_baseline_hook(command: str, cwd: Path, stage_name: str) -> StageResult:
    code, out = run_command(command, cwd)
    if code == 0:
        return StageResult(stage_name, True, "baseline passed", command=command, command_exit_code=0)
    return StageResult(
        stage_name,
        False,
        f"baseline failed: {(out or f'exit code {code}')[:400]}",
        command=command,
        command_exit_code=code,
    )


def validate_stage_0(project_dir: Path, workspace_dir: Path) -> StageResult:
    if not path_within_root(workspace_dir, project_dir):
        return StageResult("0_isolation", False, f"project dir must stay under workspace root: {project_dir}")
    if not project_dir.exists() or not project_dir.is_dir():
        return StageResult("0_isolation", False, f"project dir missing: {project_dir}")
    return StageResult("0_isolation", True, "project dir exists")


def validate_stage_1(project_dir: Path, req_name: str, min_prd_chars: int) -> StageResult:
    prd_path = project_dir / f"{req_name}需求规格说明书.md"
    if not prd_path.exists():
        return StageResult("1_prd", False, f"PRD missing: {prd_path}")
    content = prd_path.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_PRD_SECTIONS if section not in content]
    if missing:
        return StageResult("1_prd", False, f"PRD missing required sections: {', '.join(missing)}")
    chars = count_visible_chars(content)
    if chars < min_prd_chars:
        return StageResult("1_prd", False, f"PRD too short: {chars} < {min_prd_chars}")
    return StageResult("1_prd", True, f"PRD validated, chars={chars}")


def validate_stage_2(project_dir: Path) -> StageResult:
    required_files = [
        project_dir / "apps" / "api" / "main.py",
        project_dir / "apps" / "web" / "index.html",
        project_dir / "apps" / "web" / "admin.html",
        project_dir / "apps" / "api" / "routers" / "samples.py",
        project_dir / "apps" / "api" / "schemas" / "sample.py",
    ]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        return StageResult("2_web", False, f"web skeleton missing: {', '.join(missing)}")
    keyword_fail = find_sensitive_keywords(
        files=[project_dir / "apps" / "web" / "index.html", project_dir / "apps" / "web" / "admin.html"],
        keywords=SENSITIVE_KEYWORDS,
    )
    if keyword_fail:
        return StageResult("2_web", False, f"sensitive keywords found in web files: {keyword_fail}")
    return StageResult("2_web", True, "web skeleton exists")


def validate_stage_3(project_dir: Path) -> StageResult:
    report_json = project_dir / "slop_report.latest.json"
    if not report_json.exists():
        return StageResult("3_slop", False, "slop_report.latest.json missing")
    try:
        data = json.loads(report_json.read_text(encoding="utf-8"))
    except Exception:
        return StageResult("3_slop", False, "slop_report.latest.json unreadable")
    if not isinstance(data, dict):
        return StageResult("3_slop", False, "slop_report.latest.json invalid format")
    if "fixed" not in data or "remaining" not in data:
        return StageResult("3_slop", False, "slop_report.latest.json missing fixed/remaining lists")
    remaining = data.get("remaining")
    if not isinstance(remaining, list):
        return StageResult("3_slop", False, "slop_report.latest.json remaining invalid")
    # Hard gate: no medium/high-severity text placeholders should remain.
    high_remaining: list[str] = []
    for item in remaining:
        if not isinstance(item, dict):
            continue
        sev = int(item.get("severity", 0) or 0)
        rule = str(item.get("rule", "") or "")
        if sev >= 2 or rule in {"placeholder_cn"}:
            high_remaining.append(f"{rule}(sev={sev}) file={item.get('file')}")
    if high_remaining:
        return StageResult("3_slop", False, "slop remaining not resolved: " + "; ".join(high_remaining[:6]))
    checklog = project_dir / "checklog.md"
    if not checklog.exists():
        return StageResult("3_slop", False, "checklog.md missing")
    text = checklog.read_text(encoding="utf-8", errors="ignore")
    if "AI_SLOP_DETECTOR_EVIDENCE" not in text:
        return StageResult("3_slop", False, "checklog.md missing AI_SLOP_DETECTOR_EVIDENCE section")
    return StageResult("3_slop", True, "slop detector evidence found")


def validate_stage_4(project_dir: Path, req_name: str) -> StageResult:
    required = [
        project_dir / f"{req_name}操作手册.md",
        project_dir / f"{req_name}操作手册.docx",
        project_dir / f"{req_name}操作手册.pdf",
        project_dir / f"{req_name}源代码文档.md",
        project_dir / f"{req_name}源代码文档.docx",
        project_dir / f"{req_name}源代码文档.pdf",
        project_dir / "软件著作权登记申请表.md",
        project_dir / "软件著作权登记申请表.docx",
        project_dir / "images",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        return StageResult("4_copyright", False, f"deliverables missing: {', '.join(missing)}")
    keyword_fail = find_sensitive_keywords(
        files=[
            project_dir / f"{req_name}操作手册.md",
            project_dir / f"{req_name}源代码文档.md",
            project_dir / "软件著作权登记申请表.md",
        ],
        keywords=SENSITIVE_KEYWORDS,
    )
    if keyword_fail:
        return StageResult("4_copyright", False, f"sensitive keywords found in markdown deliverables: {keyword_fail}")
    return StageResult("4_copyright", True, "deliverables complete")


def find_sensitive_keywords(files: list[Path], keywords: list[str]) -> str:
    hits: list[str] = []
    upper_keywords = [k.upper() for k in keywords]
    for path in files:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        upper_text = text.upper()
        for idx, key in enumerate(keywords):
            if upper_keywords[idx] in upper_text:
                rel_name = path.name
                hits.append(f"{rel_name}:{key}")
    return "; ".join(hits[:8])


def validate_prompt_rule_leak(workspace_dir: Path) -> StageResult:
    prompt_path = workspace_dir / "shared" / "docs" / "automation_prompt.md"
    if not prompt_path.exists():
        return StageResult("prompt_static_check", True, "automation_prompt.md not found, skip")
    text = prompt_path.read_text(encoding="utf-8", errors="ignore")
    hits = [kw for kw in LAYOUT_RULE_KEYWORDS if kw in text]
    if hits:
        return StageResult(
            "prompt_static_check",
            False,
            "FAIL: automation_prompt.md contains layout-detail keywords: " + ", ".join(hits),
        )
    return StageResult("prompt_static_check", True, "no layout-rule leakage keywords found")


def build_preflight_command(workspace_dir: Path) -> str:
    scripts_dir = workspace_dir / "shared" / "scripts"
    preflight = scripts_dir / "preflight_check.py"
    py = sys.executable
    return (
        f'"{py}" -X utf8 "{preflight}" '
        "--project-dir . "
        '--requirement-name "{requirement_name}" '
        "--min-prd-chars {min_prd_chars}"
    )


def execute_stage_with_gate(
    stage_name: str,
    validator: Callable[[], StageResult],
    command: str | None,
    cwd: Path,
    retries: int,
) -> StageResult:
    if not command:
        print(f"[{stage_name}] INFO - no command, run gate only")
        return validator()

    attempt = 0
    last_result: StageResult | None = None
    while attempt <= retries:
        print(f"[{stage_name}] START - attempt {attempt + 1}/{retries + 1}")
        print(f"[{stage_name}] CMD - {command}")
        code, out = run_command(command, cwd)
        if code == 0:
            if out:
                print(f"[{stage_name}] OUT - {_shorten(out)}")
            result = validator()
            result.command = command
            result.command_exit_code = 0
            result.retries = attempt
            if result.passed:
                print(f"[{stage_name}] GATE - PASS ({result.message})")
                return result
            print(f"[{stage_name}] GATE - FAIL ({result.message})")
            result.message = f"command ok but gate failed: {result.message}"
            last_result = result
        else:
            if out:
                print(f"[{stage_name}] OUT - {_shorten(out)}")
            last_result = StageResult(
                stage_name,
                False,
                f"command failed: {(out or f'exit code {code}')[:400]}",
                command=command,
                command_exit_code=code,
                retries=attempt,
            )
        attempt += 1

    if last_result is None:
        last_result = validator()
        last_result.command = command or ""
        last_result.retries = retries
    return last_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Serial pipeline gate runner")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--requirement-name", required=True)
    parser.add_argument("--min-prd-chars", type=int, default=2200)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--cmd-stage-1", default="")
    parser.add_argument("--cmd-stage-2", default="")
    parser.add_argument("--cmd-stage-3", default="")
    parser.add_argument("--cmd-stage-4", default="")
    parser.add_argument("--report-json", default="")
    parser.add_argument("--cmd-stage-0-1", default="")
    parser.add_argument("--workspace-dir", default=r"E:\copyRight\workspace")
    parser.add_argument("--auto-normalize-name", action="store_true", help="Auto-normalize requirement name and continue.")
    args = parser.parse_args()
    normalized_name = args.requirement_name.strip().replace("+", "")
    if normalized_name != args.requirement_name:
        if args.auto_normalize_name:
            print(f"[name_guard] WARN - normalized requirement-name: '{args.requirement_name}' -> '{normalized_name}'")
            args.requirement_name = normalized_name
        else:
            print("[name_guard] FAIL - requirement-name invalid. Do not use '+' or leading/trailing spaces.")
            print("            Hint: pass --auto-normalize-name to auto-fix and continue.")
            return 1

    project_dir = Path(args.project_dir).resolve()
    workspace_dir = Path(args.workspace_dir).resolve()
    # Stage-1 in this runner is a gate only. PRD creation must be done by the caller
    # through the requirement directory wrapper (for example, {B}/scripts/generate_prd.py).
    report: list[StageResult] = []
    if not path_within_root(workspace_dir, project_dir):
        result = StageResult("workspace_location", False, f"project dir must stay under workspace root: {project_dir}")
        report.append(result)
        print(f"[{result.stage}] FAIL - {result.message}")
        if args.report_json and path_within_root(workspace_dir, Path(args.report_json).resolve()):
            out_path = Path(args.report_json).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps([entry.__dict__ for entry in report], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return 1
    preflight_baseline_cmd = (
        f'python -X utf8 "{workspace_dir / "preflight_baseline.py"}" '
        f'--workspace-dir "{workspace_dir}" '
        f'--project-dir "{project_dir}" '
        f'--requirement-name "{args.requirement_name}" '
        f'--min-prd-chars {args.min_prd_chars} '
        f'--report-json "{project_dir / "preflight_baseline_report.json"}"'
    )
    postflight_baseline_cmd = (
        f'python -X utf8 "{workspace_dir / "postflight_baseline.py"}" '
        f'--project-dir "{project_dir}" '
        f'--requirement-name "{args.requirement_name}" '
        f'--report-json "{project_dir / "postflight_baseline_report.json"}"'
    )
    soft_copyright_validate_cmd = (
        f'python -X utf8 "{workspace_dir / "shared" / "scripts" / "soft_copyright_validate.py"}" '
        f'--project-root "{workspace_dir}" '
        f'--name "{args.requirement_name}" '
        f'--code-root "{project_dir}" '
        f'--require-docx-pdf'
    )

    preflight_baseline = run_baseline_hook(preflight_baseline_cmd, workspace_dir, "baseline_preflight")
    report.append(preflight_baseline)
    print(f"[{preflight_baseline.stage}] {'PASS' if preflight_baseline.passed else 'FAIL'} - {preflight_baseline.message}")
    if not preflight_baseline.passed:
        if args.report_json:
            out_path = Path(args.report_json).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps([entry.__dict__ for entry in report], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return 1
    preflight_command = args.cmd_stage_0_1 or build_preflight_command(workspace_dir).format(
        requirement_name=args.requirement_name,
        min_prd_chars=args.min_prd_chars,
    )

    gates = [
        ("0_isolation", lambda: validate_stage_0(project_dir, workspace_dir), None),
        ("0_1_preflight", lambda: StageResult("0_1_preflight", True, "preflight command passed"), preflight_command),
        ("1_prd", lambda: validate_stage_1(project_dir, args.requirement_name, args.min_prd_chars), args.cmd_stage_1 or None),
        ("2_web", lambda: validate_stage_2(project_dir), args.cmd_stage_2 or None),
        ("3_slop", lambda: validate_stage_3(project_dir), args.cmd_stage_3 or None),
        ("4_copyright", lambda: validate_stage_4(project_dir, args.requirement_name), args.cmd_stage_4 or None),
    ]

    for stage_name, validator, command in gates:
        result = execute_stage_with_gate(stage_name, validator, command, project_dir, args.retries)
        report.append(result)
        print(f"[{result.stage}] {'PASS' if result.passed else 'FAIL'} - {result.message}")
        if not result.passed:
            break

    static_result = validate_prompt_rule_leak(project_dir.parent)
    report.append(static_result)
    print(f"[{static_result.stage}] {'PASS' if static_result.passed else 'FAIL'} - {static_result.message}")
    if not static_result.passed:
        if args.report_json:
            out_path = Path(args.report_json).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps([entry.__dict__ for entry in report], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return 1

    if args.report_json:
        out_path = Path(args.report_json).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps([entry.__dict__ for entry in report], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    gate_stage_names = {name for name, _, _ in gates}
    gate_results = [entry for entry in report if entry.stage in gate_stage_names]
    all_pass = len(gate_results) == len(gates) and all(entry.passed for entry in gate_results)
    if all_pass:
        postflight_baseline = run_baseline_hook(postflight_baseline_cmd, workspace_dir, "baseline_postflight")
        report.append(postflight_baseline)
        print(f"[{postflight_baseline.stage}] {'PASS' if postflight_baseline.passed else 'FAIL'} - {postflight_baseline.message}")
        if not postflight_baseline.passed:
            if args.report_json:
                out_path = Path(args.report_json).resolve()
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(
                    json.dumps([entry.__dict__ for entry in report], ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            return 1

        soft_copyright_validate = run_baseline_hook(soft_copyright_validate_cmd, workspace_dir, "baseline_soft_copyright")
        report.append(soft_copyright_validate)
        print(f"[{soft_copyright_validate.stage}] {'PASS' if soft_copyright_validate.passed else 'FAIL'} - {soft_copyright_validate.message}")
        if args.report_json:
            out_path = Path(args.report_json).resolve()
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps([entry.__dict__ for entry in report], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return 0 if soft_copyright_validate.passed else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
