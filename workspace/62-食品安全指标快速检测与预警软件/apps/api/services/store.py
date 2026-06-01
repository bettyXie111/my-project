# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


def utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


@dataclass(frozen=True)
class ItemRow:
    sample_id: str
    sample_code: str
    owner: str
    category_count: int
    review_rounds: int
    quantity: float
    created_at: str


@dataclass(frozen=True)
class AlertRow:
    alert_id: str
    sample_id: str
    alert_level: str
    reason: str
    status: str
    created_at: str
    acknowledged_at: str | None


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
                create table if not exists samples(
                  sample_id text primary key,
                  sample_code text not null,
                  owner text not null,
                  category_count integer not null,
                  review_rounds integer not null,
                  quantity real not null,
                  created_at text not null
                );
                create table if not exists alerts(
                  alert_id text primary key,
                  sample_id text not null,
                  alert_level text not null,
                  reason text not null,
                  status text not null,
                  created_at text not null,
                  acknowledged_at text
                );
                """
            )
            con.commit()

    def seed_demo(self) -> None:
        if self.list_samples():
            return
        self.create_sample(sample_id="SMP-0001", sample_code="S-0001", owner="示例单位", category_count=12, review_rounds=1, quantity=280.0)
        self.create_sample(sample_id="SMP-0002", sample_code="S-0002", owner="示例单位", category_count=12, review_rounds=1, quantity=180.0)
        self.seed_demo_alerts()

    def create_sample(self, *, sample_id: str, sample_code: str, owner: str, category_count: int, review_rounds: int, quantity: float) -> None:
        with self._connect() as con:
            con.execute(
                """
                insert into samples(sample_id, sample_code, owner, category_count, review_rounds, quantity, created_at)
                values(?,?,?,?,?,?,?)
                """,
                (sample_id, sample_code, owner, int(category_count), int(review_rounds), float(quantity), utc_now()),
            )
            con.commit()

    def list_samples(self) -> list[ItemRow]:
        with self._connect() as con:
            cur = con.execute(
                """
                select sample_id, sample_code, owner, category_count, review_rounds, quantity, created_at
                from samples order by created_at desc
                """
            )
            return [
                ItemRow(
                    sample_id=r["sample_id"],
                    sample_code=r["sample_code"],
                    owner=r["owner"],
                    category_count=int(r["category_count"]),
                    review_rounds=int(r["review_rounds"]),
                    quantity=float(r["quantity"]),
                    created_at=str(r["created_at"]),
                )
                for r in cur.fetchall()
            ]

    def seed_demo_alerts(self) -> None:
        if self.list_alerts():
            return
        self.create_alert(
            alert_id="ALT-0001",
            sample_id="SMP-0001",
            alert_level="高",
            reason="样本复核结论存在差异",
        )
        self.create_alert(
            alert_id="ALT-0002",
            sample_id="SMP-0002",
            alert_level="中",
            reason="样本检测指标接近阈值",
        )

    def create_alert(self, *, alert_id: str, sample_id: str, alert_level: str, reason: str) -> None:
        with self._connect() as con:
            con.execute(
                """
                insert into alerts(alert_id, sample_id, alert_level, reason, status, created_at, acknowledged_at)
                values(?,?,?,?,?,?,?)
                """,
                (alert_id, sample_id, alert_level, reason, "待确认", utc_now(), None),
            )
            con.commit()

    def list_alerts(self) -> list[AlertRow]:
        with self._connect() as con:
            cur = con.execute(
                """
                select alert_id, sample_id, alert_level, reason, status, created_at, acknowledged_at
                from alerts order by created_at desc
                """
            )
            return [
                AlertRow(
                    alert_id=r["alert_id"],
                    sample_id=r["sample_id"],
                    alert_level=r["alert_level"],
                    reason=r["reason"],
                    status=r["status"],
                    created_at=str(r["created_at"]),
                    acknowledged_at=str(r["acknowledged_at"]) if r["acknowledged_at"] else None,
                )
                for r in cur.fetchall()
            ]

    def acknowledge_alert(self, alert_id: str) -> bool:
        with self._connect() as con:
            cur = con.execute(
                """
                update alerts
                set status = ?, acknowledged_at = ?
                where alert_id = ? and status != ?
                """,
                ("已确认", utc_now(), alert_id, "已确认"),
            )
            con.commit()
            return cur.rowcount > 0
