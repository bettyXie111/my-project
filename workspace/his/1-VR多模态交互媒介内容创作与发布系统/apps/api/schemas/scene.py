# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class SceneCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=80)


class SceneOut(BaseModel):
    id: str
    project_id: str
    name: str
    created_at: str


class SceneNodeCreate(BaseModel):
    scene_id: str = Field(..., min_length=8, max_length=64)
    parent_id: str | None = Field(None, max_length=64)
    name: str = Field(..., min_length=1, max_length=80)
    node_type: str = Field(..., min_length=2, max_length=30)
    transform_json: str = Field("{}", max_length=4000)
    asset_ref_id: str | None = Field(None, max_length=64)
    props_json: str = Field("{}", max_length=8000)


class SceneNodeOut(BaseModel):
    id: str
    scene_id: str
    parent_id: str | None
    name: str
    node_type: str
    transform_json: str
    asset_ref_id: str | None
    props_json: str
    created_at: str
