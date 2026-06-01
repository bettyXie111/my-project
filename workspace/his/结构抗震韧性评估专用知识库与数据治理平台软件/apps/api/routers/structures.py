from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn
from ..services.audit import audit_write


router = APIRouter(tags=["structures"])


class StructureIn(BaseModel):
    project_id: int
    name: str = Field(min_length=2)
    type: str
    year_built: int
    stories: int
    material_system: str
    fortification_intensity: str


@router.get("/structures")
def list_structures(_: TokenClaims = Depends(require_perm("structures:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT s.*, p.name AS project_name FROM structures s JOIN projects p ON p.id=s.project_id ORDER BY s.id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


@router.post("/structures")
def create_structure(data: StructureIn, claims: TokenClaims = Depends(require_perm("structures:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO structures(project_id, name, type, year_built, stories, material_system, fortification_intensity) VALUES(?,?,?,?,?,?,?)",
            (data.project_id, data.name, data.type, data.year_built, data.stories, data.material_system, data.fortification_intensity),
        )
        audit_write(conn, claims.sub, "create", "structure", str(cur.lastrowid), f"name={data.name}")
        return {"id": cur.lastrowid}

