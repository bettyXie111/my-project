# -*- coding: utf-8 -*-
from __future__ import annotations

from apps.api.db import db
from apps.api.util import new_id, utc_now


def create_scene(project_id: str, name: str) -> str:
    sid = new_id()
    with db() as conn:
        conn.execute("INSERT INTO scene(id,project_id,name,created_at) VALUES (?,?,?,?)", (sid, project_id, name, utc_now()))
    return sid


def list_scenes(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM scene WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]


def create_node(scene_id: str, parent_id: str | None, name: str, node_type: str, transform_json: str, asset_ref_id: str | None, props_json: str) -> str:
    nid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO scene_node(id,scene_id,parent_id,name,node_type,transform_json,asset_ref_id,props_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (nid, scene_id, parent_id, name, node_type, transform_json or "{}", asset_ref_id, props_json or "{}", utc_now()),
        )
    return nid


def list_nodes(scene_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM scene_node WHERE scene_id=? ORDER BY created_at ASC", (scene_id,)).fetchall()
        return [dict(r) for r in rows]
