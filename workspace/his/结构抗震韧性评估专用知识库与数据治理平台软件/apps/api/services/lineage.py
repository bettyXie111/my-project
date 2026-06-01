from __future__ import annotations

from sqlite3 import Connection


def write_lineage_for_assessment(conn: Connection, assessment_id: int, indicator_ids: list[int]) -> None:
    for ind_id in indicator_ids:
        conn.execute(
            "INSERT INTO lineage_edges(from_type, from_id, to_type, to_id, note) VALUES(?,?,?,?,?)",
            ("indicator", str(ind_id), "assessment", str(assessment_id), "indicator_included"),
        )

