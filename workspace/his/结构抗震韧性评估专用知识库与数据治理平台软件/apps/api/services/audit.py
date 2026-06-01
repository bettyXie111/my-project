from __future__ import annotations

import time
from sqlite3 import Connection


def audit_log(conn: Connection, *, actor: str, action: str, object_type: str, object_id: str, detail: str) -> None:
    conn.execute(
        "INSERT INTO audit_logs(actor, action, object_type, object_id, detail, at) VALUES(?,?,?,?,?,?)",
        (actor, action, object_type, object_id, detail, int(time.time())),
    )


def audit_write(conn: Connection, actor: str, action: str, object_type: str, object_id: str, detail: str) -> None:
    audit_log(conn, actor=actor, action=action, object_type=object_type, object_id=object_id, detail=detail)

