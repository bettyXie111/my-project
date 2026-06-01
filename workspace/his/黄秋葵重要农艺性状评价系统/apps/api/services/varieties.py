from __future__ import annotations

from .db import connect
from .ids import short_id
from ..schemas.variety import VarietyCreate, VarietyItem, VarietyUpdate


def _row_to_item(row) -> VarietyItem:
    return VarietyItem(
        id=row["id"],
        name=row["name"],
        source=row["source"],
        type=row["type"],
        remark=row["remark"],
        active=bool(row["active"]),
    )


def list_varieties(*, query: str = "") -> list[VarietyItem]:
    query = query.strip()
    conn = connect()
    try:
        if query:
            rows = conn.execute(
                "SELECT * FROM varieties WHERE name LIKE ? ORDER BY name",
                (f"%{query}%",),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM varieties ORDER BY name").fetchall()
        return [_row_to_item(r) for r in rows]
    finally:
        conn.close()


def get_variety(variety_id: str) -> VarietyItem | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM varieties WHERE id=?", (variety_id,)).fetchone()
        return _row_to_item(row) if row else None
    finally:
        conn.close()


def create_variety(payload: VarietyCreate) -> VarietyItem:
    conn = connect()
    try:
        vid = short_id("var")
        conn.execute(
            "INSERT INTO varieties(id,name,source,type,remark,active) VALUES(?,?,?,?,?,1)",
            (vid, payload.name, payload.source, payload.type, payload.remark),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM varieties WHERE id=?", (vid,)).fetchone()
        return _row_to_item(row)
    finally:
        conn.close()


def update_variety(variety_id: str, payload: VarietyUpdate) -> VarietyItem | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM varieties WHERE id=?", (variety_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        for field in ("name", "source", "type", "remark", "active"):
            incoming = getattr(payload, field, None)
            if incoming is not None:
                data[field] = incoming
        conn.execute(
            "UPDATE varieties SET name=?, source=?, type=?, remark=?, active=? WHERE id=?",
            (data["name"], data["source"], data["type"], data["remark"], int(bool(data["active"])), variety_id),
        )
        conn.commit()
        row2 = conn.execute("SELECT * FROM varieties WHERE id=?", (variety_id,)).fetchone()
        return _row_to_item(row2)
    finally:
        conn.close()

