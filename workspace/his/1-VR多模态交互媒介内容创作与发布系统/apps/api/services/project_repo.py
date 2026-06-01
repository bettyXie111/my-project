# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3

from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now


def create_project(name: str, target_device: str, constraints_json: str) -> str:
    pid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO project(id,name,target_device,constraints_json,status,created_at) VALUES (?,?,?,?,?,?)",
            (pid, name, target_device, constraints_json or "{}", "draft", utc_now()),
        )
    return pid


def list_projects() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM project ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def get_project(project_id: str) -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT * FROM project WHERE id=?", (project_id,)).fetchone()
        return dict(row) if row else None


def update_project(project_id: str, patch: dict) -> bool:
    allow = {"name", "target_device", "constraints_json", "status"}
    fields = {k: v for k, v in patch.items() if k in allow and v is not None}
    if not fields:
        return False
    sets = ", ".join([f"{k}=?" for k in fields.keys()])
    values = list(fields.values()) + [project_id]
    with db() as conn:
        cur = conn.execute(f"UPDATE project SET {sets} WHERE id=?", values)
        return cur.rowcount > 0


def delete_project(project_id: str) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM project WHERE id=?", (project_id,))
        return cur.rowcount > 0
