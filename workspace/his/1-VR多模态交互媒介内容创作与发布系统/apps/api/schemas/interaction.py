# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class InteractionCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    scene_id: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=80)
    enabled: bool = Field(True)
    graph_json: str = Field("{}", max_length=20000)


class InteractionOut(BaseModel):
    id: str
    project_id: str
    scene_id: str
    name: str
    enabled: bool
    graph_json: str
    created_at: str
