# -*- coding: utf-8 -*-
from __future__ import annotations

from apps.api.db import db
from apps.api.util import new_id, utc_now


def create_interaction(project_id: str, scene_id: str, name: str, enabled: bool, graph_json: str) -> str:
    iid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO interaction(id,project_id,scene_id,name,enabled,graph_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (iid, project_id, scene_id, name, 1 if enabled else 0, graph_json or "{}", utc_now()),
        )
    return iid


def list_interactions(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM interaction WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["enabled"] = bool(d.get("enabled"))
            out.append(d)
        return out
