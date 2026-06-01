from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_HEADINGS = [
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
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in content]
    if missing:
        print(f"FAIL: missing headings: {', '.join(missing)}")
        return 2
    visible_chars = count_visible_chars(content)
    if visible_chars < args.min_chars:
        print(f"FAIL: visible chars too short: {visible_chars} < {args.min_chars}")
        return 2
    placeholders = ["TBD", "待补", "占位", "TODO"]
    remains = [token for token in placeholders if token in content]
    if remains:
        print(f"FAIL: placeholder text remains: {', '.join(remains)}")
        return 2
    print(f"PASS: PRD validated, visible chars={visible_chars}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

