# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

from .errors import BadRequest
from .store import ProjectStore


def _csv_escape(value: object) -> str:
    s = "" if value is None else str(value)
    s = s.replace('"', '""')
    return f"\"{s}\""


def to_csv(rows: list[list[object]]) -> str:
    out = StringIO()
    for row in rows:
        out.write(",".join(_csv_escape(v) for v in row))
        out.write("\n")
    return out.getvalue()


@dataclass(frozen=True)
class ExportBundle:
    plants_csv: str
    materials_csv: str
    lights_csv: str


def export_all(store: ProjectStore) -> ExportBundle:
    plants = store.list_plants()
    materials = store.list_materials()
    lights = store.list_lights()
    if not plants or not materials or not lights:
        raise BadRequest("export requires non-empty plants/materials/lights.")

    plants_rows: list[list[object]] = [["编号", "中文名", "类别", "常绿/落叶", "冠幅范围(m)", "季相要点"]]
    for p in plants:
        evergreen = "常绿" if bool(p.get("evergreen")) else "落叶"
        crown = f"{p.get('crownMinM')}-{p.get('crownMaxM')}"
        plants_rows.append([p.get("code"), p.get("cnName"), p.get("category"), evergreen, crown, p.get("seasonHint")])

    materials_rows: list[list[object]] = [["编号", "名称", "单位", "用途"]]
    for m in materials:
        materials_rows.append([m.get("code"), m.get("name"), m.get("unit"), m.get("usage")])

    lights_rows: list[list[object]] = [["编号", "色温", "功率(W)", "数量"]]
    for l in lights:
        lights_rows.append([l.get("code"), l.get("cct"), l.get("watt"), l.get("qty")])

    return ExportBundle(plants_csv=to_csv(plants_rows), materials_csv=to_csv(materials_rows), lights_csv=to_csv(lights_rows))

