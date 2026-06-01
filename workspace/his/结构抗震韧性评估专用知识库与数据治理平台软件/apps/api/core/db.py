from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator


DB_PATH = Path("apps/api/runtime/app.db")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def get_conn() -> sqlite3.Connection:
    return _connect()


def tx() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        conn.execute("BEGIN;")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA_SQL = Path("apps/api/schema/schema.sql")


def init_db() -> None:
    if not SCHEMA_SQL.exists():
        raise FileNotFoundError(f"schema missing: {SCHEMA_SQL}")
    with get_conn() as conn:
        conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))

