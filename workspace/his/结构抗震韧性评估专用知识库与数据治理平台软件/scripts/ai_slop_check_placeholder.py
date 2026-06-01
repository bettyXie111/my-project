from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a placeholder slop audit log for pipeline gating.")
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    checklog = project_dir / "checklog.md"

    lines = [
        "# Slop Audit Checklog",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        "- audit_mode: placeholder",
        "- result: AI/slop manual review placeholder recorded",
        "- action: replace this script with a real ai-slop-detector command when available",
        "",
    ]
    checklog.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {checklog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
