# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


EXPECTED_OUTPUTS = [
    "{name}需求规格说明书.md",
    "{name}操作手册.md",
    "{name}操作手册.docx",
    "{name}操作手册.pdf",
    "{name}源代码文档.md",
    "{name}源代码文档.docx",
    "{name}源代码文档.pdf",
    "软件著作权登记申请表.md",
    "软件著作权登记申请表.docx",
]
MIN_SCREENSHOT_COUNT = 8


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def run(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).resolve()
    report: dict[str, object] = {"passed": True, "checks": []}

    for template in EXPECTED_OUTPUTS:
        p = project_dir / template.format(name=args.requirement_name)
        ok = p.exists()
        report["checks"].append({"name": f"exists:{p.name}", "passed": ok, "message": str(p)})
        report["passed"] = report["passed"] and ok

    images_dir = project_dir / "images"
    image_files = sorted(x.name for x in images_dir.glob("*.png")) if images_dir.exists() else []
    images_ok = images_dir.exists() and len(image_files) >= MIN_SCREENSHOT_COUNT
    report["checks"].append(
        {
            "name": "images_dir",
            "passed": images_ok,
            "message": f"count={len(image_files)}, min_required={MIN_SCREENSHOT_COUNT}",
        }
    )
    report["passed"] = report["passed"] and images_ok

    manual_md = project_dir / f"{args.requirement_name}操作手册.md"
    if manual_md.exists():
        t = manual_md.read_text(encoding="utf-8", errors="ignore")
        refs = set(re.findall(r"!\[[^\]]*\]\(images/([^)]+)\)", t))
        missing_refs = sorted(x for x in refs if not (images_dir / x).exists())
        ok = len(refs) >= MIN_SCREENSHOT_COUNT and not missing_refs
        report["checks"].append(
            {
                "name": "manual_image_refs",
                "passed": ok,
                "message": f"refs={len(refs)}, min_required={MIN_SCREENSHOT_COUNT}, missing={missing_refs}",
            }
        )
        report["passed"] = report["passed"] and ok

    pipeline_report = project_dir / "pipeline_report.latest.json"
    if pipeline_report.exists():
        data = read_json(pipeline_report)
        stages = [x for x in data if isinstance(x, dict) and "stage" in x]
        failed = [x.get("stage") for x in stages if not x.get("passed", False)]
        ok = not failed
        report["checks"].append({"name": "pipeline_report", "passed": ok, "message": "ok" if ok else f"failed={failed}"})
        report["passed"] = report["passed"] and ok

    out = Path(args.report_json).resolve() if args.report_json else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Reusable postflight baseline checks")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--requirement-name", required=True)
    parser.add_argument("--report-json", default="")
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
