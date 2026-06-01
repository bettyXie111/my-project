from __future__ import annotations

from dataclasses import dataclass
from math import isnan

from .db import connect
from .ids import short_id
from .jsonx import dumps, loads
from ..schemas.scoring import ScoreBreakdown, ScoreProfileCreate, ScoreProfileItem


@dataclass(frozen=True)
class TraitProfile:
    trait_id: str
    weight: float
    standardize: str
    missing_policy: str


def _row_to_profile(row) -> ScoreProfileItem:
    items = loads(row["items_json"])
    return ScoreProfileItem(
        id=row["id"],
        name=row["name"],
        version=row["version"],
        items=items,
        note=row["note"],
    )


def list_profiles(*, query: str = "") -> list[ScoreProfileItem]:
    query = query.strip()
    conn = connect()
    try:
        if query:
            rows = conn.execute("SELECT * FROM score_profiles WHERE name LIKE ? ORDER BY name", (f"%{query}%",)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM score_profiles ORDER BY name").fetchall()
        return [_row_to_profile(r) for r in rows]
    finally:
        conn.close()


def get_profile(profile_id: str) -> ScoreProfileItem | None:
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM score_profiles WHERE id=?", (profile_id,)).fetchone()
        return _row_to_profile(row) if row else None
    finally:
        conn.close()


def create_profile(payload: ScoreProfileCreate) -> ScoreProfileItem:
    conn = connect()
    try:
        pid = short_id("prf")
        conn.execute(
            "INSERT INTO score_profiles(id,name,version,items_json,note) VALUES(?,?,?,?,?)",
            (pid, payload.name, payload.version, dumps([i.model_dump() for i in payload.items]), payload.note),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM score_profiles WHERE id=?", (pid,)).fetchone()
        return _row_to_profile(row)
    finally:
        conn.close()


def _minmax(values: list[float], direction: str) -> dict[float, float]:
    filtered = [v for v in values if v is not None]
    if not filtered:
        return {}
    lo, hi = min(filtered), max(filtered)
    if hi == lo:
        return {v: 60.0 for v in filtered}
    out: dict[float, float] = {}
    for v in filtered:
        ratio = (v - lo) / (hi - lo)
        score = ratio * 100.0
        if direction == "lower_is_better":
            score = (1.0 - ratio) * 100.0
        out[v] = round(score, 4)
    return out


def _zscore(values: list[float], direction: str) -> dict[float, float]:
    filtered = [v for v in values if v is not None]
    if not filtered:
        return {}
    mean = sum(filtered) / len(filtered)
    var = sum((v - mean) ** 2 for v in filtered) / max(1, (len(filtered) - 1))
    if var <= 1e-12:
        return {v: 60.0 for v in filtered}
    std = var**0.5
    out: dict[float, float] = {}
    for v in filtered:
        z = (v - mean) / std
        score = 50.0 + z * 10.0
        if direction == "lower_is_better":
            score = 50.0 - z * 10.0
        out[v] = round(max(0.0, min(100.0, score)), 4)
    return out


def _load_trial_context(conn, trial_id: str) -> dict:
    trow = conn.execute("SELECT * FROM trials WHERE id=?", (trial_id,)).fetchone()
    if not trow:
        return {}
    plots = conn.execute("SELECT * FROM plots WHERE trial_id=?", (trial_id,)).fetchall()
    varieties = {r["id"]: r for r in conn.execute("SELECT * FROM varieties").fetchall()}
    traits = {r["id"]: r for r in conn.execute("SELECT * FROM traits").fetchall()}
    observations = conn.execute(
        "SELECT o.*, p.variety_id AS variety_id FROM observations o JOIN plots p ON p.id=o.plot_id WHERE p.trial_id=?",
        (trial_id,),
    ).fetchall()
    return {
        "trial": dict(trow),
        "plots": [dict(p) for p in plots],
        "varieties": {k: dict(v) for k, v in varieties.items()},
        "traits": {k: dict(v) for k, v in traits.items()},
        "observations": [dict(o) for o in observations],
    }


def _default_profile(conn) -> list[TraitProfile]:
    rows = conn.execute("SELECT id FROM traits WHERE active=1 ORDER BY code").fetchall()
    if not rows:
        return []
    weight = round(1.0 / len(rows), 6)
    return [TraitProfile(trait_id=r["id"], weight=weight, standardize="minmax", missing_policy="ignore") for r in rows]


def _normalize_weights(items: list[TraitProfile]) -> list[TraitProfile]:
    s = sum(max(0.0, float(i.weight)) for i in items)
    if s <= 1e-12:
        return [TraitProfile(i.trait_id, 0.0, i.standardize, i.missing_policy) for i in items]
    return [TraitProfile(i.trait_id, float(i.weight) / s, i.standardize, i.missing_policy) for i in items]


def _resolve_profile(conn, profile_id: str) -> list[TraitProfile]:
    if profile_id:
        row = conn.execute("SELECT items_json FROM score_profiles WHERE id=?", (profile_id,)).fetchone()
        if row:
            items = loads(row["items_json"])
            parsed: list[TraitProfile] = []
            for item in items:
                parsed.append(
                    TraitProfile(
                        trait_id=item.get("trait_id", ""),
                        weight=float(item.get("weight", 0.0)),
                        standardize=str(item.get("standardize", "minmax")),
                        missing_policy=str(item.get("missing_policy", "ignore")),
                    )
                )
            return _normalize_weights([i for i in parsed if i.trait_id])
    return _normalize_weights(_default_profile(conn))


def _aggregate_by_variety(context: dict) -> dict[str, dict[str, list[float]]]:
    plots = context["plots"]
    plot_to_variety = {p["id"]: p["variety_id"] for p in plots}
    agg: dict[str, dict[str, list[float]]] = {}
    for o in context["observations"]:
        if o.get("status") not in {"submitted", "approved"}:
            continue
        variety_id = plot_to_variety.get(o["plot_id"])
        if not variety_id:
            continue
        agg.setdefault(variety_id, {}).setdefault(o["trait_id"], []).append(float(o["value"]))
    return agg


def _choose_value(values: list[float], policy: str) -> float | None:
    if not values:
        return None
    policy = (policy or "mean").lower()
    if policy == "median":
        s = sorted(values)
        mid = len(s) // 2
        return s[mid] if len(s) % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0
    if policy == "min":
        return min(values)
    if policy == "max":
        return max(values)
    return sum(values) / len(values)


def calculate_scores(*, trial_id: str, profile_id: str = "") -> list[ScoreBreakdown] | None:
    conn = connect()
    try:
        context = _load_trial_context(conn, trial_id)
        if not context:
            return None
        profile = _resolve_profile(conn, profile_id)
        by_variety = _aggregate_by_variety(context)

        trait_meta = context["traits"]
        variety_meta = context["varieties"]

        chosen: dict[str, dict[str, float | None]] = {}
        for variety_id, trait_map in by_variety.items():
            chosen[variety_id] = {}
            for trait_id, values in trait_map.items():
                chosen[variety_id][trait_id] = _choose_value(values, "mean")

        trait_values: dict[str, list[float]] = {}
        for variety_id, tmap in chosen.items():
            for trait_id, v in tmap.items():
                if v is None:
                    continue
                trait_values.setdefault(trait_id, []).append(float(v))

        standard_maps: dict[str, dict[float, float]] = {}
        for item in profile:
            meta = trait_meta.get(item.trait_id) or {}
            direction = meta.get("direction") or "higher_is_better"
            values = trait_values.get(item.trait_id, [])
            method = (item.standardize or "minmax").lower()
            if method == "zscore":
                standard_maps[item.trait_id] = _zscore(values, direction)
            else:
                standard_maps[item.trait_id] = _minmax(values, direction)

        results: list[ScoreBreakdown] = []
        for variety_id in sorted(by_variety.keys()):
            t_scores: dict[str, float] = {}
            explain_parts: list[str] = []
            total = 0.0
            wsum = 0.0
            for item in profile:
                trait_id = item.trait_id
                weight = float(item.weight)
                raw = chosen.get(variety_id, {}).get(trait_id)
                if raw is None:
                    if item.missing_policy == "lowest":
                        score = 0.0
                        explain_parts.append(f"{trait_id}:缺失按最低分")
                    else:
                        explain_parts.append(f"{trait_id}:缺失未计入")
                        continue
                else:
                    score = standard_maps.get(trait_id, {}).get(float(raw))
                    if score is None or isnan(float(score)):
                        continue
                t_scores[trait_id] = float(score)
                total += float(score) * weight
                wsum += weight
            if wsum > 1e-12:
                total = total / wsum
            name = (variety_meta.get(variety_id) or {}).get("name") or variety_id
            results.append(
                ScoreBreakdown(
                    trial_id=trial_id,
                    variety_id=variety_id,
                    variety_name=name,
                    total_score=round(float(total), 4),
                    trait_scores={k: round(float(v), 4) for k, v in t_scores.items()},
                    explain="；".join(explain_parts[:8]),
                )
            )
        results.sort(key=lambda x: x.total_score, reverse=True)
        return results
    finally:
        conn.close()

