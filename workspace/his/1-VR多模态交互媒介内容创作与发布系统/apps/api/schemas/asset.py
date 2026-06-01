# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class AssetCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    type: str = Field(..., min_length=2, max_length=20)
    filename: str = Field(..., min_length=1, max_length=160)
    sha256: str = Field(..., min_length=16, max_length=80)
    size: int = Field(..., ge=0, le=2_000_000_000)
    tags: list[str] = Field(default_factory=list)
    meta_json: str = Field("{}", max_length=8000)


class AssetOut(BaseModel):
    id: str
    project_id: str
    type: str
    filename: str
    sha256: str
    size: int
    tags: list[str]
    meta_json: str
    created_at: str
