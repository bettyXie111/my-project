from __future__ import annotations

from .db import connect
from .ids import short_id
from ..schemas.trait import TraitCreate, TraitItem, TraitUpdate


def _row_to_item(row) -> TraitItem:
    return TraitItem(
        id=row["id"],
        code=row["code"],
        name=row["name"],
        unit=row["unit"],
        direction=row["direction"],
        method=row["method"],
        min_value=row["min_value"],
        max_value=row["max_value"],
        active=bool(row["active"]),
    )


def list_traits(*, query: str = "") -> list[TraitItem]:
    query = query.strip()
    conn = connect()
    try:
        if query:
            rows = conn.execute(
                "SELECT * FROM traits WHERE name LIKE ? OR code LIKE ? ORDER BY code",
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM traits ORDER BY code").fetchall()
        return [_row_to_item(r) for r in rows]
    finally:
        conn.close()


def get_trait(trait_id: str) -> TraitItem | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM traits WHERE id=?", (trait_id,)).fetchone()
        return _row_to_item(row) if row else None
    finally:
        conn.close()


def create_trait(payload: TraitCreate) -> TraitItem:
    conn = connect()
    try:
        tid = short_id("trt")
        conn.execute(
            "INSERT INTO traits(id,code,name,unit,direction,method,min_value,max_value,active) VALUES(?,?,?,?,?,?,?,?,1)",
            (
                tid,
                payload.code.strip().upper(),
                payload.name,
                payload.unit,
                payload.direction,
                payload.method,
                payload.min_value,
                payload.max_value,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM traits WHERE id=?", (tid,)).fetchone()
        return _row_to_item(row)
    finally:
        conn.close()


def update_trait(trait_id: str, payload: TraitUpdate) -> TraitItem | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM traits WHERE id=?", (trait_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        for field in ("code", "name", "unit", "direction", "method", "min_value", "max_value", "active"):
            incoming = getattr(payload, field, None)
            if incoming is not None:
                data[field] = incoming
        data["code"] = str(data["code"]).strip().upper()
        conn.execute(
            "UPDATE traits SET code=?, name=?, unit=?, direction=?, method=?, min_value=?, max_value=?, active=? WHERE id=?",
            (
                data["code"],
                data["name"],
                data["unit"],
                data["direction"],
                data["method"],
                data["min_value"],
                data["max_value"],
                int(bool(data["active"])),
                trait_id,
            ),
        )
        conn.commit()
        row2 = conn.execute("SELECT * FROM traits WHERE id=?", (trait_id,)).fetchone()
        return _row_to_item(row2)
    finally:
        conn.close()

