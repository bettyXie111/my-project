from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


REQUIRED_PRD_HEADINGS = [
    "## 2. 行业背景与问题定义",
    "## 3. 产品目标与成功指标",
    "## 4. 用户角色与权限边界",
    "## 6. 核心业务流程",
    "## 7. 功能需求",
    "## 8. 数据模型",
    "## 9. 接口约束",
    "## 11. 视觉风格关键词",
    "## 14. 验收标准",
]


@dataclass
class StageResult:
    stage: str
    passed: bool
    message: str
    command: str = ""
    command_exit_code: int | None = None
    retries: int = 0


def count_visible_chars(text: str) -> int:
    return len("".join(text.split()))


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


def validate_stage_0(project_dir: Path) -> StageResult:
    if not project_dir.exists() or not project_dir.is_dir():
        return StageResult("0_isolation", False, f"project dir missing: {project_dir}")
    return StageResult("0_isolation", True, "project dir exists")


def validate_stage_1(project_dir: Path, req_name: str, min_prd_chars: int) -> StageResult:
    prd_path = project_dir / f"{req_name}需求规格说明书.md"
    if not prd_path.exists():
        return StageResult("1_prd", False, f"PRD missing: {prd_path}")
    content = prd_path.read_text(encoding="utf-8")
    missing = [h for h in REQUIRED_PRD_HEADINGS if h not in content]
    if missing:
        return StageResult("1_prd", False, f"PRD missing headings: {', '.join(missing)}")
    chars = count_visible_chars(content)
    if chars < min_prd_chars:
        return StageResult("1_prd", False, f"PRD too short: {chars} < {min_prd_chars}")
    return StageResult("1_prd", True, f"PRD validated, chars={chars}")


def validate_stage_2(project_dir: Path) -> StageResult:
    required_files = [
        project_dir / "apps" / "api" / "main.py",
        project_dir / "apps" / "web" / "index.html",
    ]
    missing = [str(p) for p in required_files if not p.exists()]
    if missing:
        return StageResult("2_web", False, f"web skeleton missing: {', '.join(missing)}")
    return StageResult("2_web", True, "web skeleton exists")


def validate_stage_3(project_dir: Path) -> StageResult:
    checklog = project_dir / "checklog.md"
    if not checklog.exists():
        return StageResult("3_slop", False, "checklog.md missing")
    text = checklog.read_text(encoding="utf-8")
    if "slop" not in text.lower() and "AI" not in text:
        return StageResult("3_slop", False, "no slop/audit evidence found in checklog")
    return StageResult("3_slop", True, "slop audit evidence found")


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
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        return StageResult("4_copyright", False, f"deliverables missing: {', '.join(missing)}")
    return StageResult("4_copyright", True, "deliverables complete")


def execute_stage_with_gate(
    stage_name: str,
    validator: Callable[[], StageResult],
    command: str | None,
    cwd: Path,
    retries: int,
) -> StageResult:
    first = validator()
    if not first.passed:
        return first
    if not command:
        return first
    attempt = 0
    last_output = ""
    while attempt <= retries:
        code, out = run_command(command, cwd)
        if code == 0:
            result = validator()
            result.command = command
            result.command_exit_code = 0
            result.retries = attempt
            if not result.passed:
                result.message = f"command ok but gate failed: {result.message}"
            return result
        last_output = out
        attempt += 1
    failed = StageResult(stage_name, False, f"command failed after retries: {last_output[:400]}")
    failed.command = command
    failed.command_exit_code = 1
    failed.retries = retries
    return failed


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
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    report: list[StageResult] = []

    gates = [
        ("0_isolation", lambda: validate_stage_0(project_dir), None),
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

    if args.report_json:
        out_path = Path(args.report_json).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps([r.__dict__ for r in report], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    all_pass = len(report) == len(gates) and all(r.passed for r in report)
    return 0 if all_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
