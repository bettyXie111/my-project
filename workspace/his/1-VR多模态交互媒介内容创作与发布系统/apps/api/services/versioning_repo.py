# -*- coding: utf-8 -*-
from __future__ import annotations

import json

from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now


def _asset_manifest(conn, project_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id,type,filename,sha256,size,tags,meta_json,created_at FROM asset WHERE project_id=? ORDER BY created_at ASC",
        (project_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def _snapshot(conn, project_id: str) -> dict:
    scenes = conn.execute("SELECT id,name,created_at FROM scene WHERE project_id=? ORDER BY created_at ASC", (project_id,)).fetchall()
    interactions = conn.execute(
        "SELECT id,scene_id,name,enabled,graph_json,created_at FROM interaction WHERE project_id=? ORDER BY created_at ASC",
        (project_id,),
    ).fetchall()
    return {
        "scenes": [dict(r) for r in scenes],
        "interactions": [dict(r) for r in interactions],
    }


def create_version(project_id: str, version: str, note: str) -> str:
    vid = new_id()
    with db() as conn:
        manifest = _asset_manifest(conn, project_id)
        snap = _snapshot(conn, project_id)
        conn.execute(
            "INSERT INTO version(id,project_id,version,note,snapshot_json,asset_manifest_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (vid, project_id, version, note or "", json_dumps(snap), json_dumps(manifest), utc_now()),
        )
    return vid


def list_versions(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM version WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
