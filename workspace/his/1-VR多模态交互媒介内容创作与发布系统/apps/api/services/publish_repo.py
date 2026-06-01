# -*- coding: utf-8 -*-
from __future__ import annotations

from apps.api.db import db
from apps.api.util import new_id, utc_now


def create_publish_record(project_id: str, version_id: str, channel: str, note: str, artifact_path: str) -> str:
    pid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO publish_record(id,project_id,version_id,channel,note,artifact_path,created_at) VALUES (?,?,?,?,?,?,?)",
            (pid, project_id, version_id, channel or "local_export", note or "", artifact_path or "", utc_now()),
        )
    return pid


def list_publish_records(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM publish_record WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
