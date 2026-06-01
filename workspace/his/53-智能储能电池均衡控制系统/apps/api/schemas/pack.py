# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class PackCreate(BaseModel):
    pack_code: str = Field(..., description="电池包编号")
    vendor: str = Field(..., description="厂家")
    series_cells: int = Field(..., ge=1, le=400, description="串联数量")
    parallel_cells: int = Field(..., ge=1, le=40, description="并联数量")
    rated_capacity_ah: float = Field(..., gt=0, description="额定容量(Ah)")


class PackView(BaseModel):
    pack_id: str
    pack_code: str
    vendor: str
    series_cells: int
    parallel_cells: int
    rated_capacity_ah: float
    created_at: str
