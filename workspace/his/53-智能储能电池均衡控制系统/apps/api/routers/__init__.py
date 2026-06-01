# -*- coding: utf-8 -*-
from __future__ import annotations

from .health import router as health_router
from .packs import router as packs_router

__all__ = ["health_router", "packs_router"]
