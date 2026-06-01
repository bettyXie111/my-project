# -*- coding: utf-8 -*-
from __future__ import annotations

from .health import router as health_router
from .alerts import router as alert_router
from .samples import router as sample_router

__all__ = ["health_router", "sample_router", "alert_router"]
