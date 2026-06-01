# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def resolve_db_path() -> Path:
    base = os.environ.get("APP_DB_DIR", "").strip()
    root = Path(base).resolve() if base else Path.cwd().resolve()
    return root / "data" / "app.db"


def ensure_db_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  target_device TEXT NOT NULL,
  constraints_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS asset (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  type TEXT NOT NULL,
  filename TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  size INTEGER NOT NULL,
  tags TEXT NOT NULL,
  meta_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_asset_project ON asset(project_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_asset_unique_hash ON asset(project_id, sha256);

CREATE TABLE IF NOT EXISTS scene (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_scene_project ON scene(project_id);

CREATE TABLE IF NOT EXISTS scene_node (
  id TEXT PRIMARY KEY,
  scene_id TEXT NOT NULL,
  parent_id TEXT,
  name TEXT NOT NULL,
  node_type TEXT NOT NULL,
  transform_json TEXT NOT NULL,
  asset_ref_id TEXT,
  props_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scene_id) REFERENCES scene(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_node_scene ON scene_node(scene_id);

CREATE TABLE IF NOT EXISTS interaction (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  scene_id TEXT NOT NULL,
  name TEXT NOT NULL,
  enabled INTEGER NOT NULL,
  graph_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
  FOREIGN KEY(scene_id) REFERENCES scene(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_interaction_project ON interaction(project_id);

CREATE TABLE IF NOT EXISTS version (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  version TEXT NOT NULL,
  note TEXT NOT NULL,
  snapshot_json TEXT NOT NULL,
  asset_manifest_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_version_unique ON version(project_id, version);

CREATE TABLE IF NOT EXISTS publish_record (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  note TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
  FOREIGN KEY(version_id) REFERENCES version(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_publish_project ON publish_record(project_id);

CREATE TABLE IF NOT EXISTS audit_log (
  id TEXT PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  detail_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(created_at);
"""
    )


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    path = resolve_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    ensure_db_schema(conn)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
