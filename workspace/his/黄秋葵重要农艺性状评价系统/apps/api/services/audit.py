from __future__ import annotations

from datetime import datetime, timezone

from .db import connect
from .ids import short_id
from .jsonx import dumps, loads


def write_audit(action: str, payload: dict) -> None:
    conn = connect()
    try:
        conn.execute(
            "INSERT INTO audit_log(id, action, payload_json, created_at) VALUES(?,?,?,?)",
            (
                short_id("aud"),
                action,
                dumps(payload),
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def list_audit(limit: int = 200) -> list[dict]:
    conn = connect()
    try:
        rows = conn.execute(
            "SELECT id, action, payload_json, created_at FROM audit_log ORDER BY created_at DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        items: list[dict] = []
        for row in rows:
            items.append(
                {
                    "id": row["id"],
                    "action": row["action"],
                    "payload": loads(row["payload_json"]),
                    "created_at": row["created_at"],
                }
            )
        return items
    finally:
        conn.close()

