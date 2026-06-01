from __future__ import annotations

from datetime import date, datetime, timezone

from .db import connect
from .ids import short_id
from ..schemas.observation import ObservationCreate, ObservationItem, ObservationUpdate


def _row_to_item(row) -> ObservationItem:
    plot_row = row["plot_id"]
    trial_id = row["trial_id"]
    return ObservationItem(
        id=row["id"],
        trial_id=trial_id,
        plot_id=plot_row,
        trait_id=row["trait_id"],
        observed_at=date.fromisoformat(row["observed_at"]),
        value=float(row["value"]),
        note=row["note"],
        operator=row["operator"],
        status=row["status"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def list_observations(*, trial_id: str = "", plot_id: str = "", trait_id: str = "") -> list[ObservationItem]:
    filters: list[str] = []
    params: list[object] = []

    if trial_id:
        filters.append("p.trial_id=?")
        params.append(trial_id)
    if plot_id:
        filters.append("o.plot_id=?")
        params.append(plot_id)
    if trait_id:
        filters.append("o.trait_id=?")
        params.append(trait_id)

    where = (" WHERE " + " AND ".join(filters)) if filters else ""
    sql = (
        "SELECT o.*, p.trial_id AS trial_id FROM observations o "
        "JOIN plots p ON p.id=o.plot_id"
        f"{where} ORDER BY o.observed_at DESC, o.created_at DESC"
    )

    conn = connect()
    try:
        rows = conn.execute(sql, tuple(params)).fetchall()
        return [_row_to_item(r) for r in rows]
    finally:
        conn.close()


def get_observation(obs_id: str) -> ObservationItem | None:
    conn = connect()
    try:
        row = conn.execute(
            "SELECT o.*, p.trial_id AS trial_id FROM observations o JOIN plots p ON p.id=o.plot_id WHERE o.id=?",
            (obs_id,),
        ).fetchone()
        return _row_to_item(row) if row else None
    finally:
        conn.close()


def _validate_observation_range(conn, trait_id: str, value: float) -> tuple[bool, str]:
    row = conn.execute("SELECT min_value,max_value,name,unit FROM traits WHERE id=?", (trait_id,)).fetchone()
    if not row:
        return False, "trait_not_found"
    min_v, max_v = row["min_value"], row["max_value"]
    if min_v is not None and value < float(min_v):
        return False, f"value_below_min:{row['name']}({row['unit']})"
    if max_v is not None and value > float(max_v):
        return False, f"value_above_max:{row['name']}({row['unit']})"
    return True, "ok"


def create_observation(payload: ObservationCreate) -> ObservationItem:
    conn = connect()
    try:
        plot_row = conn.execute("SELECT id FROM plots WHERE id=?", (payload.plot_id,)).fetchone()
        if not plot_row:
            raise ValueError("plot_not_found")
        ok, msg = _validate_observation_range(conn, payload.trait_id, float(payload.value))
        note = payload.note
        if not ok:
            note = (note + "；" if note else "") + f"范围提示：{msg}"

        obs_id = short_id("obs")
        conn.execute(
            "INSERT INTO observations(id,plot_id,trait_id,observed_at,value,note,operator,status,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (
                obs_id,
                payload.plot_id,
                payload.trait_id,
                payload.observed_at.isoformat(),
                float(payload.value),
                note,
                payload.operator,
                "submitted",
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT o.*, p.trial_id AS trial_id FROM observations o JOIN plots p ON p.id=o.plot_id WHERE o.id=?",
            (obs_id,),
        ).fetchone()
        return _row_to_item(row)
    finally:
        conn.close()


def update_observation_status(obs_id: str, payload: ObservationUpdate) -> ObservationItem | None:
    status = payload.status.strip().lower()
    if status not in {"draft", "submitted", "approved", "rejected"}:
        status = "submitted"
    conn = connect()
    try:
        row0 = conn.execute("SELECT id FROM observations WHERE id=?", (obs_id,)).fetchone()
        if not row0:
            return None
        conn.execute("UPDATE observations SET status=? WHERE id=?", (status, obs_id))
        conn.commit()
        return get_observation(obs_id)
    finally:
        conn.close()

