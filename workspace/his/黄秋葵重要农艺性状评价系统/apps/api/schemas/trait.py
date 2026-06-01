from __future__ import annotations

from pydantic import BaseModel, Field


class TraitItem(BaseModel):
    id: str
    code: str
    name: str
    unit: str
    direction: str
    method: str = ""
    min_value: float | None = None
    max_value: float | None = None
    active: bool = True


class TraitCreate(BaseModel):
    code: str = Field(min_length=1, max_length=16)
    name: str = Field(min_length=1, max_length=60)
    unit: str = Field(min_length=0, max_length=24, default="")
    direction: str = Field(min_length=1, max_length=24, default="higher_is_better")
    method: str = Field(default="", max_length=400)
    min_value: float | None = None
    max_value: float | None = None


class TraitUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=16)
    name: str | None = Field(default=None, min_length=1, max_length=60)
    unit: str | None = Field(default=None, min_length=0, max_length=24)
    direction: str | None = Field(default=None, min_length=1, max_length=24)
    method: str | None = Field(default=None, max_length=400)
    min_value: float | None = None
    max_value: float | None = None
    active: bool | None = None

