from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class TrialItem(BaseModel):
    id: str
    name: str
    location: str
    season: str
    design: str
    replicates: int
    manager: str = ""
    created_at: datetime


class PlotItem(BaseModel):
    id: str
    trial_id: str
    block: int
    code: str
    variety_id: str
    area_m2: float = 0.0
    management_tags: list[str] = []


class TrialDetail(TrialItem):
    plots: list[PlotItem]


class TrialCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=80)
    season: str = Field(min_length=1, max_length=40)
    design: str = Field(min_length=1, max_length=40, default="randomized_block")
    replicates: int = Field(default=3, ge=1, le=20)
    manager: str = Field(default="", max_length=40)


class PlotCreate(BaseModel):
    block: int = Field(ge=1, le=200)
    code: str = Field(min_length=1, max_length=24)
    variety_id: str = Field(min_length=1, max_length=64)
    area_m2: float = Field(default=0.0, ge=0.0, le=10000.0)
    management_tags: list[str] = []

