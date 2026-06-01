# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from apps.api.schemas.versioning import PublishCreate, PublishOut, VersionCreate, VersionOut
from apps.api.services import publish_repo, versioning_repo


router = APIRouter(prefix="/api/versioning", tags=["versioning"])


@router.post("/versions", response_model=dict)
def create_version(payload: VersionCreate):
    vid = versioning_repo.create_version(payload.project_id, payload.version, payload.note)
    return {"id": vid}


@router.get("/versions", response_model=list[VersionOut])
def list_versions(project_id: str):
    return versioning_repo.list_versions(project_id)


@router.post("/publish", response_model=dict)
def create_publish(payload: PublishCreate):
    pid = publish_repo.create_publish_record(payload.project_id, payload.version_id, payload.channel, payload.note, payload.artifact_path)
    return {"id": pid}


@router.get("/publish", response_model=list[PublishOut])
def list_publish(project_id: str):
    return publish_repo.list_publish_records(project_id)
