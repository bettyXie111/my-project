"""Cross-module helpers."""

from __future__ import annotations

import csv
import io
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any

from ..core.config import settings
from ..core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from ..core.responses import page_response, text_response
from ..core.security import iso_now
from .constants import (
    BIZ_CONTRACT,
    BIZ_EXPENSE,
    BIZ_PROCUREMENT_REQUEST,
    ROLE_PERMISSION_MAP,
    STATUS_ACTIVE,
    STATUS_APPROVED,
    STATUS_COMPLETED,
    STATUS_EFFECTIVE,
    STATUS_PENDING,
    STATUS_REJECTED,
)


def json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def json_loads(raw: str | None, default: Any) -> Any:
    if not raw:
        return default
    return json.loads(raw)


def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def generate_document_no(prefix: str) -> str:
    return f"{prefix}-{datetime.utcnow():%Y%m%d%H%M%S%f}-{uuid.uuid4().hex[:6].upper()}"


def sanitize_mobile(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) < 7:
        return "***"
    return f"{value[:3]}****{value[-4:]}"


def sanitize_email(value: str | None) -> str | None:
    if not value or "@" not in value:
        return value
    name, domain = value.split("@", 1)
    masked = f"{name[:1]}***" if name else "***"
    return f"{masked}@{domain}"


def now_plus_hours(hours: int) -> str:
    return (datetime.utcnow() + timedelta(hours=hours)).replace(microsecond=0).isoformat() + "Z"


def require_fields(payload: dict[str, Any], *field_names: str) -> None:
    missing = [name for name in field_names if payload.get(name) in (None, "", [])]
    if missing:
        raise ValidationError(f"缺少必要字段: {', '.join(missing)}")


def get_permissions_for_user(connection: sqlite3.Connection, user: dict[str, Any]) -> list[str]:
    role_codes = json_loads(user["role_codes_json"], [])
    if not role_codes:
        return []
    permissions: set[str] = set()
    for role_code in role_codes:
        permissions.update(ROLE_PERMISSION_MAP.get(role_code, []))
    if not permissions:
        role_rows = connection.execute(
            "SELECT permissions_json FROM roles WHERE code IN (%s)"
            % ",".join("?" for _ in role_codes),
            tuple(role_codes),
        ).fetchall()
        for row in role_rows:
            permissions.update(json_loads(row["permissions_json"], []))
    return sorted(permissions)


def require_permission(connection: sqlite3.Connection, user: dict[str, Any], permission: str) -> None:
    if permission not in get_permissions_for_user(connection, user):
        raise ForbiddenError()


def get_role_rows(connection: sqlite3.Connection, role_codes: list[str]) -> list[dict[str, Any]]:
    if not role_codes:
        return []
    rows = connection.execute(
        "SELECT * FROM roles WHERE code IN (%s)" % ",".join("?" for _ in role_codes),
        tuple(role_codes),
    ).fetchall()
    return [{key: row[key] for key in row.keys()} for row in rows]


def get_data_scopes(connection: sqlite3.Connection, user: dict[str, Any]) -> list[str]:
    scope_values = []
    for row in get_role_rows(connection, json_loads(user["role_codes_json"], [])):
        scope_values.append(row["data_scope_type"])
    return sorted(set(scope_values))


def paginate(query: dict[str, Any]) -> tuple[int, int]:
    page = max(int(query.get("page", 1)), 1)
    page_size = min(max(int(query.get("pageSize", 20)), 1), 100)
    return page, page_size


def audit_log(
    connection: sqlite3.Connection,
    *,
    actor_user_id: str,
    action_type: str,
    biz_type: str,
    biz_id: str,
    diff: dict[str, Any],
    request_id: str,
) -> None:
    connection.execute(
        """
        INSERT INTO audit_logs(
            id, actor_user_id, action_type, biz_type, biz_id, diff_json, request_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            generate_id("audit"),
            actor_user_id,
            action_type,
            biz_type,
            biz_id,
            json_dumps(diff),
            request_id,
            iso_now(),
        ),
    )


def create_notification(
    connection: sqlite3.Connection,
    *,
    receiver_user_id: str,
    title: str,
    content: str,
    biz_ref_type: str | None = None,
    biz_ref_id: str | None = None,
) -> None:
    now = iso_now()
    connection.execute(
        """
        INSERT INTO notifications(
            id, channel, receiver_user_id, title, content, read_at, biz_ref_type, biz_ref_id,
            status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, 'IN_APP', ?, ?, ?, NULL, ?, ?, ?, ?, 'system', ?, 'system', 1)
        """,
        (
            generate_id("notice"),
            receiver_user_id,
            title,
            content,
            biz_ref_type,
            biz_ref_id,
            STATUS_ACTIVE,
            now,
            now,
        ),
    )


def get_entity(connection: sqlite3.Connection, table: str, entity_id: str) -> dict[str, Any]:
    row = connection.execute(f"SELECT * FROM {table} WHERE id = ?", (entity_id,)).fetchone()
    if row is None:
        raise NotFoundError(f"{table} 数据不存在")
    return {key: row[key] for key in row.keys()}


def get_entity_by_code(connection: sqlite3.Connection, table: str, code: str) -> dict[str, Any] | None:
    row = connection.execute(f"SELECT * FROM {table} WHERE code = ?", (code,)).fetchone()
    return {key: row[key] for key in row.keys()} if row is not None else None


def ensure_unique_code(connection: sqlite3.Connection, table: str, code: str) -> None:
    if get_entity_by_code(connection, table, code) is not None:
        raise ConflictError(f"{table} 编码已存在")


def save_idempotent_response(
    connection: sqlite3.Connection,
    key: str,
    endpoint: str,
    response: dict[str, Any],
) -> None:
    connection.execute(
        """
        INSERT OR REPLACE INTO idempotency_keys(id, idem_key, endpoint, response_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (generate_id("idem"), key, endpoint, json_dumps(response), iso_now()),
    )


def load_idempotent_response(
    connection: sqlite3.Connection,
    key: str | None,
    endpoint: str,
) -> dict[str, Any] | None:
    if not key:
        return None
    row = connection.execute(
        "SELECT response_json FROM idempotency_keys WHERE idem_key = ? AND endpoint = ?",
        (key, endpoint),
    ).fetchone()
    if row is None:
        return None
    return json.loads(row["response_json"])


def get_budget(connection: sqlite3.Connection, budget_key: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM budgets WHERE budget_key = ? AND status = 'ACTIVE'",
        (budget_key,),
    ).fetchone()
    if row is None:
        raise ValidationError(f"预算不存在: {budget_key}")
    return {key: row[key] for key in row.keys()}


def validate_budget(
    connection: sqlite3.Connection,
    budget_key: str,
    amount: float,
) -> dict[str, Any]:
    budget = get_budget(connection, budget_key)
    available = float(budget["budget_amount"]) - float(budget["used_amount"])
    allowed = available >= amount
    result = {
        "budgetKey": budget_key,
        "budgetAmount": float(budget["budget_amount"]),
        "usedAmount": float(budget["used_amount"]),
        "availableAmount": available,
        "requestedAmount": amount,
        "allowed": allowed,
        "controlMode": budget["control_mode"],
    }
    if not allowed and (budget["control_mode"] == "HARD" or settings.enable_hard_budget_control):
        raise ConflictError("预算不足或超预算被阻断", code="BUDGET_409_01")
    return result


def reserve_budget(connection: sqlite3.Connection, budget_key: str, amount: float) -> None:
    budget = get_budget(connection, budget_key)
    new_used_amount = float(budget["used_amount"]) + amount
    connection.execute(
        "UPDATE budgets SET used_amount = ?, updated_at = ?, version = version + 1 WHERE id = ?",
        (new_used_amount, iso_now(), budget["id"]),
    )


def apply_business_status(
    connection: sqlite3.Connection,
    *,
    biz_type: str,
    biz_id: str,
    status: str,
    workflow_instance_id: str | None = None,
) -> None:
    table_mapping = {
        BIZ_PROCUREMENT_REQUEST: "procurement_requests",
        BIZ_CONTRACT: "contracts",
        BIZ_EXPENSE: "expense_claims",
    }
    table = table_mapping.get(biz_type)
    if table is None:
        return
    if workflow_instance_id:
        connection.execute(
            f"""
            UPDATE {table}
            SET status = ?, workflow_instance_id = ?, updated_at = ?, version = version + 1
            WHERE id = ?
            """,
            (status, workflow_instance_id, iso_now(), biz_id),
        )
        return
    if table == "contracts" and status == STATUS_EFFECTIVE:
        connection.execute(
            """
            UPDATE contracts
            SET status = ?, effective_date = COALESCE(effective_date, ?), updated_at = ?, version = version + 1
            WHERE id = ?
            """,
            (status, iso_now()[:10], iso_now(), biz_id),
        )
        return
    connection.execute(
        f"UPDATE {table} SET status = ?, updated_at = ?, version = version + 1 WHERE id = ?",
        (status, iso_now(), biz_id),
    )


def build_list_sql(
    table: str,
    *,
    keyword_columns: list[str] | None = None,
    extra_filters: dict[str, str] | None = None,
    query: dict[str, Any],
) -> tuple[str, list[Any]]:
    clauses = ["1 = 1"]
    params: list[Any] = []
    keyword = query.get("keyword")
    if keyword and keyword_columns:
        clauses.append("(" + " OR ".join(f"{column} LIKE ?" for column in keyword_columns) + ")")
        params.extend([f"%{keyword}%"] * len(keyword_columns))
    if extra_filters:
        for query_key, column_name in extra_filters.items():
            value = query.get(query_key)
            if value:
                clauses.append(f"{column_name} = ?")
                params.append(value)
    sql = f"SELECT * FROM {table} WHERE {' AND '.join(clauses)} ORDER BY created_at DESC"
    return sql, params


def page_from_sql(
    connection: sqlite3.Connection,
    *,
    sql: str,
    params: list[Any],
    query: dict[str, Any],
    request_id: str,
    item_transform: callable | None = None,
) -> tuple[int, list[tuple[str, str]], bytes]:
    page, page_size = paginate(query)
    total_sql = f"SELECT COUNT(1) AS total FROM ({sql}) AS subquery"
    total = connection.execute(total_sql, tuple(params)).fetchone()["total"]
    offset = (page - 1) * page_size
    paginated_sql = f"{sql} LIMIT ? OFFSET ?"
    rows = connection.execute(paginated_sql, tuple(params + [page_size, offset])).fetchall()
    items = []
    for row in rows:
        item = {key: row[key] for key in row.keys()}
        items.append(item_transform(item) if item_transform else item)
    return page_response(items, page, page_size, total, request_id)


def maybe_csv_export(items: list[dict[str, Any]], file_name: str) -> tuple[int, list[tuple[str, str]], bytes]:
    buffer = io.StringIO()
    if items:
        writer = csv.DictWriter(buffer, fieldnames=list(items[0].keys()))
        writer.writeheader()
        writer.writerows(items)
    else:
        buffer.write("")
    return text_response(
        buffer.getvalue(),
        content_type=f"text/csv; charset=utf-8; name={file_name}",
    )


def mask_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user["id"],
        "username": user["username"],
        "displayName": user["display_name"],
        "email": sanitize_email(user.get("email")),
        "mobile": sanitize_mobile(user.get("mobile")),
        "orgUnitId": user["org_unit_id"],
        "roleCodes": json_loads(user["role_codes_json"], []),
        "status": user["status"],
    }


def normalize_master_item(item: dict[str, Any]) -> dict[str, Any]:
    item["createdAt"] = item.pop("created_at")
    item["updatedAt"] = item.pop("updated_at")
    return item


def ensure_status(entity: dict[str, Any], *allowed_statuses: str) -> None:
    if entity["status"] not in allowed_statuses:
        raise ConflictError(f"当前状态不允许执行该操作: {entity['status']}")


def notify_workflow_result(
    connection: sqlite3.Connection,
    *,
    biz_type: str,
    biz_id: str,
    initiator_user_id: str,
    result: str,
) -> None:
    title = f"{biz_type} 审批结果"
    content = f"{biz_type} {biz_id} 审批结果为 {result}"
    create_notification(
        connection,
        receiver_user_id=initiator_user_id,
        title=title,
        content=content,
        biz_ref_type=biz_type,
        biz_ref_id=biz_id,
    )


def workflow_final_status_for(result: str, biz_type: str) -> str:
    if result == STATUS_APPROVED:
        mapping = {
            BIZ_PROCUREMENT_REQUEST: STATUS_APPROVED,
            BIZ_CONTRACT: STATUS_EFFECTIVE,
            BIZ_EXPENSE: STATUS_APPROVED,
        }
        return mapping.get(biz_type, STATUS_COMPLETED)
    if result == STATUS_REJECTED:
        return STATUS_REJECTED
    return STATUS_PENDING
