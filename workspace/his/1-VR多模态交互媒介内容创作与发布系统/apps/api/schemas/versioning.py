# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class VersionCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    version: str = Field(..., min_length=2, max_length=20, description="版本号，如 V1.0.0")
    note: str = Field("", max_length=1000)


class VersionOut(BaseModel):
    id: str
    project_id: str
    version: str
    note: str
    snapshot_json: str
    asset_manifest_json: str
    created_at: str


class PublishCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    version_id: str = Field(..., min_length=8, max_length=64)
    channel: str = Field("local_export", max_length=40)
    note: str = Field("", max_length=1000)
    artifact_path: str = Field("", max_length=300)


class PublishOut(BaseModel):
    id: str
    project_id: str
    version_id: str
    channel: str
    note: str
    artifact_path: str
    created_at: str
