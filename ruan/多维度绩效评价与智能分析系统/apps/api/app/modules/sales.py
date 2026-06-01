"""Performance review endpoints."""

from __future__ import annotations

from typing import Any

from ..core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    audit_log,
    create_notification,
    get_permissions_for_user,
    json_dumps,
    json_loads,
    require_fields,
    require_permission,
)
from .constants import BIZ_PERFORMANCE_PLAN, STATUS_APPROVED, STATUS_COMPLETED


def _get_plan(context: Any) -> dict[str, Any]:
    row = context.db.execute(
        "SELECT * FROM performance_plans WHERE id = ?",
        (context.path_params["planId"],),
    ).fetchone()
    if row is None:
        raise NotFoundError("绩效计划不存在")
    return {key: row[key] for key in row.keys()}


def _grade_for_score(score: float) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    return "D"


def _normalize_scores(plan: dict[str, Any], payload_scores: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float]:
    scorecard = json_loads(plan["scorecard_json"], [])
    if not scorecard:
        raise ValidationError("绩效计划未配置指标卡")
    if not payload_scores:
        raise ValidationError("请至少提交一条评分记录")
    by_code = {item["code"]: item for item in scorecard}
    normalized: list[dict[str, Any]] = []
    total_weight = 0.0
    weighted_score = 0.0
    seen_codes: set[str] = set()
    for item in payload_scores:
        code = item.get("code")
        if code not in by_code:
            raise ValidationError(f"未知的指标编码: {code}")
        if code in seen_codes:
            raise ValidationError(f"重复的指标编码: {code}")
        score = float(item.get("score", 0))
        if score < 0 or score > 100:
            raise ValidationError("评分必须在 0 到 100 之间")
        base = by_code[code]
        weight = float(base.get("weight", 0))
        total_weight += weight
        weighted_score += score * weight
        seen_codes.add(code)
        normalized.append(
            {
                "code": code,
                "name": base.get("name"),
                "dimension": base.get("dimension"),
                "weight": weight,
                "score": round(score, 2),
                "comment": item.get("comment", ""),
            }
        )
    if seen_codes != set(by_code.keys()):
        missing = sorted(set(by_code.keys()) - seen_codes)
        raise ValidationError(f"以下指标尚未评分: {', '.join(missing)}")
    if total_weight <= 0:
        raise ValidationError("绩效计划权重配置无效")
    return normalized, round(weighted_score / total_weight, 2)


def _submit_self_review(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.self.review")
    require_fields(context.body, "summary", "scores")
    plan = _get_plan(context)
    permissions = set(get_permissions_for_user(context.db, context.user))
    if context.user["id"] != plan["employee_user_id"] and "performance.review.manage" not in permissions:
        raise ForbiddenError("仅计划所属员工或具备评价权限的用户可以提交自评")
    if plan["status"] not in {STATUS_APPROVED, "SELF_REVIEW_SUBMITTED"}:
        raise ConflictError("当前绩效计划状态不允许提交自评", code="PLAN_409_03")
    scores, _ = _normalize_scores(plan, context.body["scores"])
    review_payload = {
        "summary": context.body["summary"],
        "scores": scores,
        "submittedAt": iso_now(),
        "submittedBy": context.user["id"],
    }
    context.db.execute(
        """
        UPDATE performance_plans
        SET self_review_json = ?, status = 'SELF_REVIEW_SUBMITTED',
            updated_at = ?, updated_by = ?, version = version + 1
        WHERE id = ?
        """,
        (json_dumps(review_payload), iso_now(), context.user["id"], plan["id"]),
    )
    create_notification(
        context.db,
        receiver_user_id=plan["manager_user_id"],
        title="员工自评已提交",
        content=f"绩效计划 {plan['plan_no']} 已完成员工自评，请进入经理评价环节。",
        biz_ref_type=BIZ_PERFORMANCE_PLAN,
        biz_ref_id=plan["id"],
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PERFORMANCE_SELF_REVIEW_SUBMITTED",
        biz_type=BIZ_PERFORMANCE_PLAN,
        biz_id=plan["id"],
        diff={"summary": context.body["summary"]},
        request_id=context.request_id,
    )
    return json_response({"planId": plan["id"], "status": "SELF_REVIEW_SUBMITTED"}, context.request_id)


def _submit_manager_review(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "performance.review.manage")
    require_fields(context.body, "summary", "scores")
    plan = _get_plan(context)
    permissions = set(get_permissions_for_user(context.db, context.user))
    if context.user["id"] != plan["manager_user_id"] and "iam.manage" not in permissions:
        raise ForbiddenError("仅直属经理或系统管理员可以提交经理评价")
    if plan["status"] != "SELF_REVIEW_SUBMITTED":
        raise ConflictError("当前绩效计划尚未进入经理评价阶段", code="PLAN_409_04")
    if not plan["self_review_json"]:
        raise ConflictError("员工尚未提交自评，不能进行经理评价", code="PLAN_409_05")
    scores, total_score = _normalize_scores(plan, context.body["scores"])
    grade = _grade_for_score(total_score)
    improvement_required = total_score < 75
    review_payload = {
        "summary": context.body["summary"],
        "scores": scores,
        "totalScore": total_score,
        "grade": grade,
        "improvementRequired": improvement_required,
        "submittedAt": iso_now(),
        "submittedBy": context.user["id"],
    }
    context.db.execute(
        """
        UPDATE performance_plans
        SET manager_review_json = ?, total_score = ?, final_grade = ?, status = ?,
            updated_at = ?, updated_by = ?, version = version + 1
        WHERE id = ?
        """,
        (
            json_dumps(review_payload),
            total_score,
            grade,
            STATUS_COMPLETED,
            iso_now(),
            context.user["id"],
            plan["id"],
        ),
    )
    create_notification(
        context.db,
        receiver_user_id=plan["employee_user_id"],
        title="绩效评价结果已生成",
        content=f"绩效计划 {plan['plan_no']} 已完成经理评价，最终等级 {grade}。",
        biz_ref_type=BIZ_PERFORMANCE_PLAN,
        biz_ref_id=plan["id"],
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PERFORMANCE_MANAGER_REVIEW_SUBMITTED",
        biz_type=BIZ_PERFORMANCE_PLAN,
        biz_id=plan["id"],
        diff={"summary": context.body["summary"], "totalScore": total_score, "grade": grade},
        request_id=context.request_id,
    )
    return json_response(
        {
            "planId": plan["id"],
            "status": STATUS_COMPLETED,
            "totalScore": total_score,
            "grade": grade,
            "improvementRequired": improvement_required,
        },
        context.request_id,
    )


def register(router: Any) -> None:
    router.add("POST", "/api/v1/performance/plans/{planId}/self-review", _submit_self_review)
    router.add("POST", "/api/v1/performance/plans/{planId}/manager-review", _submit_manager_review)
