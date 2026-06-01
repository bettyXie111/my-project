from __future__ import annotations

import json
from pathlib import Path

from .db import get_conn


SEED_JSON = Path("apps/api/seed/seed.json")


def _table_empty(conn, table: str) -> bool:
    row = conn.execute(f"SELECT COUNT(1) AS c FROM {table}").fetchone()
    return int(row["c"]) == 0


def ensure_seeded() -> None:
    if not SEED_JSON.exists():
        return
    payload = json.loads(SEED_JSON.read_text(encoding="utf-8"))
    with get_conn() as conn:
        if not _table_empty(conn, "users"):
            return
        for u in payload.get("users", []):
            conn.execute(
                "INSERT INTO users(username, password, role, display_name) VALUES(?,?,?,?)",
                (u["username"], u["password"], u["role"], u.get("display_name", u["username"])),
            )
        for p in payload.get("projects", []):
            conn.execute(
                "INSERT INTO projects(name, region, site_class, importance, owner) VALUES(?,?,?,?,?)",
                (p["name"], p["region"], p["site_class"], p["importance"], p["owner"]),
            )
        for s in payload.get("structures", []):
            conn.execute(
                "INSERT INTO structures(project_id, name, type, year_built, stories, material_system, fortification_intensity) VALUES(?,?,?,?,?,?,?)",
                (
                    s["project_id"],
                    s["name"],
                    s["type"],
                    s["year_built"],
                    s["stories"],
                    s["material_system"],
                    s["fortification_intensity"],
                ),
            )
        for d in payload.get("datasets", []):
            conn.execute(
                "INSERT INTO datasets(name, category, owner, source_desc, sensitivity_level) VALUES(?,?,?,?,?)",
                (d["name"], d["category"], d["owner"], d["source_desc"], d["sensitivity_level"]),
            )

