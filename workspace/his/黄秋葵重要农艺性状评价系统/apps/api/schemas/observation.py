from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, Field


class ObservationItem(BaseModel):
    id: str
    trial_id: str
    plot_id: str
    trait_id: str
    observed_at: date
    value: float
    note: str = ""
    operator: str = ""
    status: str
    created_at: datetime


class ObservationCreate(BaseModel):
    plot_id: str = Field(min_length=1, max_length=64)
    trait_id: str = Field(min_length=1, max_length=64)
    observed_at: date
    value: float
    note: str = Field(default="", max_length=200)
    operator: str = Field(default="", max_length=40)


class ObservationUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=24)

