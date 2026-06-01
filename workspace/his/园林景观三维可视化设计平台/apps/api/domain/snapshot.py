# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Snapshot utilities.

Rationale:
- A plan "version" should be reviewable after data changes.
- A snapshot is a plain JSON object that contains the relevant collections.
- This module provides deterministic snapshot generation and validation helpers.
"""

from dataclasses import dataclass
from typing import Any

from .errors import BadRequest


@dataclass(frozen=True)
class Snapshot:
    season: str
    plants: list[dict[str, Any]]
    materials: list[dict[str, Any]]
    lights: list[dict[str, Any]]
    issues: list[dict[str, Any]]
    pavings: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "season": self.season,
            "plants": list(self.plants),
            "materials": list(self.materials),
            "lights": list(self.lights),
            "issues": list(self.issues),
            "pavings": list(self.pavings),
        }


def _as_list(value: object, *, name: str) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    raise BadRequest(f"{name} must be list")


def _as_str(value: object, *, name: str, default: str = "") -> str:
    if value is None:
        return default
    s = str(value).strip()
    return s


def build_snapshot(
    *,
    season: str,
    plants: list[dict[str, Any]],
    materials: list[dict[str, Any]],
    lights: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    pavings: list[dict[str, Any]],
) -> Snapshot:
    season = _as_str(season, name="season", default="春") or "春"
    return Snapshot(
        season=season,
        plants=list(plants),
        materials=list(materials),
        lights=list(lights),
        issues=list(issues),
        pavings=list(pavings),
    )


def validate_snapshot(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise BadRequest("snapshot must be object")
    season = _as_str(payload.get("season"), name="season", default="")
    if season and season not in {"春", "夏", "秋", "冬"}:
        raise BadRequest("season must be one of 春/夏/秋/冬")

    for key in ("plants", "materials", "lights", "issues", "pavings"):
        _as_list(payload.get(key), name=key)


def summarize_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    validate_snapshot(payload)
    season = _as_str(payload.get("season"), name="season", default="春") or "春"
    plants = _as_list(payload.get("plants"), name="plants")
    materials = _as_list(payload.get("materials"), name="materials")
    lights = _as_list(payload.get("lights"), name="lights")
    issues = _as_list(payload.get("issues"), name="issues")
    pavings = _as_list(payload.get("pavings"), name="pavings")
    return {
        "season": season,
        "counts": {
            "plants": len(plants),
            "materials": len(materials),
            "lights": len(lights),
            "issues": len(issues),
            "pavings": len(pavings),
        },
        "checks": {
            "hasPlants": len(plants) > 0,
            "hasMaterials": len(materials) > 0,
            "hasLights": len(lights) > 0,
        },
    }

