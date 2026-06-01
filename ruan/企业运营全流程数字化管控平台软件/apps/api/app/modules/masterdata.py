"""Master data endpoints."""

from __future__ import annotations

from typing import Any

from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    audit_log,
    build_list_sql,
    ensure_unique_code,
    generate_id,
    normalize_master_item,
    page_from_sql,
    require_fields,
    require_permission,
)
from .constants import STATUS_ACTIVE


def _list_factory(
    table: str,
    keyword_columns: list[str],
    extra_filters: dict[str, str] | None = None,
) -> Any:
    def handler(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
        require_permission(context.db, context.user, "masterdata.manage")
        sql, params = build_list_sql(
            table,
            keyword_columns=keyword_columns,
            extra_filters=extra_filters,
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

    return handler


def _create_customer(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(context.body, "code", "name")
    ensure_unique_code(context.db, "customers", context.body["code"])
    now = iso_now()
    customer_id = generate_id("cust")
    context.db.execute(
        """
        INSERT INTO customers(
            id, code, name, industry, owner_user_id, contact_name, contact_phone, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            customer_id,
            context.body["code"],
            context.body["name"],
            context.body.get("industry"),
            context.body.get("ownerUserId"),
            context.body.get("contactName"),
            context.body.get("contactPhone"),
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
        action_type="CUSTOMER_CREATED",
        biz_type="CUSTOMER",
        biz_id=customer_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"customerId": customer_id}, context.request_id, status_code=201)


def _create_supplier(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(context.body, "code", "name")
    ensure_unique_code(context.db, "suppliers", context.body["code"])
    now = iso_now()
    supplier_id = generate_id("sup")
    context.db.execute(
        """
        INSERT INTO suppliers(
            id, code, name, category, rating, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            supplier_id,
            context.body["code"],
            context.body["name"],
            context.body.get("category"),
            int(context.body.get("rating", 3)),
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
        action_type="SUPPLIER_CREATED",
        biz_type="SUPPLIER",
        biz_id=supplier_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"supplierId": supplier_id}, context.request_id, status_code=201)


def _create_item(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(context.body, "code", "name", "itemType", "uom")
    ensure_unique_code(context.db, "item_master", context.body["code"])
    now = iso_now()
    item_id = generate_id("item")
    context.db.execute(
        """
        INSERT INTO item_master(
            id, code, name, item_type, uom, safety_stock, unit_price, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            item_id,
            context.body["code"],
            context.body["name"],
            context.body["itemType"],
            context.body["uom"],
            float(context.body.get("safetyStock", 0)),
            float(context.body.get("unitPrice", 0)),
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
        action_type="ITEM_CREATED",
        biz_type="ITEM_MASTER",
        biz_id=item_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"itemId": item_id}, context.request_id, status_code=201)


def _create_project(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(context.body, "code", "name", "ownerOrgId")
    ensure_unique_code(context.db, "projects", context.body["code"])
    now = iso_now()
    project_id = generate_id("proj")
    context.db.execute(
        """
        INSERT INTO projects(
            id, code, name, owner_org_id, start_date, end_date, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            project_id,
            context.body["code"],
            context.body["name"],
            context.body["ownerOrgId"],
            context.body.get("startDate"),
            context.body.get("endDate"),
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
        action_type="PROJECT_CREATED",
        biz_type="PROJECT",
        biz_id=project_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"projectId": project_id}, context.request_id, status_code=201)


def _create_warehouse(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(context.body, "code", "name", "orgUnitId")
    ensure_unique_code(context.db, "warehouses", context.body["code"])
    now = iso_now()
    warehouse_id = generate_id("wh")
    context.db.execute(
        """
        INSERT INTO warehouses(
            id, code, name, org_unit_id, location, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            warehouse_id,
            context.body["code"],
            context.body["name"],
            context.body["orgUnitId"],
            context.body.get("location"),
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
        action_type="WAREHOUSE_CREATED",
        biz_type="WAREHOUSE",
        biz_id=warehouse_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"warehouseId": warehouse_id}, context.request_id, status_code=201)


def _summary(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    tables = {
        "customers": "customers",
        "suppliers": "suppliers",
        "items": "item_master",
        "projects": "projects",
        "warehouses": "warehouses",
    }
    summary = {}
    for key, table_name in tables.items():
        total = context.db.execute(
            f"SELECT COUNT(1) AS total FROM {table_name} WHERE status = 'ACTIVE'"
        ).fetchone()["total"]
        summary[key] = total
    return json_response(summary, context.request_id)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/customers", _list_factory("customers", ["code", "name"], {"status": "status"}))
    router.add("POST", "/api/v1/customers", _create_customer)
    router.add("GET", "/api/v1/suppliers", _list_factory("suppliers", ["code", "name"], {"status": "status"}))
    router.add("POST", "/api/v1/suppliers", _create_supplier)
    router.add("GET", "/api/v1/items", _list_factory("item_master", ["code", "name"], {"status": "status", "itemType": "item_type"}))
    router.add("POST", "/api/v1/items", _create_item)
    router.add("GET", "/api/v1/projects", _list_factory("projects", ["code", "name"], {"status": "status", "ownerOrgId": "owner_org_id"}))
    router.add("POST", "/api/v1/projects", _create_project)
    router.add("GET", "/api/v1/warehouses", _list_factory("warehouses", ["code", "name"], {"status": "status", "orgUnitId": "org_unit_id"}))
    router.add("POST", "/api/v1/warehouses", _create_warehouse)
    router.add("GET", "/api/v1/masterdata/summary", _summary)
