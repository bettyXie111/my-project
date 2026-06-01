"""Audit log endpoints."""

from __future__ import annotations

from typing import Any

from ..core.responses import json_response
from .common import require_permission


def _list_audit_logs(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "audit.view")
    clauses = ["1 = 1"]
    params: list[Any] = []
    if context.query.get("bizType"):
        clauses.append("biz_type = ?")
        params.append(context.query["bizType"])
    if context.query.get("bizId"):
        clauses.append("biz_id = ?")
        params.append(context.query["bizId"])
    if context.query.get("actorUserId"):
        clauses.append("actor_user_id = ?")
        params.append(context.query["actorUserId"])
    sql = f"SELECT * FROM audit_logs WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT 200"
    rows = context.db.execute(sql, tuple(params)).fetchall()
    items = [{key: row[key] for key in row.keys()} for row in rows]
    return json_response({"items": items}, context.request_id)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/audit-logs", _list_audit_logs)
