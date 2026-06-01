# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Department:
    id: str
    name: str
    created_at: datetime


@dataclass(frozen=True)
class Position:
    id: str
    name: str
    dept_id: str
    created_at: datetime


@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    dept_id: str
    title: str
    created_at: datetime
