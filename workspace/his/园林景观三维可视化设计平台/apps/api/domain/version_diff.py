# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Change:
    kind: str  # add/update/delete
    entity: str
    id: str
    before: dict[str, Any] | None
    after: dict[str, Any] | None


def _index_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for it in items:
        out[str(it.get("id"))] = it
    return out


def _diff_dict(a: dict[str, Any], b: dict[str, Any], *, keys: list[str] | None = None) -> dict[str, tuple[Any, Any]]:
    if keys is None:
        keys = sorted({*a.keys(), *b.keys()})
    changes: dict[str, tuple[Any, Any]] = {}
    for k in keys:
        if a.get(k) != b.get(k):
            changes[k] = (a.get(k), b.get(k))
    return changes


def diff_entities(entity: str, before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[Change]:
    a = _index_by_id(before)
    b = _index_by_id(after)
    changes: list[Change] = []
    for item_id, item in b.items():
        if item_id not in a:
            changes.append(Change(kind="add", entity=entity, id=item_id, before=None, after=item))
    for item_id, item in a.items():
        if item_id not in b:
            changes.append(Change(kind="delete", entity=entity, id=item_id, before=item, after=None))
    for item_id, item in b.items():
        if item_id in a:
            delta = _diff_dict(a[item_id], item)
            if delta:
                changes.append(Change(kind="update", entity=entity, id=item_id, before=a[item_id], after=item))
    return changes


def diff_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    # Snapshot structure is intentionally loose. We diff only known collections.
    out: dict[str, Any] = {"changes": []}
    for entity in ("plants", "materials", "lights", "issues", "pavings"):
        b = before.get(entity) if isinstance(before.get(entity), list) else []
        a = after.get(entity) if isinstance(after.get(entity), list) else []
        changes = diff_entities(entity, list(b), list(a))
        out["changes"].extend(
            [
                {
                    "kind": c.kind,
                    "entity": c.entity,
                    "id": c.id,
                    "fieldsChanged": sorted((_diff_dict(c.before or {}, c.after or {})).keys()) if c.kind == "update" else [],
                }
                for c in changes
            ]
        )
    out["summary"] = {
        "add": sum(1 for c in out["changes"] if c["kind"] == "add"),
        "update": sum(1 for c in out["changes"] if c["kind"] == "update"),
        "delete": sum(1 for c in out["changes"] if c["kind"] == "delete"),
    }
    return out

