from __future__ import annotations

from pydantic import BaseModel, Field


class ScoreProfileTraitItem(BaseModel):
    trait_id: str
    weight: float = Field(ge=0.0, le=1.0)
    standardize: str = Field(default="minmax", min_length=1, max_length=20)
    missing_policy: str = Field(default="ignore", min_length=1, max_length=20)


class ScoreProfileItem(BaseModel):
    id: str
    name: str
    version: str
    items: list[ScoreProfileTraitItem]
    note: str = ""


class ScoreProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    version: str = Field(default="v1", min_length=1, max_length=20)
    items: list[ScoreProfileTraitItem]
    note: str = Field(default="", max_length=200)


class ScoreBreakdown(BaseModel):
    trial_id: str
    variety_id: str
    variety_name: str
    total_score: float
    trait_scores: dict[str, float]
    explain: str = ""

