from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[3] / "data" / "okra_traits.db"


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_database() -> None:
    conn = connect()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS varieties (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              source TEXT NOT NULL DEFAULT '',
              type TEXT NOT NULL DEFAULT '',
              remark TEXT NOT NULL DEFAULT '',
              active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS traits (
              id TEXT PRIMARY KEY,
              code TEXT NOT NULL,
              name TEXT NOT NULL,
              unit TEXT NOT NULL DEFAULT '',
              direction TEXT NOT NULL DEFAULT 'higher_is_better',
              method TEXT NOT NULL DEFAULT '',
              min_value REAL,
              max_value REAL,
              active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS trials (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              location TEXT NOT NULL,
              season TEXT NOT NULL,
              design TEXT NOT NULL,
              replicates INTEGER NOT NULL,
              manager TEXT NOT NULL DEFAULT '',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS plots (
              id TEXT PRIMARY KEY,
              trial_id TEXT NOT NULL REFERENCES trials(id) ON DELETE CASCADE,
              block INTEGER NOT NULL,
              code TEXT NOT NULL,
              variety_id TEXT NOT NULL REFERENCES varieties(id),
              area_m2 REAL NOT NULL DEFAULT 0,
              management_tags TEXT NOT NULL DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS observations (
              id TEXT PRIMARY KEY,
              plot_id TEXT NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
              trait_id TEXT NOT NULL REFERENCES traits(id),
              observed_at TEXT NOT NULL,
              value REAL NOT NULL,
              note TEXT NOT NULL DEFAULT '',
              operator TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL DEFAULT 'draft',
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS score_profiles (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              version TEXT NOT NULL,
              items_json TEXT NOT NULL,
              note TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS audit_log (
              id TEXT PRIMARY KEY,
              action TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()

