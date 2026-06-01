# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from apps.api.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from apps.api.services import project_repo


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects():
    return project_repo.list_projects()


@router.post("", response_model=dict)
def create_project(payload: ProjectCreate):
    pid = project_repo.create_project(payload.name, payload.target_device, payload.constraints_json)
    return {"id": pid}


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str):
    p = project_repo.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="not found")
    return p


@router.patch("/{project_id}", response_model=dict)
def patch_project(project_id: str, payload: ProjectUpdate):
    ok = project_repo.update_project(project_id, payload.model_dump())
    if not ok:
        raise HTTPException(status_code=404, detail="not found or no changes")
    return {"updated": True}


@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str):
    ok = project_repo.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
