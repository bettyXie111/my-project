from __future__ import annotations

from pydantic import BaseModel, Field


class VarietyItem(BaseModel):
    id: str
    name: str
    source: str = ""
    type: str = ""
    remark: str = ""
    active: bool = True


class VarietyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    source: str = Field(default="", max_length=120)
    type: str = Field(default="", max_length=40)
    remark: str = Field(default="", max_length=400)


class VarietyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=60)
    source: str | None = Field(default=None, max_length=120)
    type: str | None = Field(default=None, max_length=40)
    remark: str | None = Field(default=None, max_length=400)
    active: bool | None = None

