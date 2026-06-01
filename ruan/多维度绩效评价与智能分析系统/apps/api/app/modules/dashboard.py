"""Performance dashboard aggregation endpoint."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from ..core.responses import json_response
from .common import require_permission


def _scalar(connection: Any, sql: str, params: tuple[Any, ...] = ()) -> Any:
    return connection.execute(sql, params).fetchone()[0]


def _performance_dashboard(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "dashboard.view")
    today = date.today().isoformat()
    one_week_later = (date.today() + timedelta(days=7)).isoformat()

    plan_kpi = {
        "cycleCount": _scalar(context.db, "SELECT COUNT(1) FROM performance_cycles WHERE status = 'ACTIVE'"),
        "draftCount": _scalar(context.db, "SELECT COUNT(1) FROM performance_plans WHERE status = 'DRAFT'"),
        "approvalCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM performance_plans WHERE status = 'PENDING_APPROVAL'",
        ),
        "completedCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM performance_plans WHERE status = 'COMPLETED'",
        ),
    }
    review_kpi = {
        "selfReviewPendingCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM performance_plans WHERE status = 'APPROVED'",
        ),
        "managerReviewPendingCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM performance_plans WHERE status = 'SELF_REVIEW_SUBMITTED'",
        ),
        "avgScore": round(
            float(
                _scalar(
                    context.db,
                    "SELECT COALESCE(AVG(total_score), 0) FROM performance_plans WHERE status = 'COMPLETED'",
                )
            ),
            2,
        ),
        "lowScoreCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM performance_plans WHERE status = 'COMPLETED' AND total_score < 75",
        ),
    }
    improvement_kpi = {
        "openActionCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM improvement_actions WHERE status IN ('OPEN', 'IN_PROGRESS')",
        ),
        "overdueActionCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM improvement_actions WHERE status IN ('OPEN', 'IN_PROGRESS') AND due_date < ?",
            (today,),
        ),
        "notificationCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM notifications WHERE receiver_user_id = ? AND read_at IS NULL",
            (context.user["id"],),
        ),
        "todoCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM approval_tasks WHERE assignee_user_id = ? AND status = 'OPEN'",
            (context.user["id"],),
        ),
    }

    alerts: list[dict[str, Any]] = []
    nearing_deadline = context.db.execute(
        """
        SELECT p.plan_no, u.display_name, c.self_review_deadline
        FROM performance_plans p
        JOIN users u ON u.id = p.employee_user_id
        JOIN performance_cycles c ON c.id = p.cycle_id
        WHERE p.status = 'APPROVED'
          AND c.self_review_deadline BETWEEN ? AND ?
        ORDER BY c.self_review_deadline ASC
        LIMIT 4
        """,
        (today, one_week_later),
    ).fetchall()
    for row in nearing_deadline:
        alerts.append(
            {
                "type": "SELF_REVIEW_DUE",
                "label": f"{row['plan_no']} / {row['display_name']}",
                "value": row["self_review_deadline"],
            }
        )

    low_score_rows = context.db.execute(
        """
        SELECT p.plan_no, u.display_name, p.total_score
        FROM performance_plans p
        JOIN users u ON u.id = p.employee_user_id
        WHERE p.status = 'COMPLETED' AND p.total_score < 75
        ORDER BY p.total_score ASC, p.updated_at DESC
        LIMIT 4
        """
    ).fetchall()
    for row in low_score_rows:
        alerts.append(
            {
                "type": "LOW_SCORE",
                "label": f"{row['plan_no']} / {row['display_name']}",
                "value": row["total_score"],
            }
        )

    overdue_actions = context.db.execute(
        """
        SELECT action_no, action_title, due_date
        FROM improvement_actions
        WHERE status IN ('OPEN', 'IN_PROGRESS') AND due_date < ?
        ORDER BY due_date ASC
        LIMIT 4
        """,
        (today,),
    ).fetchall()
    for row in overdue_actions:
        alerts.append(
            {
                "type": "ACTION_OVERDUE",
                "label": f"{row['action_no']} / {row['action_title']}",
                "value": row["due_date"],
            }
        )

    return json_response(
        {
            "planKpi": plan_kpi,
            "reviewKpi": review_kpi,
            "improvementKpi": improvement_kpi,
            "alerts": alerts,
        },
        context.request_id,
    )


def register(router: Any) -> None:
    router.add("GET", "/api/v1/dashboard/performance", _performance_dashboard)
