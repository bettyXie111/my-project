"""Performance plan endpoints."""

from __future__ import annotations

from typing import Any

from ..core.exceptions import ConflictError, NotFoundError, ValidationError
from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    audit_log,
    generate_document_no,
    generate_id,
    json_dumps,
    json_loads,
    paginate,
    require_fields,
    require_permission,
)
from .constants import BIZ_PERFORMANCE_PLAN, STATUS_DRAFT


def _get_indicator_scorecard(connection: Any, payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("scoreItems"):
        items = payload["scoreItems"]
    else:
        rows = connection.execute(
            """
            SELECT id, code, name, dimension, weight, scoring_rule
            FROM performance_indicators
            WHERE status = 'ACTIVE'
            ORDER BY dimension ASC, code ASC
            """
        ).fetchall()
        items = [
            {
                "indicatorId": row["id"],
                "code": row["code"],
                "name": row["name"],
                "dimension": row["dimension"],
                "weight": float(row["weight"]),
                "scoringRule": row["scoring_rule"],
            }
            for row in rows
        ]
    if not items:
        raise ValidationError("请先维护绩效指标库后再创建绩效计划")
    total_weight = round(sum(float(item.get("weight", 0)) for item in items), 2)
    if total_weight <= 0:
        raise ValidationError("绩效计划指标权重总和必须大于 0")
    return items


def _serialize_plan(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "planNo": row["plan_no"],
        "cycleId": row["cycle_id"],
        "cycleName": row["cycle_name"],
        "employeeUserId": row["employee_user_id"],
        "employeeName": row["employee_name"],
        "managerUserId": row["manager_user_id"],
        "managerName": row["manager_name"],
        "orgUnitId": row["org_unit_id"],
        "orgUnitName": row["org_unit_name"],
        "title": row["title"],
        "scorecard": json_loads(row["scorecard_json"], []),
        "selfReview": json_loads(row["self_review_json"], None),
        "managerReview": json_loads(row["manager_review_json"], None),
        "totalScore": round(float(row["total_score"] or 0), 2),
        "finalGrade": row["final_grade"],
        "status": row["status"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def _list_plans(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.plan.manage")
    page, page_size = paginate(context.query)
    clauses = ["1 = 1"]
    params: list[Any] = []
    for query_key, column_name in {
        "status": "p.status",
        "cycleId": "p.cycle_id",
        "employeeUserId": "p.employee_user_id",
    }.items():
        value = context.query.get(query_key)
        if value:
            clauses.append(f"{column_name} = ?")
            params.append(value)
    keyword = context.query.get("keyword")
    if keyword:
        clauses.append("(p.plan_no LIKE ? OR p.title LIKE ? OR employee.display_name LIKE ?)")
        params.extend([f"%{keyword}%"] * 3)

    sql = f"""
        SELECT
            p.*,
            cycle.cycle_name,
            employee.display_name AS employee_name,
            manager.display_name AS manager_name,
            org.name AS org_unit_name
        FROM performance_plans p
        JOIN performance_cycles cycle ON cycle.id = p.cycle_id
        JOIN users employee ON employee.id = p.employee_user_id
        JOIN users manager ON manager.id = p.manager_user_id
        JOIN org_units org ON org.id = p.org_unit_id
        WHERE {' AND '.join(clauses)}
        ORDER BY p.created_at DESC
    """
    total = context.db.execute(
        f"SELECT COUNT(1) AS total FROM ({sql}) AS subquery",
        tuple(params),
    ).fetchone()["total"]
    rows = context.db.execute(
        f"{sql} LIMIT ? OFFSET ?",
        tuple(params + [page_size, (page - 1) * page_size]),
    ).fetchall()
    items = [_serialize_plan(row) for row in rows]
    return json_response(
        {"items": items, "page": page, "pageSize": page_size, "total": total},
        context.request_id,
    )


def _create_plan(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.plan.manage")
    require_fields(context.body, "cycleId", "employeeUserId", "managerUserId", "orgUnitId", "title")
    existing = context.db.execute(
        """
        SELECT id FROM performance_plans
        WHERE cycle_id = ? AND employee_user_id = ?
        """,
        (context.body["cycleId"], context.body["employeeUserId"]),
    ).fetchone()
    if existing is not None:
        raise ConflictError("同一考核周期下该员工的绩效计划已存在", code="PLAN_409_01")

    scorecard = _get_indicator_scorecard(context.db, context.body)
    plan_id = generate_id("plan")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO performance_plans(
            id, plan_no, cycle_id, employee_user_id, manager_user_id, org_unit_id, title,
            scorecard_json, self_review_json, manager_review_json, total_score, final_grade,
            workflow_instance_id, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, 0, NULL, NULL, ?, ?, ?, ?, ?, 1)
        """,
        (
            plan_id,
            generate_document_no("PP"),
            context.body["cycleId"],
            context.body["employeeUserId"],
            context.body["managerUserId"],
            context.body["orgUnitId"],
            context.body["title"],
            json_dumps(scorecard),
            STATUS_DRAFT,
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PERFORMANCE_PLAN_CREATED",
        biz_type=BIZ_PERFORMANCE_PLAN,
        biz_id=plan_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"planId": plan_id, "status": STATUS_DRAFT}, context.request_id, status_code=201)


def _submit_plan(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.plan.manage")
    row = context.db.execute(
        """
        SELECT p.*, cycle.cycle_name, employee.display_name AS employee_name, manager.display_name AS manager_name
        FROM performance_plans p
        JOIN performance_cycles cycle ON cycle.id = p.cycle_id
        JOIN users employee ON employee.id = p.employee_user_id
        JOIN users manager ON manager.id = p.manager_user_id
        WHERE p.id = ?
        """,
        (context.path_params["planId"],),
    ).fetchone()
    if row is None:
        raise NotFoundError("绩效计划不存在")
    if row["status"] != STATUS_DRAFT:
        raise ConflictError("只有草稿状态的绩效计划可以提交审批", code="PLAN_409_02")

    from .workflows import create_workflow_instance

    result = create_workflow_instance(
        context.db,
        biz_type=BIZ_PERFORMANCE_PLAN,
        biz_id=row["id"],
        title=f"绩效计划审批 {row['plan_no']}",
        payload={
            "cycleName": row["cycle_name"],
            "employeeName": row["employee_name"],
            "managerName": row["manager_name"],
            "scoreItemCount": len(json_loads(row["scorecard_json"], [])),
        },
        initiator_user_id=context.user["id"],
        request_id=context.request_id,
    )
    return json_response(result, context.request_id, status_code=201)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/performance/plans", _list_plans)
    router.add("POST", "/api/v1/performance/plans", _create_plan)
    router.add("POST", "/api/v1/performance/plans/{planId}/submit", _submit_plan)
