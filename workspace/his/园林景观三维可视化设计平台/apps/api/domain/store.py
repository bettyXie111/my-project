# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .errors import BadRequest, Conflict, NotFound
from .geometry import Point, parse_point, polygon_area, validate_polygon
from .ids import new_id
from .validators import LightInput, MaterialInput, PlantInput, parse_light_input, parse_material_input, parse_plant_input, validate_code


def _now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def _read_json(path: Path, *, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class Site:
    id: str
    name: str
    location: str
    scale_meter_per_px: float
    north_angle_deg: float
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "scaleMeterPerPx": self.scale_meter_per_px,
            "northAngleDeg": self.north_angle_deg,
            "createdAt": self.created_at,
        }


@dataclass
class Plan:
    id: str
    site_id: str
    name: str
    theme: str
    created_by: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "siteId": self.site_id,
            "name": self.name,
            "theme": self.theme,
            "createdBy": self.created_by,
            "createdAt": self.created_at,
        }


@dataclass
class PlanVersion:
    id: str
    plan_id: str
    version: str
    change_log: str
    created_at: str
    snapshot: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "planId": self.plan_id,
            "version": self.version,
            "changeLog": self.change_log,
            "createdAt": self.created_at,
            "snapshot": self.snapshot,
        }


@dataclass
class PlantCatalogItem:
    id: str
    code: str
    cn_name: str
    category: str
    evergreen: bool
    crown_min_m: float
    crown_max_m: float
    season_hint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "code": self.code,
            "cnName": self.cn_name,
            "category": self.category,
            "evergreen": self.evergreen,
            "crownMinM": self.crown_min_m,
            "crownMaxM": self.crown_max_m,
            "seasonHint": self.season_hint,
        }


@dataclass
class MaterialItem:
    id: str
    code: str
    name: str
    unit: str
    usage: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "code": self.code, "name": self.name, "unit": self.unit, "usage": self.usage}


@dataclass
class LightItem:
    id: str
    code: str
    cct: str
    watt: int
    qty: int

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "code": self.code, "cct": self.cct, "watt": self.watt, "qty": self.qty}


@dataclass
class Issue:
    id: str
    version_id: str
    title: str
    tag: str
    priority: str
    status: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "versionId": self.version_id,
            "title": self.title,
            "tag": self.tag,
            "priority": self.priority,
            "status": self.status,
            "createdAt": self.created_at,
        }


@dataclass
class PavingSurface:
    id: str
    plan_id: str
    material_code: str
    points: list[Point]

    def area_m2(self, *, meter_per_px: float) -> float:
        return polygon_area(self.points) * (meter_per_px**2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "planId": self.plan_id,
            "materialCode": self.material_code,
            "points": [{"x": p.x, "y": p.y} for p in self.points],
        }


class ProjectStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.data_dir = base_dir / "apps" / "api" / "data"
        self.state_path = self.data_dir / "project_state.json"
        self._state = _read_json(self.state_path, default={})
        self._ensure_seed()

    def _ensure_seed(self) -> None:
        if self._state.get("seeded"):
            return
        site_id = new_id("S")
        plan_id = new_id("PLN")
        version_id = new_id("V")
        self._state = {
            "seeded": True,
            "sites": [
                Site(
                    id=site_id,
                    name="滨水公园示范段",
                    location="华东 · 城市新区",
                    scale_meter_per_px=0.05,
                    north_angle_deg=0.0,
                    created_at=_now_iso(),
                ).to_dict()
            ],
            "plans": [
                Plan(
                    id=plan_id,
                    site_id=site_id,
                    name="自然雅致方案",
                    theme="自然雅致",
                    created_by="designer",
                    created_at=_now_iso(),
                ).to_dict()
            ],
            "versions": [
                PlanVersion(
                    id=version_id,
                    plan_id=plan_id,
                    version="V1.0.0",
                    change_log="初版：建立场地基准，整理植物与材料口径，形成评审事项清单。",
                    created_at=_now_iso(),
                    snapshot={"season": "春"},
                ).to_dict()
            ],
            "plants": [
                PlantCatalogItem(
                    id=new_id("P"),
                    code="P-001",
                    cn_name="香樟",
                    category="乔木",
                    evergreen=True,
                    crown_min_m=6,
                    crown_max_m=10,
                    season_hint="四季常绿，适合作为骨架乔木。",
                ).to_dict(),
                PlantCatalogItem(
                    id=new_id("P"),
                    code="P-002",
                    cn_name="紫薇",
                    category="乔木",
                    evergreen=False,
                    crown_min_m=3,
                    crown_max_m=5,
                    season_hint="夏季花期明显，适合节点色彩强调。",
                ).to_dict(),
                PlantCatalogItem(
                    id=new_id("P"),
                    code="P-003",
                    cn_name="红枫",
                    category="乔木",
                    evergreen=False,
                    crown_min_m=4,
                    crown_max_m=7,
                    season_hint="秋季红叶，宜与常绿灌木形成对比。",
                ).to_dict(),
                PlantCatalogItem(
                    id=new_id("P"),
                    code="P-004",
                    cn_name="海桐",
                    category="灌木",
                    evergreen=True,
                    crown_min_m=0.8,
                    crown_max_m=1.2,
                    season_hint="常绿耐修剪，可用于分隔与基础绿篱。",
                ).to_dict(),
            ],
            "materials": [
                MaterialItem(id=new_id("M"), code="M-01", name="透水砖（暖灰）", unit="㎡", usage="主园路").to_dict(),
                MaterialItem(id=new_id("M"), code="M-02", name="花岗岩火烧面", unit="㎡", usage="入口广场").to_dict(),
                MaterialItem(id=new_id("M"), code="M-03", name="防腐木平台板", unit="㎡", usage="亲水平台").to_dict(),
            ],
            "lights": [
                LightItem(id=new_id("L"), code="L-01", cct="3000K", watt=12, qty=18).to_dict(),
                LightItem(id=new_id("L"), code="L-02", cct="3500K", watt=18, qty=6).to_dict(),
            ],
            "issues": [
                Issue(
                    id="R-1001",
                    version_id=version_id,
                    title="入口动线转角偏急",
                    tag="动线",
                    priority="高",
                    status="新建",
                    created_at=_now_iso(),
                ).to_dict(),
                Issue(
                    id="R-1002",
                    version_id=version_id,
                    title="水体边缘需增加防滑提示",
                    tag="水体",
                    priority="中",
                    status="处理中",
                    created_at=_now_iso(),
                ).to_dict(),
            ],
            "pavings": [
                PavingSurface(
                    id=new_id("PV"),
                    plan_id=plan_id,
                    material_code="M-01",
                    points=[Point(10, 10), Point(210, 15), Point(230, 120), Point(15, 140)],
                ).to_dict()
            ],
        }
        self.save()

    def save(self) -> None:
        _write_json(self.state_path, self._state)

    def _list(self, key: str) -> list[dict[str, Any]]:
        raw = self._state.get(key) or []
        if not isinstance(raw, list):
            raise RuntimeError(f"state.{key} must be a list")
        return list(raw)

    def list_sites(self) -> list[dict[str, Any]]:
        return self._list("sites")

    def list_plans(self) -> list[dict[str, Any]]:
        return self._list("plans")

    def list_versions(self) -> list[dict[str, Any]]:
        return self._list("versions")

    def list_plants(self) -> list[dict[str, Any]]:
        return self._list("plants")

    def list_materials(self) -> list[dict[str, Any]]:
        return self._list("materials")

    def list_lights(self) -> list[dict[str, Any]]:
        return self._list("lights")

    def list_issues(self) -> list[dict[str, Any]]:
        return self._list("issues")

    def list_pavings(self) -> list[dict[str, Any]]:
        return self._list("pavings")

    def _replace_by_id(self, key: str, item_id: str, item: dict[str, Any]) -> dict[str, Any]:
        items = self._list(key)
        for i, it in enumerate(items):
            if str(it.get("id")) == item_id:
                items[i] = item
                self._state[key] = items
                self.save()
                return item
        raise NotFound(f"{key} item not found: {item_id}")

    def _find_one(self, key: str, item_id: str) -> dict[str, Any]:
        for item in self._list(key):
            if str(item.get("id")) == item_id:
                return item
        raise NotFound(f"{key} item not found: {item_id}")

    def get_site(self, site_id: str) -> dict[str, Any]:
        return self._find_one("sites", site_id)

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        return self._find_one("plans", plan_id)

    def get_version(self, version_id: str) -> dict[str, Any]:
        return self._find_one("versions", version_id)

    def create_issue(self, version_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title") or "").strip()
        tag = str(payload.get("tag") or "").strip()
        priority = str(payload.get("priority") or "").strip() or "中"
        if not title or not tag:
            raise BadRequest("title and tag are required.")
        issue_id = new_id("R")
        issue = Issue(
            id=issue_id,
            version_id=version_id,
            title=title,
            tag=tag,
            priority=priority,
            status="新建",
            created_at=_now_iso(),
        ).to_dict()
        self._state.setdefault("issues", []).append(issue)
        self.save()
        return issue

    def update_issue(self, issue_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        issues = self._list("issues")
        idx = None
        for i, it in enumerate(issues):
            if str(it.get("id")) == issue_id:
                idx = i
                break
        if idx is None:
            raise NotFound(f"issue not found: {issue_id}")
        it = dict(issues[idx])
        for key in ("title", "tag", "priority", "status"):
            if key in payload and payload[key] is not None:
                it[key] = str(payload[key]).strip()
        issues[idx] = it
        self._state["issues"] = issues
        self.save()
        return it

    def _ensure_code_unique(self, key: str, code: str, *, exclude_id: str | None = None) -> None:
        for it in self._list(key):
            if exclude_id is not None and str(it.get("id")) == exclude_id:
                continue
            if str(it.get("code")).strip().upper() == code.strip().upper():
                raise Conflict(f"duplicate code in {key}: {code}")

    def create_plant(self, payload: dict[str, Any]) -> dict[str, Any]:
        inp: PlantInput = parse_plant_input(payload)
        self._ensure_code_unique("plants", inp.code)
        item = PlantCatalogItem(
            id=new_id("P"),
            code=inp.code,
            cn_name=inp.cn_name,
            category=inp.category,
            evergreen=inp.evergreen,
            crown_min_m=inp.crown_min_m,
            crown_max_m=inp.crown_max_m,
            season_hint=inp.season_hint,
        ).to_dict()
        self._state.setdefault("plants", []).append(item)
        self.save()
        return item

    def update_plant(self, plant_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        current = self._find_one("plants", plant_id)
        merged = dict(current)
        merged.update(payload or {})
        inp: PlantInput = parse_plant_input(
            {
                "code": merged.get("code"),
                "cnName": merged.get("cnName"),
                "category": merged.get("category"),
                "evergreen": merged.get("evergreen"),
                "crownMinM": merged.get("crownMinM"),
                "crownMaxM": merged.get("crownMaxM"),
                "seasonHint": merged.get("seasonHint"),
            }
        )
        self._ensure_code_unique("plants", inp.code, exclude_id=plant_id)
        merged = {
            "id": plant_id,
            "code": inp.code,
            "cnName": inp.cn_name,
            "category": inp.category,
            "evergreen": inp.evergreen,
            "crownMinM": inp.crown_min_m,
            "crownMaxM": inp.crown_max_m,
            "seasonHint": inp.season_hint,
        }
        return self._replace_by_id("plants", plant_id, merged)

    def delete_plant(self, plant_id: str) -> None:
        items = self._list("plants")
        kept = [it for it in items if str(it.get("id")) != plant_id]
        if len(kept) == len(items):
            raise NotFound(f"plants item not found: {plant_id}")
        self._state["plants"] = kept
        self.save()

    def create_material(self, payload: dict[str, Any]) -> dict[str, Any]:
        inp: MaterialInput = parse_material_input(payload)
        self._ensure_code_unique("materials", inp.code)
        item = MaterialItem(id=new_id("M"), code=inp.code, name=inp.name, unit=inp.unit, usage=inp.usage).to_dict()
        self._state.setdefault("materials", []).append(item)
        self.save()
        return item

    def update_material(self, material_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        current = self._find_one("materials", material_id)
        merged = dict(current)
        merged.update(payload or {})
        inp: MaterialInput = parse_material_input(
            {"code": merged.get("code"), "name": merged.get("name"), "unit": merged.get("unit"), "usage": merged.get("usage")}
        )
        self._ensure_code_unique("materials", inp.code, exclude_id=material_id)
        item = {"id": material_id, "code": inp.code, "name": inp.name, "unit": inp.unit, "usage": inp.usage}
        return self._replace_by_id("materials", material_id, item)

    def delete_material(self, material_id: str) -> None:
        items = self._list("materials")
        kept = [it for it in items if str(it.get("id")) != material_id]
        if len(kept) == len(items):
            raise NotFound(f"materials item not found: {material_id}")
        self._state["materials"] = kept
        self.save()

    def create_light(self, payload: dict[str, Any]) -> dict[str, Any]:
        inp: LightInput = parse_light_input(payload)
        self._ensure_code_unique("lights", inp.code)
        item = LightItem(id=new_id("L"), code=inp.code, cct=inp.cct, watt=inp.watt, qty=inp.qty).to_dict()
        self._state.setdefault("lights", []).append(item)
        self.save()
        return item

    def update_light(self, light_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        current = self._find_one("lights", light_id)
        merged = dict(current)
        merged.update(payload or {})
        inp: LightInput = parse_light_input(
            {"code": merged.get("code"), "cct": merged.get("cct"), "watt": merged.get("watt"), "qty": merged.get("qty")}
        )
        self._ensure_code_unique("lights", inp.code, exclude_id=light_id)
        item = {"id": light_id, "code": inp.code, "cct": inp.cct, "watt": inp.watt, "qty": inp.qty}
        return self._replace_by_id("lights", light_id, item)

    def delete_light(self, light_id: str) -> None:
        items = self._list("lights")
        kept = [it for it in items if str(it.get("id")) != light_id]
        if len(kept) == len(items):
            raise NotFound(f"lights item not found: {light_id}")
        self._state["lights"] = kept
        self.save()

    def import_plants_csv(self, csv_rows: list[list[str]]) -> dict[str, Any]:
        # Expected header: 编号,中文名,类别,常绿/落叶,冠幅最小,冠幅最大,季相要点
        if not csv_rows or len(csv_rows) < 2:
            raise BadRequest("csv requires header + at least 1 row.")
        header = [h.strip() for h in csv_rows[0]]
        col = {name: header.index(name) for name in header}
        required = ["编号", "中文名", "类别", "常绿/落叶", "冠幅最小", "冠幅最大"]
        for r in required:
            if r not in col:
                raise BadRequest(f"missing csv column: {r}")

        created = 0
        updated = 0
        errors: list[str] = []
        for idx, row in enumerate(csv_rows[1:], start=2):
            try:
                code = validate_code(row[col["编号"]], prefix="P")
                cn = row[col["中文名"]].strip()
                category = row[col["类别"]].strip()
                ev = row[col["常绿/落叶"]].strip()
                evergreen = ev in {"常绿", "是", "TRUE", "true", "1"}
                crown_min = float(row[col["冠幅最小"]])
                crown_max = float(row[col["冠幅最大"]])
                hint = row[col.get("季相要点", -1)].strip() if "季相要点" in col and col["季相要点"] < len(row) else ""
                payload = {
                    "code": code,
                    "cnName": cn,
                    "category": category,
                    "evergreen": evergreen,
                    "crownMinM": crown_min,
                    "crownMaxM": crown_max,
                    "seasonHint": hint,
                }
                # Upsert by code
                found = None
                for it in self._list("plants"):
                    if str(it.get("code")).strip().upper() == code:
                        found = it
                        break
                if found is None:
                    self.create_plant(payload)
                    created += 1
                else:
                    self.update_plant(str(found.get("id")), payload)
                    updated += 1
            except Exception as exc:
                errors.append(f"line {idx}: {exc}")
        return {"created": created, "updated": updated, "errors": errors}

    def create_paving(self, plan_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        material_code = str(payload.get("materialCode") or "").strip()
        points_raw = payload.get("points")
        if not material_code:
            raise BadRequest("materialCode is required.")
        if not isinstance(points_raw, list):
            raise BadRequest("points must be a list of {x,y}.")
        points = [parse_point(p, name="points[i]") for p in points_raw]
        validate_polygon(points)
        paving = PavingSurface(id=new_id("PV"), plan_id=plan_id, material_code=material_code, points=points).to_dict()
        self._state.setdefault("pavings", []).append(paving)
        self.save()
        return paving

    def ensure_unique_codes(self) -> None:
        # Defensive consistency check.
        for key, code_field in (("plants", "code"), ("materials", "code"), ("lights", "code")):
            seen: set[str] = set()
            for it in self._list(key):
                code = str(it.get(code_field) or "").strip()
                if not code:
                    raise BadRequest(f"{key} item missing code.")
                if code in seen:
                    raise Conflict(f"duplicate {key} code: {code}")
                seen.add(code)
