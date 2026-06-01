from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.authz import TokenClaims, require_perm
from ..core.db import get_conn
from ..services.audit import audit_write


router = APIRouter(tags=["projects"])


class ProjectIn(BaseModel):
    name: str = Field(min_length=2)
    region: str
    site_class: str
    importance: str


@router.get("/projects")
def list_projects(_: TokenClaims = Depends(require_perm("projects:read"))) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@router.post("/projects")
def create_project(data: ProjectIn, claims: TokenClaims = Depends(require_perm("projects:write"))) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO projects(name, region, site_class, importance, owner) VALUES(?,?,?,?,?)",
            (data.name, data.region, data.site_class, data.importance, claims.sub),
        )
        audit_write(conn, claims.sub, "create", "project", str(cur.lastrowid), f"name={data.name}")
        return {"id": cur.lastrowid}


@router.put("/projects/{project_id}")
def update_project(project_id: int, data: ProjectIn, claims: TokenClaims = Depends(require_perm("projects:write"))) -> dict:
    with get_conn() as conn:
        conn.execute(
            "UPDATE projects SET name=?, region=?, site_class=?, importance=? WHERE id=?",
            (data.name, data.region, data.site_class, data.importance, project_id),
        )
        audit_write(conn, claims.sub, "update", "project", str(project_id), "fields=all")
        return {"ok": True}


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, claims: TokenClaims = Depends(require_perm("projects:write"))) -> dict:
    with get_conn() as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
        audit_write(conn, claims.sub, "delete", "project", str(project_id), "ok")
        return {"ok": True}

