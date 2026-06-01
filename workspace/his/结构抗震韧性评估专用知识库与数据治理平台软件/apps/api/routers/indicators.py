from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn
from ..services.audit import audit_write


router = APIRouter(tags=["indicators"])


class IndicatorIn(BaseModel):
    structure_id: int
    name: str = Field(min_length=2)
    method: str
    unit: str
    data_bindings_json: dict


@router.get("/indicators")
def list_indicators(structure_id: int, _: TokenClaims = Depends(require_perm("indicators:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM indicators WHERE structure_id=? ORDER BY id DESC", (structure_id,)).fetchall()
        return [dict(r) for r in rows]


@router.post("/indicators")
def create_indicator(data: IndicatorIn, claims: TokenClaims = Depends(require_perm("indicators:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO indicators(structure_id, name, method, unit, data_bindings_json) VALUES(?,?,?,?,?)",
            (data.structure_id, data.name, data.method, data.unit, json.dumps(data.data_bindings_json, ensure_ascii=False)),
        )
        audit_write(conn, claims.sub, "create", "indicator", str(cur.lastrowid), f"name={data.name}")
        return {"id": cur.lastrowid}

