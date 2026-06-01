# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


def utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


@dataclass(frozen=True)
class PackRow:
    pack_id: str
    pack_code: str
    vendor: str
    series_cells: int
    parallel_cells: int
    rated_capacity_ah: float
    created_at: str


class Store:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                create table if not exists packs(
                  pack_id text primary key,
                  pack_code text not null,
                  vendor text not null,
                  series_cells integer not null,
                  parallel_cells integer not null,
                  rated_capacity_ah real not null,
                  created_at text not null
                );
                """
            )
            con.commit()

    def seed_demo(self) -> None:
        rows = self.list_packs()
        if rows:
            return
        self.create_pack(
            pack_id="PACK-0001",
            pack_code="SZ-ESS-0001",
            vendor="示例能源",
            series_cells=96,
            parallel_cells=1,
            rated_capacity_ah=280.0,
        )
        self.create_pack(
            pack_id="PACK-0002",
            pack_code="SZ-ESS-0002",
            vendor="示例能源",
            series_cells=96,
            parallel_cells=1,
            rated_capacity_ah=280.0,
        )

    def create_pack(
        self,
        *,
        pack_id: str,
        pack_code: str,
        vendor: str,
        series_cells: int,
        parallel_cells: int,
        rated_capacity_ah: float,
    ) -> None:
        with self._connect() as con:
            con.execute(
                """
                insert into packs(pack_id, pack_code, vendor, series_cells, parallel_cells, rated_capacity_ah, created_at)
                values(?,?,?,?,?,?,?)
                """,
                (pack_id, pack_code, vendor, int(series_cells), int(parallel_cells), float(rated_capacity_ah), utc_now()),
            )
            con.commit()

    def list_packs(self) -> list[PackRow]:
        with self._connect() as con:
            cur = con.execute(
                """
                select pack_id, pack_code, vendor, series_cells, parallel_cells, rated_capacity_ah, created_at
                from packs order by created_at desc
                """
            )
            return [
                PackRow(
                    pack_id=r["pack_id"],
                    pack_code=r["pack_code"],
                    vendor=r["vendor"],
                    series_cells=int(r["series_cells"]),
                    parallel_cells=int(r["parallel_cells"]),
                    rated_capacity_ah=float(r["rated_capacity_ah"]),
                    created_at=str(r["created_at"]),
                )
                for r in cur.fetchall()
            ]
