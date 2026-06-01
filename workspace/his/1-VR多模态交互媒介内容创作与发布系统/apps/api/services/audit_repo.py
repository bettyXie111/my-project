# -*- coding: utf-8 -*-
from __future__ import annotations

from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now


def write_audit(actor: str, action: str, target_type: str, target_id: str, detail: dict) -> str:
    aid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO audit_log(id,actor,action,target_type,target_id,detail_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (aid, actor or "system", action, target_type, target_id, json_dumps(detail or {}), utc_now()),
        )
    return aid


def list_audit(limit: int = 100) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (int(limit),)).fetchall()
        return [dict(r) for r in rows]
