from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn
from ..services.audit import audit_write


router = APIRouter(tags=["knowledge"])


class KnowledgeIn(BaseModel):
    title: str = Field(min_length=4)
    tags: list[str] = []
    summary: str = ""
    evidence_refs_json: dict = {}


@router.get("/knowledge")
def list_entries(q: str = "", _: TokenClaims = Depends(require_perm("knowledge:read"))) -> list[dict]:
    with get_conn() as conn:
        if q.strip():
            rows = conn.execute(
                "SELECT * FROM knowledge_entries WHERE title LIKE ? OR tags LIKE ? ORDER BY id DESC",
                (f"%{q}%", f"%{q}%"),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM knowledge_entries ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@router.post("/knowledge")
def create_entry(data: KnowledgeIn, claims: TokenClaims = Depends(require_perm("knowledge:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO knowledge_entries(title, tags, summary, evidence_refs_json, created_at, created_by) VALUES(?,?,?,?,?,?)",
            (
                data.title,
                ",".join(data.tags),
                data.summary,
                json.dumps(data.evidence_refs_json, ensure_ascii=False),
                int(time.time()),
                claims.sub,
            ),
        )
        audit_write(conn, claims.sub, "create", "knowledge_entry", str(cur.lastrowid), f"title={data.title}")
        return {"id": cur.lastrowid}

