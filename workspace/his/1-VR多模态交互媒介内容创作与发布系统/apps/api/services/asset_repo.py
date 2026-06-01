# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3

from apps.api.db import db
from apps.api.util import csv_tags, new_id, parse_tags, utc_now


def create_asset(project_id: str, type: str, filename: str, sha256: str, size: int, tags: list[str], meta_json: str) -> str:
    aid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO asset(id,project_id,type,filename,sha256,size,tags,meta_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (aid, project_id, type, filename, sha256, int(size), csv_tags(tags), meta_json or "{}", utc_now()),
        )
    return aid


def list_assets(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM asset WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["tags"] = parse_tags(d.get("tags", ""))
            out.append(d)
        return out


def delete_asset(asset_id: str) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM asset WHERE id=?", (asset_id,))
        return cur.rowcount > 0
