# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Reporting utilities for local project review.

This module focuses on deterministic, explainable summaries that can be used in:
- internal QA before publishing a plan version;
- exporting a "review pack" for stakeholders;
- consistency checks between exported lists and on-screen data.

The functions are intentionally written without external dependencies to keep the
runtime self-contained.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from .errors import BadRequest


def _now() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _as_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    raise BadRequest("expected list")


def _as_dict(value: object) -> dict:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    raise BadRequest("expected object")


def _norm_text(s: object) -> str:
    return ("" if s is None else str(s)).strip()


def _safe_float(v: object, *, default: float = 0.0) -> float:
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip())
    except Exception:
        return default


def _safe_int(v: object, *, default: int = 0) -> int:
    if v is None:
        return default
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (int, float)):
        return int(v)
    try:
        return int(float(str(v).strip()))
    except Exception:
        return default


def _pct(part: int, total: int) -> str:
    if total <= 0:
        return "0%"
    return f"{round(part * 100.0 / total)}%"


@dataclass(frozen=True)
class Kpi:
    sites: int
    plans: int
    versions: int
    plants: int
    materials: int
    lights: int
    issues: int
    pavings: int

    def to_dict(self) -> dict[str, int]:
        return {
            "sites": self.sites,
            "plans": self.plans,
            "versions": self.versions,
            "plants": self.plants,
            "materials": self.materials,
            "lights": self.lights,
            "issues": self.issues,
            "pavings": self.pavings,
        }


def compute_kpi(state: dict[str, Any]) -> Kpi:
    return Kpi(
        sites=len(_as_list(state.get("sites"))),
        plans=len(_as_list(state.get("plans"))),
        versions=len(_as_list(state.get("versions"))),
        plants=len(_as_list(state.get("plants"))),
        materials=len(_as_list(state.get("materials"))),
        lights=len(_as_list(state.get("lights"))),
        issues=len(_as_list(state.get("issues"))),
        pavings=len(_as_list(state.get("pavings"))),
    )


def group_by(items: Iterable[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for it in items:
        k = _norm_text(it.get(key))
        out.setdefault(k, []).append(it)
    return out


def summarize_plants(plants: list[dict[str, Any]]) -> dict[str, Any]:
    by_category = group_by(plants, "category")
    evergreen_count = 0
    for p in plants:
        if bool(p.get("evergreen")):
            evergreen_count += 1
    summary = {
        "total": len(plants),
        "evergreen": evergreen_count,
        "deciduous": len(plants) - evergreen_count,
        "evergreenRatio": _pct(evergreen_count, len(plants)),
        "byCategory": {k or "(未分类)": len(v) for k, v in sorted(by_category.items(), key=lambda kv: kv[0])},
    }
    crown_ranges = []
    for p in plants:
        mn = _safe_float(p.get("crownMinM"))
        mx = _safe_float(p.get("crownMaxM"))
        if mn > 0 and mx > 0 and mx >= mn:
            crown_ranges.append((mn, mx))
    if crown_ranges:
        summary["crownMinMin"] = min(mn for mn, _ in crown_ranges)
        summary["crownMaxMax"] = max(mx for _, mx in crown_ranges)
    return summary


def summarize_materials(materials: list[dict[str, Any]]) -> dict[str, Any]:
    by_unit = group_by(materials, "unit")
    return {
        "total": len(materials),
        "byUnit": {k or "(未定义单位)": len(v) for k, v in sorted(by_unit.items(), key=lambda kv: kv[0])},
    }


def summarize_lights(lights: list[dict[str, Any]]) -> dict[str, Any]:
    total_qty = sum(_safe_int(l.get("qty")) for l in lights)
    by_cct = group_by(lights, "cct")
    return {
        "total": len(lights),
        "totalQty": total_qty,
        "byCct": {k or "(未定义色温)": len(v) for k, v in sorted(by_cct.items(), key=lambda kv: kv[0])},
    }


def summarize_issues(issues: list[dict[str, Any]]) -> dict[str, Any]:
    by_status = group_by(issues, "status")
    by_tag = group_by(issues, "tag")
    by_priority = group_by(issues, "priority")
    return {
        "total": len(issues),
        "byStatus": {k or "(未定义状态)": len(v) for k, v in sorted(by_status.items(), key=lambda kv: kv[0])},
        "byTag": {k or "(未定义标签)": len(v) for k, v in sorted(by_tag.items(), key=lambda kv: kv[0])},
        "byPriority": {k or "(未定义优先级)": len(v) for k, v in sorted(by_priority.items(), key=lambda kv: kv[0])},
    }


@dataclass(frozen=True)
class ConsistencyIssue:
    level: str  # info/warn/error
    topic: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"level": self.level, "topic": self.topic, "message": self.message}


def check_code_uniqueness(items: list[dict[str, Any]], *, topic: str) -> list[ConsistencyIssue]:
    seen: set[str] = set()
    issues: list[ConsistencyIssue] = []
    for it in items:
        code = _norm_text(it.get("code")).upper()
        if not code:
            issues.append(ConsistencyIssue("error", topic, "missing code"))
            continue
        if code in seen:
            issues.append(ConsistencyIssue("error", topic, f"duplicate code: {code}"))
            continue
        seen.add(code)
    return issues


def check_issue_flow(issues: list[dict[str, Any]]) -> list[ConsistencyIssue]:
    allowed = {"新建", "处理中", "已解决", "已关闭"}
    out: list[ConsistencyIssue] = []
    for it in issues:
        status = _norm_text(it.get("status"))
        if status and status not in allowed:
            out.append(ConsistencyIssue("warn", "issues", f"unknown status: {status}"))
    return out


def check_theme_keywords(plans: list[dict[str, Any]]) -> list[ConsistencyIssue]:
    out: list[ConsistencyIssue] = []
    for p in plans:
        theme = _norm_text(p.get("theme"))
        if not theme:
            out.append(ConsistencyIssue("warn", "plans", "theme is empty"))
        elif len(theme) > 20:
            out.append(ConsistencyIssue("info", "plans", "theme text is long; consider shorter label"))
    return out


def run_consistency_checks(state: dict[str, Any]) -> list[ConsistencyIssue]:
    plants = _as_list(state.get("plants"))
    materials = _as_list(state.get("materials"))
    lights = _as_list(state.get("lights"))
    issues = _as_list(state.get("issues"))
    plans = _as_list(state.get("plans"))

    results: list[ConsistencyIssue] = []
    results.extend(check_code_uniqueness(plants, topic="plants"))
    results.extend(check_code_uniqueness(materials, topic="materials"))
    results.extend(check_code_uniqueness(lights, topic="lights"))
    results.extend(check_issue_flow(issues))
    results.extend(check_theme_keywords(plans))
    return results


def build_markdown_report(state: dict[str, Any]) -> str:
    kpi = compute_kpi(state)
    plants = _as_list(state.get("plants"))
    materials = _as_list(state.get("materials"))
    lights = _as_list(state.get("lights"))
    issues = _as_list(state.get("issues"))
    checks = run_consistency_checks(state)

    p_sum = summarize_plants(plants)
    m_sum = summarize_materials(materials)
    l_sum = summarize_lights(lights)
    i_sum = summarize_issues(issues)

    lines: list[str] = []
    lines.append(f"# 项目自检报告")
    lines.append("")
    lines.append(f"- 生成时间：{_now()}")
    lines.append("")
    lines.append("## 1 关键指标")
    lines.append("")
    for k, v in kpi.to_dict().items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 2 植物库概览")
    lines.append("")
    lines.append(f"- 总数：{p_sum['total']}")
    lines.append(f"- 常绿/落叶：{p_sum['evergreen']}/{p_sum['deciduous']}（常绿占比 {p_sum['evergreenRatio']}）")
    if "crownMinMin" in p_sum and "crownMaxMax" in p_sum:
        lines.append(f"- 冠幅范围覆盖：{p_sum['crownMinMin']}m ~ {p_sum['crownMaxMax']}m")
    lines.append("- 类别分布：")
    for k, v in p_sum["byCategory"].items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("## 3 材料字典概览")
    lines.append("")
    lines.append(f"- 总数：{m_sum['total']}")
    lines.append("- 单位分布：")
    for k, v in m_sum["byUnit"].items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("## 4 灯具清单概览")
    lines.append("")
    lines.append(f"- 条目数：{l_sum['total']}")
    lines.append(f"- 数量合计：{l_sum['totalQty']}")
    lines.append("- 色温分布：")
    for k, v in l_sum["byCct"].items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("## 5 评审事项概览")
    lines.append("")
    lines.append(f"- 总数：{i_sum['total']}")
    lines.append("- 状态分布：")
    for k, v in i_sum["byStatus"].items():
        lines.append(f"  - {k}: {v}")
    lines.append("- 标签分布：")
    for k, v in i_sum["byTag"].items():
        lines.append(f"  - {k}: {v}")
    lines.append("- 优先级分布：")
    for k, v in i_sum["byPriority"].items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("## 6 一致性检查")
    lines.append("")
    if not checks:
        lines.append("- 未发现问题。")
    else:
        for it in checks:
            lines.append(f"- [{it.level}] {it.topic}: {it.message}")
    lines.append("")
    lines.append("## 7 建议")
    lines.append("")
    lines.append("- 发布版本前，优先关闭高优先级事项，确保变更摘要覆盖关键对象。")
    lines.append("- 清单导出字段应与施工深化口径一致，必要时补充规格/工艺/等级字段。")
    lines.append("- 对于涉及安全与无障碍的调整，建议在评审事项中明确原因与验收标准。")
    lines.append("")
    return "\n".join(lines) + "\n"

