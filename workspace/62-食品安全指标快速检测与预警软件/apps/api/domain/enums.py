# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import Enum


class DetectionMode(str, Enum):
    rapid = "rapid"
    routine = "routine"


class AlertLevel(str, Enum):
    info = "info"
    warn = "warn"
    critical = "critical"
