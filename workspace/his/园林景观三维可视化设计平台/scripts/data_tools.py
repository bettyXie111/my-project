# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Data tools for local JSON state.

This module provides tiny maintenance helpers that are safe to run offline:
- validate required keys exist;
- normalize list ordering for stable diffs;
- rebuild minimal seed state if file is missing.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Result:
    ok: bool
    message: str


REQUIRED_TOP_KEYS = ["seeded", "sites", "plans", "versions", "plants", "materials", "lights", "issues", "pavings"]


def read_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_state(state: dict[str, Any]) -> Result:
    if not isinstance(state, dict):
        return Result(False, "state must be an object")
    missing = [k for k in REQUIRED_TOP_KEYS if k not in state]
    if missing:
        return Result(False, "missing keys: " + ", ".join(missing))
    for k in REQUIRED_TOP_KEYS[1:]:
        if not isinstance(state.get(k), list):
            return Result(False, f"{k} must be a list")
    return Result(True, "ok")


def sort_state(state: dict[str, Any]) -> dict[str, Any]:
    out = dict(state)
    for key in ("sites", "plans", "versions", "plants", "materials", "lights", "issues", "pavings"):
        items = out.get(key)
        if not isinstance(items, list):
            continue
        out[key] = sorted(items, key=lambda it: str((it or {}).get("id", "")))
    return out


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    state_path = project_root / "apps" / "api" / "data" / "project_state.json"
    state = read_state(state_path)
    if not state:
        print("state file missing or empty; nothing to normalize")
        return 0
    res = validate_state(state)
    if not res.ok:
        print("FAIL:", res.message)
        return 1
    sorted_state = sort_state(state)
    write_state(state_path, sorted_state)
    print("PASS: normalized", state_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

