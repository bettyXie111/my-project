"""SQLite database helpers and migration runner."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from .config import settings


def ensure_parent_directory(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection."""

    ensure_parent_directory(settings.database_path)
    connection = sqlite3.connect(str(settings.database_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """Provide a commit or rollback guarded transaction."""

    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def fetch_one(
    connection: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> dict[str, Any] | None:
    row = connection.execute(sql, params).fetchone()
    return row_to_dict(row)


def fetch_all(
    connection: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    rows = connection.execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows if row is not None]


def execute(
    connection: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> None:
    connection.execute(sql, params)


def init_database() -> None:
    """Run SQL migrations in lexical order."""

    with transaction() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        applied_rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
        applied_versions = {row[0] for row in applied_rows}
        migration_files = sorted(settings.migrations_dir.glob("*.sql"))
        for migration_file in migration_files:
            version = migration_file.name
            if version in applied_versions:
                continue
            sql = migration_file.read_text(encoding="utf-8")
            connection.executescript(sql)
            connection.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (?, datetime('now'))",
                (version,),
            )
