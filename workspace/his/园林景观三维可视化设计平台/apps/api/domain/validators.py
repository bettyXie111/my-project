# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .errors import BadRequest


CODE_RE = re.compile(r"^[A-Z]{1,4}-\d{2,4}$")


def require_str(obj: dict[str, Any], key: str, *, min_len: int = 1, max_len: int = 200) -> str:
    raw = obj.get(key)
    if raw is None:
        raise BadRequest(f"{key} is required.")
    value = str(raw).strip()
    if len(value) < min_len:
        raise BadRequest(f"{key} is too short.")
    if len(value) > max_len:
        raise BadRequest(f"{key} is too long.")
    return value


def optional_str(obj: dict[str, Any], key: str, *, max_len: int = 200) -> str:
    raw = obj.get(key)
    if raw is None:
        return ""
    value = str(raw).strip()
    if len(value) > max_len:
        raise BadRequest(f"{key} is too long.")
    return value


def require_bool(obj: dict[str, Any], key: str) -> bool:
    raw = obj.get(key)
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)) and raw in (0, 1):
        return bool(raw)
    if isinstance(raw, str):
        v = raw.strip().lower()
        if v in {"true", "1", "yes", "y"}:
            return True
        if v in {"false", "0", "no", "n"}:
            return False
    raise BadRequest(f"{key} must be boolean.")


def require_float(obj: dict[str, Any], key: str, *, min_value: float | None = None, max_value: float | None = None) -> float:
    raw = obj.get(key)
    if not isinstance(raw, (int, float, str)):
        raise BadRequest(f"{key} must be number.")
    try:
        value = float(raw)
    except Exception as exc:
        raise BadRequest(f"{key} must be number.") from exc
    if min_value is not None and value < min_value:
        raise BadRequest(f"{key} must be >= {min_value}.")
    if max_value is not None and value > max_value:
        raise BadRequest(f"{key} must be <= {max_value}.")
    return value


def require_int(obj: dict[str, Any], key: str, *, min_value: int | None = None, max_value: int | None = None) -> int:
    raw = obj.get(key)
    if not isinstance(raw, (int, float, str)):
        raise BadRequest(f"{key} must be integer.")
    try:
        value = int(float(raw))
    except Exception as exc:
        raise BadRequest(f"{key} must be integer.") from exc
    if min_value is not None and value < min_value:
        raise BadRequest(f"{key} must be >= {min_value}.")
    if max_value is not None and value > max_value:
        raise BadRequest(f"{key} must be <= {max_value}.")
    return value


def validate_code(code: str, *, prefix: str) -> str:
    code = code.strip().upper()
    if not CODE_RE.match(code):
        raise BadRequest(f"code format invalid: {code}")
    if not code.startswith(prefix.upper() + "-"):
        raise BadRequest(f"code must start with '{prefix}-'.")
    return code


@dataclass(frozen=True)
class PlantInput:
    code: str
    cn_name: str
    category: str
    evergreen: bool
    crown_min_m: float
    crown_max_m: float
    season_hint: str


def parse_plant_input(payload: dict[str, Any]) -> PlantInput:
    code = validate_code(require_str(payload, "code", max_len=16), prefix="P")
    cn_name = require_str(payload, "cnName", max_len=32)
    category = require_str(payload, "category", max_len=10)
    evergreen = require_bool(payload, "evergreen")
    crown_min_m = require_float(payload, "crownMinM", min_value=0.1, max_value=50.0)
    crown_max_m = require_float(payload, "crownMaxM", min_value=0.1, max_value=50.0)
    if crown_max_m < crown_min_m:
        raise BadRequest("crownMaxM must be >= crownMinM.")
    season_hint = optional_str(payload, "seasonHint", max_len=120)
    return PlantInput(
        code=code,
        cn_name=cn_name,
        category=category,
        evergreen=evergreen,
        crown_min_m=crown_min_m,
        crown_max_m=crown_max_m,
        season_hint=season_hint,
    )


@dataclass(frozen=True)
class MaterialInput:
    code: str
    name: str
    unit: str
    usage: str


def parse_material_input(payload: dict[str, Any]) -> MaterialInput:
    code = validate_code(require_str(payload, "code", max_len=16), prefix="M")
    name = require_str(payload, "name", max_len=60)
    unit = require_str(payload, "unit", max_len=10)
    usage = optional_str(payload, "usage", max_len=40)
    return MaterialInput(code=code, name=name, unit=unit, usage=usage)


@dataclass(frozen=True)
class LightInput:
    code: str
    cct: str
    watt: int
    qty: int


def parse_light_input(payload: dict[str, Any]) -> LightInput:
    code = validate_code(require_str(payload, "code", max_len=16), prefix="L")
    cct = require_str(payload, "cct", max_len=16)
    watt = require_int(payload, "watt", min_value=1, max_value=1000)
    qty = require_int(payload, "qty", min_value=0, max_value=100000)
    return LightInput(code=code, cct=cct, watt=watt, qty=qty)

