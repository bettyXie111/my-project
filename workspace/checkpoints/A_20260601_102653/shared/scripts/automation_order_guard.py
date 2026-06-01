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

PLACEHOLDER_TOKENS = ["TBD", "TODO", "待补", "占位"]


def count_visible_chars(text: str) -> int:
    return len("".join(text.split()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated PRD before entering coding stage.")
    parser.add_argument("--prd", required=True)
    parser.add_argument("--min-chars", type=int, default=2200)
    args = parser.parse_args()

    prd_path = Path(args.prd).resolve()
    if not prd_path.exists():
        print(f"FAIL: PRD missing: {prd_path}")
        return 2

    content = prd_path.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_PRD_SECTIONS if section not in content]
    if missing:
        print(f"FAIL: missing required sections: {', '.join(missing)}")
        return 2

    visible_chars = count_visible_chars(content)
    if visible_chars < args.min_chars:
        print(f"FAIL: visible chars too short: {visible_chars} < {args.min_chars}")
        return 2

    remains = [token for token in PLACEHOLDER_TOKENS if token in content]
    if remains:
        print(f"FAIL: placeholder text remains: {', '.join(remains)}")
        return 2

    print(f"PASS: PRD validated, visible chars={visible_chars}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
