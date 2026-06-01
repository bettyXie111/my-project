from __future__ import annotations

from datetime import datetime, timezone

from .db import connect
from .ids import short_id
from .jsonx import dumps, loads
from ..schemas.trial import PlotCreate, PlotItem, TrialCreate, TrialDetail, TrialItem


def _row_to_trial(row) -> TrialItem:
    return TrialItem(
        id=row["id"],
        name=row["name"],
        location=row["location"],
        season=row["season"],
        design=row["design"],
        replicates=int(row["replicates"]),
        manager=row["manager"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _row_to_plot(row) -> PlotItem:
    return PlotItem(
        id=row["id"],
        trial_id=row["trial_id"],
        block=int(row["block"]),
        code=row["code"],
        variety_id=row["variety_id"],
        area_m2=float(row["area_m2"]),
        management_tags=list(loads(row["management_tags"])),
    )


def list_trials(*, query: str = "") -> list[TrialItem]:
    query = query.strip()
    conn = connect()
    try:
        if query:
            rows = conn.execute(
                "SELECT * FROM trials WHERE name LIKE ? OR location LIKE ? ORDER BY created_at DESC",
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM trials ORDER BY created_at DESC").fetchall()
        return [_row_to_trial(r) for r in rows]
    finally:
        conn.close()


def create_trial(payload: TrialCreate) -> TrialItem:
    conn = connect()
    try:
        tid = short_id("trl")
        conn.execute(
            "INSERT INTO trials(id,name,location,season,design,replicates,manager,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (
                tid,
                payload.name,
                payload.location,
                payload.season,
                payload.design,
                int(payload.replicates),
                payload.manager,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM trials WHERE id=?", (tid,)).fetchone()
        return _row_to_trial(row)
    finally:
        conn.close()


def get_trial(trial_id: str) -> TrialDetail | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM trials WHERE id=?", (trial_id,)).fetchone()
        if not row:
            return None
        trial = _row_to_trial(row)
        plot_rows = conn.execute(
            "SELECT * FROM plots WHERE trial_id=? ORDER BY block, code",
            (trial_id,),
        ).fetchall()
        plots = [_row_to_plot(r) for r in plot_rows]
        return TrialDetail(**trial.model_dump(), plots=plots)
    finally:
        conn.close()


def add_plot(trial_id: str, payload: PlotCreate) -> TrialDetail | None:
    conn = connect()
    try:
        trial_row = conn.execute("SELECT id FROM trials WHERE id=?", (trial_id,)).fetchone()
        if not trial_row:
            return None
        plot_id = short_id("plt")
        conn.execute(
            "INSERT INTO plots(id,trial_id,block,code,variety_id,area_m2,management_tags) VALUES(?,?,?,?,?,?,?)",
            (
                plot_id,
                trial_id,
                int(payload.block),
                payload.code,
                payload.variety_id,
                float(payload.area_m2),
                dumps(payload.management_tags),
            ),
        )
        conn.commit()
        return get_trial(trial_id)
    finally:
        conn.close()

