# -*- coding: utf-8 -*-
from __future__ import annotations

from .hr import router as hr_router
from .project import router as project_router
from .asset import router as asset_router
from .scene import router as scene_router
from .interaction import router as interaction_router
from .versioning import router as versioning_router
from .audit import router as audit_router

__all__ = [
    "hr_router",
    "project_router",
    "asset_router",
    "scene_router",
    "interaction_router",
    "versioning_router",
    "audit_router",
]
