# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80, description="项目名称")
    target_device: str = Field(..., min_length=2, max_length=30, description="目标设备")
    constraints_json: str = Field("{}", max_length=4000, description="性能/规格约束 JSON")


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=80)
    target_device: str | None = Field(None, min_length=2, max_length=30)
    constraints_json: str | None = Field(None, max_length=4000)
    status: str | None = Field(None, max_length=30)


class ProjectOut(BaseModel):
    id: str
    name: str
    target_device: str
    constraints_json: str
    status: str
    created_at: str
