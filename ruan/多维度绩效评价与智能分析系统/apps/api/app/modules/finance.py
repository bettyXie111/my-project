"""Performance analytics and improvement action endpoints."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ..core.exceptions import ConflictError, NotFoundError
from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    audit_log,
    create_notification,
    generate_document_no,
    generate_id,
    paginate,
    require_fields,
    require_permission,
)
from .constants import BIZ_PERFORMANCE_PLAN


def _analytics_overview(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.analytics.view")
    today = date.today().isoformat()
    seven_days_later = (date.today() + timedelta(days=7)).isoformat()

    metrics = {
        "totalPlans": context.db.execute("SELECT COUNT(1) AS total FROM performance_plans").fetchone()["total"],
        "approvedPlans": context.db.execute(
            "SELECT COUNT(1) AS total FROM performance_plans WHERE status = 'APPROVED'"
        ).fetchone()["total"],
        "selfReviewPending": context.db.execute(
            "SELECT COUNT(1) AS total FROM performance_plans WHERE status = 'APPROVED'"
        ).fetchone()["total"],
        "managerReviewPending": context.db.execute(
            "SELECT COUNT(1) AS total FROM performance_plans WHERE status = 'SELF_REVIEW_SUBMITTED'"
        ).fetchone()["total"],
        "completedPlans": context.db.execute(
            "SELECT COUNT(1) AS total FROM performance_plans WHERE status = 'COMPLETED'"
        ).fetchone()["total"],
        "avgScore": round(
            float(
                context.db.execute(
                    "SELECT COALESCE(AVG(total_score), 0) AS total FROM performance_plans WHERE status = 'COMPLETED'"
                ).fetchone()["total"]
            ),
            2,
        ),
        "openActions": context.db.execute(
            "SELECT COUNT(1) AS total FROM improvement_actions WHERE status IN ('OPEN', 'IN_PROGRESS')"
        ).fetchone()["total"],
    }

    grade_rows = context.db.execute(
        """
        SELECT COALESCE(final_grade, 'UNSET') AS grade, COUNT(1) AS total
        FROM performance_plans
        WHERE status = 'COMPLETED'
        GROUP BY COALESCE(final_grade, 'UNSET')
        ORDER BY grade ASC
        """
    ).fetchall()
    grade_distribution = [{"grade": row["grade"], "count": row["total"]} for row in grade_rows]

    department_rows = context.db.execute(
        """
        SELECT org.name AS org_name, COUNT(1) AS plan_count, ROUND(AVG(p.total_score), 2) AS avg_score
        FROM performance_plans p
        JOIN org_units org ON org.id = p.org_unit_id
        WHERE p.status = 'COMPLETED'
        GROUP BY org.name
        ORDER BY avg_score DESC, plan_count DESC
        LIMIT 5
        """
    ).fetchall()
    department_ranking = [
        {"orgName": row["org_name"], "planCount": row["plan_count"], "avgScore": row["avg_score"] or 0}
        for row in department_rows
    ]

    low_score_rows = context.db.execute(
        """
        SELECT p.plan_no, u.display_name, p.total_score, p.final_grade
        FROM performance_plans p
        JOIN users u ON u.id = p.employee_user_id
        WHERE p.status = 'COMPLETED' AND p.total_score < 75
        ORDER BY p.total_score ASC, p.updated_at DESC
        LIMIT 5
        """
    ).fetchall()
    low_score_plans = [
        {
            "planNo": row["plan_no"],
            "employeeName": row["display_name"],
            "totalScore": row["total_score"],
            "grade": row["final_grade"],
        }
        for row in low_score_rows
    ]

    action_rows = context.db.execute(
        """
        SELECT action_no, action_title, due_date, status
        FROM improvement_actions
        WHERE status IN ('OPEN', 'IN_PROGRESS')
        ORDER BY due_date ASC, created_at DESC
        LIMIT 5
        """
    ).fetchall()
    open_improvements = [
        {
            "actionNo": row["action_no"],
            "title": row["action_title"],
            "dueDate": row["due_date"],
            "status": row["status"],
        }
        for row in action_rows
    ]

    alerts: list[dict[str, Any]] = []
    pending_rows = context.db.execute(
        """
        SELECT p.plan_no, employee.display_name, cycle.manager_review_deadline
        FROM performance_plans p
        JOIN users employee ON employee.id = p.employee_user_id
        JOIN performance_cycles cycle ON cycle.id = p.cycle_id
        WHERE p.status = 'SELF_REVIEW_SUBMITTED'
          AND cycle.manager_review_deadline BETWEEN ? AND ?
        ORDER BY cycle.manager_review_deadline ASC
        LIMIT 4
        """,
        (today, seven_days_later),
    ).fetchall()
    for row in pending_rows:
        alerts.append(
            {
                "type": "MANAGER_REVIEW_DUE",
                "label": f"{row['plan_no']} / {row['display_name']}",
                "value": row["manager_review_deadline"],
            }
        )

    overdue_action_rows = context.db.execute(
        """
        SELECT action_no, action_title, due_date
        FROM improvement_actions
        WHERE status IN ('OPEN', 'IN_PROGRESS') AND due_date < ?
        ORDER BY due_date ASC
        LIMIT 4
        """,
        (today,),
    ).fetchall()
    for row in overdue_action_rows:
        alerts.append(
            {
                "type": "IMPROVEMENT_OVERDUE",
                "label": f"{row['action_no']} / {row['action_title']}",
                "value": row["due_date"],
            }
        )

    return json_response(
        {
            "metrics": metrics,
            "gradeDistribution": grade_distribution,
            "departmentRanking": department_ranking,
            "lowScorePlans": low_score_plans,
            "openImprovements": open_improvements,
            "alerts": alerts,
        },
        context.request_id,
    )


def _list_improvement_actions(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.improvement.manage")
    page, page_size = paginate(context.query)
    clauses = ["1 = 1"]
    params: list[Any] = []
    for query_key, column_name in {"status": "a.status", "ownerUserId": "a.owner_user_id"}.items():
        value = context.query.get(query_key)
        if value:
            clauses.append(f"{column_name} = ?")
            params.append(value)
    sql = f"""
        SELECT
            a.*,
            p.plan_no,
            employee.display_name AS employee_name,
            owner.display_name AS owner_name,
            sponsor.display_name AS sponsor_name
        FROM improvement_actions a
        JOIN performance_plans p ON p.id = a.plan_id
        JOIN users employee ON employee.id = p.employee_user_id
        JOIN users owner ON owner.id = a.owner_user_id
        JOIN users sponsor ON sponsor.id = a.sponsor_user_id
        WHERE {' AND '.join(clauses)}
        ORDER BY a.created_at DESC
    """
    total = context.db.execute(
        f"SELECT COUNT(1) AS total FROM ({sql}) AS subquery",
        tuple(params),
    ).fetchone()["total"]
    rows = context.db.execute(
        f"{sql} LIMIT ? OFFSET ?",
        tuple(params + [page_size, (page - 1) * page_size]),
    ).fetchall()
    items = [
        {
            "id": row["id"],
            "actionNo": row["action_no"],
            "planId": row["plan_id"],
            "planNo": row["plan_no"],
            "employeeName": row["employee_name"],
            "ownerName": row["owner_name"],
            "sponsorName": row["sponsor_name"],
            "title": row["action_title"],
            "detail": row["action_detail"],
            "progressNote": row["progress_note"],
            "dueDate": row["due_date"],
            "status": row["status"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }
        for row in rows
    ]
    return json_response(
        {"items": items, "page": page, "pageSize": page_size, "total": total},
        context.request_id,
    )


def _create_improvement_action(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.improvement.manage")
    require_fields(
        context.body,
        "planId",
        "ownerUserId",
        "sponsorUserId",
        "dueDate",
        "actionTitle",
        "actionDetail",
    )
    plan_row = context.db.execute(
        "SELECT * FROM performance_plans WHERE id = ?",
        (context.body["planId"],),
    ).fetchone()
    if plan_row is None:
        raise NotFoundError("绩效计划不存在")
    if plan_row["status"] != "COMPLETED":
        raise ConflictError("仅已完成评价的绩效计划可以创建改进动作", code="ACTION_409_01")
    action_id = generate_id("action")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO improvement_actions(
            id, action_no, plan_id, owner_user_id, sponsor_user_id, due_date, action_title,
            action_detail, progress_note, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, ?, 1)
        """,
        (
            action_id,
            generate_document_no("IA"),
            context.body["planId"],
            context.body["ownerUserId"],
            context.body["sponsorUserId"],
            context.body["dueDate"],
            context.body["actionTitle"],
            context.body["actionDetail"],
            context.body.get("progressNote"),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    create_notification(
        context.db,
        receiver_user_id=context.body["ownerUserId"],
        title="新的绩效改进动作已分派",
        content=f"请在 {context.body['dueDate']} 前完成改进动作：{context.body['actionTitle']}",
        biz_ref_type=BIZ_PERFORMANCE_PLAN,
        biz_ref_id=context.body["planId"],
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="IMPROVEMENT_ACTION_CREATED",
        biz_type="IMPROVEMENT_ACTION",
        biz_id=action_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"actionId": action_id}, context.request_id, status_code=201)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/performance/analytics/overview", _analytics_overview)
    router.add("GET", "/api/v1/performance/improvement-actions", _list_improvement_actions)
    router.add("POST", "/api/v1/performance/improvement-actions", _create_improvement_action)
