# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Iterable

from .errors import BadRequest


def sniff_dialect(text: str) -> csv.Dialect:
    sample = text[:4096]
    try:
        return csv.Sniffer().sniff(sample)
    except Exception:
        class _Default(csv.Dialect):
            delimiter = ","
            quotechar = '"'
            doublequote = True
            skipinitialspace = False
            lineterminator = "\n"
            quoting = csv.QUOTE_MINIMAL

        return _Default()


def parse_csv(text: str) -> list[list[str]]:
    if not isinstance(text, str) or not text.strip():
        raise BadRequest("csv text is empty.")
    dialect = sniff_dialect(text)
    reader = csv.reader(io.StringIO(text), dialect=dialect)
    rows = []
    for row in reader:
        if not row:
            continue
        if all(not str(cell).strip() for cell in row):
            continue
        rows.append([str(cell).strip() for cell in row])
    if not rows:
        raise BadRequest("csv contains no rows.")
    return rows


def csv_to_text(rows: Iterable[Iterable[object]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    for row in rows:
        writer.writerow(["" if v is None else str(v) for v in row])
    return buf.getvalue()


@dataclass(frozen=True)
class Table:
    header: list[str]
    rows: list[list[str]]

    def col_index(self, name: str) -> int:
        try:
            return self.header.index(name)
        except ValueError as exc:
            raise BadRequest(f"missing column: {name}") from exc

    def get(self, row: list[str], name: str) -> str:
        idx = self.col_index(name)
        return row[idx] if idx < len(row) else ""


def as_table(rows: list[list[str]]) -> Table:
    header = rows[0]
    if len(header) < 2:
        raise BadRequest("csv header too short.")
    body = rows[1:]
    return Table(header=header, rows=body)

