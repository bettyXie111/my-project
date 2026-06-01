# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from .errors import BadRequest


@dataclass(frozen=True)
class Point:
    x: float
    y: float


def parse_point(obj: object, *, name: str = "point") -> Point:
    if not isinstance(obj, dict):
        raise BadRequest(f"{name} must be an object with x/y.")
    x = obj.get("x")
    y = obj.get("y")
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        raise BadRequest(f"{name}.x and {name}.y must be numbers.")
    return Point(float(x), float(y))


def polyline_length(points: list[Point]) -> float:
    if len(points) < 2:
        return 0.0
    total = 0.0
    for a, b in zip(points, points[1:], strict=False):
        total += hypot(b.x - a.x, b.y - a.y)
    return total


def polygon_area(points: list[Point]) -> float:
    if len(points) < 3:
        return 0.0
    s = 0.0
    for a, b in zip(points, points[1:] + [points[0]], strict=False):
        s += a.x * b.y - b.x * a.y
    return abs(s) * 0.5


def validate_polygon(points: list[Point]) -> None:
    if len(points) < 3:
        raise BadRequest("polygon requires >= 3 points.")
    if polygon_area(points) <= 1e-9:
        raise BadRequest("polygon area too small or degenerate.")

