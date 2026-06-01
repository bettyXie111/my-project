from __future__ import annotations

import json
from sqlite3 import Connection


def _parse_payload(payload_json: str) -> object:
    try:
        return json.loads(payload_json)
    except Exception:
        return {}


def run_quality_checks(conn: Connection, dataset_version_id: int) -> dict:
    version = conn.execute(
        "SELECT dv.id, dv.dataset_id, dv.payload_json, d.name AS dataset_name FROM dataset_versions dv JOIN datasets d ON d.id=dv.dataset_id WHERE dv.id=?",
        (dataset_version_id,),
    ).fetchone()
    if not version:
        return {"status": "failed", "score": 0, "issues": [{"message": "dataset version not found"}]}
    rules = conn.execute(
        "SELECT rule_type, rule_expr, severity FROM quality_rules WHERE dataset_id=? AND enabled=1 ORDER BY id ASC",
        (version["dataset_id"],),
    ).fetchall()
    payload = _parse_payload(version["payload_json"] or "{}")
    issues: list[dict] = []
    score = 100
    for r in rules:
        rtype = str(r["rule_type"])
        expr = str(r["rule_expr"])
        sev = str(r["severity"])
        ok, msg = evaluate_rule(payload, rtype, expr)
        if not ok:
            issues.append({"rule_type": rtype, "expr": expr, "severity": sev, "message": msg})
            score -= 10 if sev == "warn" else 25
    score = max(0, score)
    status = "passed" if not issues else "failed"
    return {
        "dataset_version_id": dataset_version_id,
        "dataset_name": version["dataset_name"],
        "status": status,
        "score": score,
        "issues": issues,
    }


def evaluate_rule(payload: object, rule_type: str, rule_expr: str) -> tuple[bool, str]:
    if rule_type == "required_field":
        field = rule_expr.strip()
        if isinstance(payload, dict) and field in payload and payload[field] not in ("", None, []):
            return True, "ok"
        return False, f"required field missing/empty: {field}"
    if rule_type == "min_items":
        try:
            field, raw_min = [x.strip() for x in rule_expr.split(",", 1)]
            n = int(raw_min)
        except Exception:
            return False, "invalid rule_expr for min_items: expected 'field,min'"
        if isinstance(payload, dict) and isinstance(payload.get(field), list) and len(payload[field]) >= n:
            return True, "ok"
        return False, f"field '{field}' items < {n}"
    if rule_type == "enum":
        try:
            field, raw = [x.strip() for x in rule_expr.split("=", 1)]
            allowed = [x.strip() for x in raw.split("|") if x.strip()]
        except Exception:
            return False, "invalid rule_expr for enum: expected 'field=a|b|c'"
        if not isinstance(payload, dict):
            return False, "payload is not object"
        v = payload.get(field)
        if v in allowed:
            return True, "ok"
        return False, f"field '{field}' value '{v}' not in {allowed}"
    return True, "unsupported rule type ignored"

