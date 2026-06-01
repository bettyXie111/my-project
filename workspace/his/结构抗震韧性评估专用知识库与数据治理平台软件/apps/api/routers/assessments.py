from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn
from ..services.audit import audit_write
from ..services.lineage import write_lineage_for_assessment


router = APIRouter(tags=["assessments"])


class AssessmentIn(BaseModel):
    structure_id: int
    summary: str = Field(min_length=5)
    indicator_ids: list[int]


class ReviewIn(BaseModel):
    status: str
    note: str = ""


@router.get("/assessments")
def list_assessments(structure_id: int, _: TokenClaims = Depends(require_perm("assessments:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM assessments WHERE structure_id=? ORDER BY id DESC", (structure_id,)).fetchall()
        return [dict(r) for r in rows]


@router.post("/assessments")
def create_assessment(data: AssessmentIn, claims: TokenClaims = Depends(require_perm("assessments:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO assessments(structure_id, status, summary, created_by, created_at) VALUES(?,?,?,?,?)",
            (data.structure_id, "submitted", data.summary, claims.sub, int(time.time())),
        )
        assessment_id = int(cur.lastrowid)
        write_lineage_for_assessment(conn, assessment_id, data.indicator_ids)
        audit_write(conn, claims.sub, "create", "assessment", str(assessment_id), "submitted")
        return {"id": assessment_id}


@router.post("/assessments/{assessment_id}/review")
def review_assessment(assessment_id: int, data: ReviewIn, claims: TokenClaims = Depends(require_perm("assessments:review"))) -> dict:
    if data.status not in {"approved", "rejected"}:
        return {"ok": False, "message": "status must be approved/rejected"}
    with get_conn() as conn:
        conn.execute(
            "UPDATE assessments SET status=?, reviewer=?, reviewed_at=?, review_note=? WHERE id=?",
            (data.status, claims.sub, int(time.time()), data.note, assessment_id),
        )
        audit_write(conn, claims.sub, "review", "assessment", str(assessment_id), f"status={data.status}")
        return {"ok": True}

