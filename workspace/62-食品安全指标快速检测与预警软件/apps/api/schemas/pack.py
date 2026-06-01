# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class SampleCreate(BaseModel):
    sample_code: str = Field(..., description="样本编号")
    vendor: str = Field(..., description="检测来源")
    series_cells: int = Field(..., ge=1, le=400, description="检测指标数量")
    parallel_cells: int = Field(..., ge=1, le=40, description="复核轮次")
    rated_capacity_ah: float = Field(..., gt=0, description="批次容量(kg)")


class SampleView(BaseModel):
    sample_id: str
    sample_code: str
    vendor: str
    series_cells: int
    parallel_cells: int
    rated_capacity_ah: float
    created_at: str
