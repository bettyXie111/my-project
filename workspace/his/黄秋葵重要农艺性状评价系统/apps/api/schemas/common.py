from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, Field


class ApiMessage(BaseModel):
    message: str = Field(default="")


class TimeMeta(BaseModel):
    created_at: datetime
    updated_at: datetime | None = None


class DateRange(BaseModel):
    start: date
    end: date

