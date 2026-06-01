# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import Enum


class BalanceMode(str, Enum):
    passive = "passive"
    active = "active"


class AlarmLevel(str, Enum):
    info = "info"
    warn = "warn"
    critical = "critical"
