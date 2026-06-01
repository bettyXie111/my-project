"""Performance master data endpoints."""

from __future__ import annotations

from typing import Any

from ..core.exceptions import ConflictError
from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    audit_log,
    build_list_sql,
    ensure_unique_code,
    generate_id,
    normalize_master_item,
    page_from_sql,
    require_fields,
    require_permission,
)
from .constants import STATUS_ACTIVE


def _list_indicators(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    sql, params = build_list_sql(
        "performance_indicators",
        keyword_columns=["code", "name", "dimension"],
        extra_filters={"dimension": "dimension", "status": "status"},
        query=context.query,
    )
    return page_from_sql(
        context.db,
        sql=sql,
        params=params,
        query=context.query,
        request_id=context.request_id,
        item_transform=normalize_master_item,
    )


def _create_indicator(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(context.body, "code", "name", "dimension", "weight", "scoringRule")
    ensure_unique_code(context.db, "performance_indicators", context.body["code"])
    now = iso_now()
    indicator_id = generate_id("kpi")
    context.db.execute(
        """
        INSERT INTO performance_indicators(
            id, code, name, dimension, weight, scoring_rule, owner_org_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            indicator_id,
            context.body["code"],
            context.body["name"],
            context.body["dimension"],
            float(context.body["weight"]),
            context.body["scoringRule"],
            context.body.get("ownerOrgId"),
            context.body.get("status", STATUS_ACTIVE),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PERFORMANCE_INDICATOR_CREATED",
        biz_type="PERFORMANCE_INDICATOR",
        biz_id=indicator_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"indicatorId": indicator_id}, context.request_id, status_code=201)


def _list_cycles(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    sql, params = build_list_sql(
        "performance_cycles",
        keyword_columns=["cycle_code", "cycle_name", "period_type"],
        extra_filters={"status": "status"},
        query=context.query,
    )
    return page_from_sql(
        context.db,
        sql=sql,
        params=params,
        query=context.query,
        request_id=context.request_id,
        item_transform=normalize_master_item,
    )


def _create_cycle(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(
        context.body,
        "cycleCode",
        "cycleName",
        "periodType",
        "startDate",
        "endDate",
        "selfReviewDeadline",
        "managerReviewDeadline",
    )
    existing_cycle = context.db.execute(
        "SELECT id FROM performance_cycles WHERE cycle_code = ?",
        (context.body["cycleCode"],),
    ).fetchone()
    if existing_cycle is not None:
        raise ConflictError("绩效周期编码已存在", code="REQ_409_01")
    now = iso_now()
    cycle_id = generate_id("cycle")
    context.db.execute(
        """
        INSERT INTO performance_cycles(
            id, cycle_code, cycle_name, period_type, start_date, end_date,
            self_review_deadline, manager_review_deadline, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            cycle_id,
            context.body["cycleCode"],
            context.body["cycleName"],
            context.body["periodType"],
            context.body["startDate"],
            context.body["endDate"],
            context.body["selfReviewDeadline"],
            context.body["managerReviewDeadline"],
            context.body.get("status", STATUS_ACTIVE),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PERFORMANCE_CYCLE_CREATED",
        biz_type="PERFORMANCE_CYCLE",
        biz_id=cycle_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"cycleId": cycle_id}, context.request_id, status_code=201)


def _summary(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    summary = {
        "orgUnits": context.db.execute("SELECT COUNT(1) AS total FROM org_units WHERE status = 'ACTIVE'").fetchone()["total"],
        "employees": context.db.execute("SELECT COUNT(1) AS total FROM users WHERE status = 'ACTIVE'").fetchone()["total"],
        "indicators": context.db.execute(
            "SELECT COUNT(1) AS total FROM performance_indicators WHERE status = 'ACTIVE'"
        ).fetchone()["total"],
        "cycles": context.db.execute(
            "SELECT COUNT(1) AS total FROM performance_cycles WHERE status = 'ACTIVE'"
        ).fetchone()["total"],
        "plans": context.db.execute("SELECT COUNT(1) AS total FROM performance_plans").fetchone()["total"],
    }
    return json_response(summary, context.request_id)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/performance/indicators", _list_indicators)
    router.add("POST", "/api/v1/performance/indicators", _create_indicator)
    router.add("GET", "/api/v1/performance/cycles", _list_cycles)
    router.add("POST", "/api/v1/performance/cycles", _create_cycle)
    router.add("GET", "/api/v1/performance/masterdata/summary", _summary)
