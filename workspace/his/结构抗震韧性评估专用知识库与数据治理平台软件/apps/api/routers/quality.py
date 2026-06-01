from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn
from ..services.audit import audit_write
from ..services.quality import run_quality_checks


router = APIRouter(tags=["quality"])


class RuleIn(BaseModel):
    dataset_id: int
    rule_type: str
    rule_expr: str
    severity: str
    enabled: bool = True


@router.get("/quality/rules")
def list_rules(dataset_id: int, _: TokenClaims = Depends(require_perm("quality:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM quality_rules WHERE dataset_id=? ORDER BY id DESC", (dataset_id,)).fetchall()
        return [dict(r) for r in rows]


@router.post("/quality/rules")
def create_rule(data: RuleIn, claims: TokenClaims = Depends(require_perm("quality:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO quality_rules(dataset_id, rule_type, rule_expr, severity, enabled) VALUES(?,?,?,?,?)",
            (data.dataset_id, data.rule_type, data.rule_expr, data.severity, 1 if data.enabled else 0),
        )
        audit_write(conn, claims.sub, "create", "quality_rule", str(cur.lastrowid), f"type={data.rule_type}")
        return {"id": cur.lastrowid}


@router.post("/quality/run")
def run_quality(dataset_version_id: int, claims: TokenClaims = Depends(require_perm("quality:write"))) -> dict:
    with get_conn() as conn:
        result = run_quality_checks(conn, dataset_version_id)
        cur = conn.execute(
            "INSERT INTO quality_runs(dataset_version_id, status, score, detail_json, run_at) VALUES(?,?,?,?,?)",
            (dataset_version_id, result["status"], result["score"], json.dumps(result, ensure_ascii=False), int(time.time())),
        )
        audit_write(conn, claims.sub, "run", "quality_run", str(cur.lastrowid), f"dataset_version_id={dataset_version_id}")
        return {"id": cur.lastrowid, "result": result}


@router.get("/quality/runs")
def list_runs(dataset_version_id: int, _: TokenClaims = Depends(require_perm("quality:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, dataset_version_id, status, score, run_at FROM quality_runs WHERE dataset_version_id=? ORDER BY id DESC",
            (dataset_version_id,),
        ).fetchall()
        return [dict(r) for r in rows]

