from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn
from ..services.audit import audit_write


router = APIRouter(tags=["datasets"])


class DatasetIn(BaseModel):
    name: str = Field(min_length=2)
    category: str
    source_desc: str
    sensitivity_level: str


class DatasetVersionIn(BaseModel):
    dataset_id: int
    version: str
    change_note: str
    payload_json: dict


@router.get("/datasets")
def list_datasets(_: TokenClaims = Depends(require_perm("datasets:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM datasets ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@router.post("/datasets")
def create_dataset(data: DatasetIn, claims: TokenClaims = Depends(require_perm("datasets:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO datasets(name, category, owner, source_desc, sensitivity_level) VALUES(?,?,?,?,?)",
            (data.name, data.category, claims.sub, data.source_desc, data.sensitivity_level),
        )
        audit_write(conn, claims.sub, "create", "dataset", str(cur.lastrowid), f"name={data.name}")
        return {"id": cur.lastrowid}


@router.get("/datasets/{dataset_id}/versions")
def list_versions(dataset_id: int, _: TokenClaims = Depends(require_perm("datasets:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, dataset_id, version, change_note, created_at FROM dataset_versions WHERE dataset_id=? ORDER BY id DESC",
            (dataset_id,),
        ).fetchall()
        return [dict(r) for r in rows]


@router.post("/datasets/versions")
def create_version(data: DatasetVersionIn, claims: TokenClaims = Depends(require_perm("datasets:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO dataset_versions(dataset_id, version, change_note, payload_json) VALUES(?,?,?,?)",
            (data.dataset_id, data.version, data.change_note, json.dumps(data.payload_json, ensure_ascii=False)),
        )
        audit_write(conn, claims.sub, "create", "dataset_version", str(cur.lastrowid), f"dataset_id={data.dataset_id}, v={data.version}")
        return {"id": cur.lastrowid}

