"""IAM module endpoints."""

from __future__ import annotations

import sqlite3
from typing import Any

from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    audit_log,
    build_list_sql,
    ensure_unique_code,
    generate_id,
    get_entity,
    json_dumps,
    normalize_master_item,
    page_from_sql,
    paginate,
    require_fields,
    require_permission,
)
from .constants import STATUS_ACTIVE


def _list_roles(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "iam.manage")
    rows = context.db.execute("SELECT * FROM roles ORDER BY code").fetchall()
    items = [{key: row[key] for key in row.keys()} for row in rows]
    return json_response(items, context.request_id)


def _list_users(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "iam.manage")
    sql, params = build_list_sql(
        "users",
        keyword_columns=["username", "display_name"],
        extra_filters={"status": "status", "orgUnitId": "org_unit_id"},
        query=context.query,
    )

    def transform(item: dict[str, Any]) -> dict[str, Any]:
        item["roleCodes"] = item.pop("role_codes_json")
        return normalize_master_item(item)

    return page_from_sql(
        context.db,
        sql=sql,
        params=params,
        query=context.query,
        request_id=context.request_id,
        item_transform=transform,
    )


def _list_org_units(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "iam.manage")
    rows = context.db.execute(
        "SELECT * FROM org_units ORDER BY parent_id, created_at"
    ).fetchall()
    items = [{key: row[key] for key in row.keys()} for row in rows]
    return json_response(items, context.request_id)


def _create_org_unit(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "iam.manage")
    require_fields(context.body, "name", "unitType")
    now = iso_now()
    org_id = generate_id("org")
    context.db.execute(
        """
        INSERT INTO org_units(
            id, parent_id, name, unit_type, manager_user_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            org_id,
            context.body.get("parentId"),
            context.body["name"],
            context.body["unitType"],
            context.body.get("managerUserId"),
            context.body.get("status", STATUS_ACTIVE),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="ORG_CREATED",
        biz_type="ORG_UNIT",
        biz_id=org_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"orgUnitId": org_id, "status": context.body.get("status", STATUS_ACTIVE)}, context.request_id, status_code=201)


def _list_cost_centers(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "iam.manage")
    sql, params = build_list_sql(
        "cost_centers",
        keyword_columns=["code", "name"],
        extra_filters={"orgUnitId": "org_unit_id", "status": "status"},
        query=context.query,
    )
    return page_from_sql(
        context.db,
        sql=sql,
        params=params,
        query=context.query,
        request_id=context.request_id,
        item_transform=normalize_master_item,
    )


def _create_cost_center(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "iam.manage")
    require_fields(context.body, "code", "name", "orgUnitId")
    ensure_unique_code(context.db, "cost_centers", context.body["code"])
    now = iso_now()
    cost_center_id = generate_id("cc")
    context.db.execute(
        """
        INSERT INTO cost_centers(
            id, code, name, org_unit_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            cost_center_id,
            context.body["code"],
            context.body["name"],
            context.body["orgUnitId"],
            context.body.get("status", STATUS_ACTIVE),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="COST_CENTER_CREATED",
        biz_type="COST_CENTER",
        biz_id=cost_center_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"costCenterId": cost_center_id}, context.request_id, status_code=201)


def _list_configs(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "config.manage")
    rows = context.db.execute("SELECT * FROM system_configs ORDER BY config_key").fetchall()
    items = [{key: row[key] for key in row.keys()} for row in rows]
    return json_response(items, context.request_id)


def _upsert_config(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "config.manage")
    require_fields(context.body, "configKey", "configValue")
    now = iso_now()
    existing = context.db.execute(
        "SELECT id FROM system_configs WHERE config_key = ?",
        (context.body["configKey"],),
    ).fetchone()
    if existing is None:
        config_id = generate_id("cfg")
        context.db.execute(
            """
            INSERT INTO system_configs(
                id, config_key, config_value, description, status,
                created_at, created_by, updated_at, updated_by, version
            ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, 1)
            """,
            (
                config_id,
                context.body["configKey"],
                context.body["configValue"],
                context.body.get("description"),
                now,
                context.user["id"],
                now,
                context.user["id"],
            ),
        )
    else:
        config_id = existing["id"]
        context.db.execute(
            """
            UPDATE system_configs
            SET config_value = ?, description = ?, updated_at = ?, updated_by = ?, version = version + 1
            WHERE id = ?
            """,
            (
                context.body["configValue"],
                context.body.get("description"),
                now,
                context.user["id"],
                config_id,
            ),
        )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="CONFIG_UPSERT",
        biz_type="SYSTEM_CONFIG",
        biz_id=config_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"configId": config_id}, context.request_id, status_code=201)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/roles", _list_roles)
    router.add("GET", "/api/v1/users", _list_users)
    router.add("GET", "/api/v1/org-units", _list_org_units)
    router.add("POST", "/api/v1/org-units", _create_org_unit)
    router.add("GET", "/api/v1/cost-centers", _list_cost_centers)
    router.add("POST", "/api/v1/cost-centers", _create_cost_center)
    router.add("GET", "/api/v1/system/configs", _list_configs)
    router.add("POST", "/api/v1/system/configs", _upsert_config)
