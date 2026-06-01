"""Sales order and contract endpoints."""

from __future__ import annotations

from typing import Any

from ..core.exceptions import ConflictError, ValidationError
from ..core.responses import json_response
from ..core.security import iso_now
from .common import (
    audit_log,
    build_list_sql,
    generate_document_no,
    generate_id,
    get_entity,
    json_dumps,
    json_loads,
    page_from_sql,
    require_fields,
    require_permission,
)
from .constants import BIZ_CONTRACT, STATUS_DRAFT, STATUS_PENDING
from .workflows import create_workflow_instance


def _create_sales_order(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "sales.manage")
    require_fields(context.body, "customerId", "items", "amountTotal", "deliveryDate")
    customer = get_entity(context.db, "customers", context.body["customerId"])
    if customer["status"] != "ACTIVE":
        raise ValidationError("客户已停用")
    order_id = generate_id("so")
    order_no = generate_document_no("SO")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO sales_orders(
            id, order_no, customer_id, amount_total, currency, delivery_date, remark, items_json,
            workflow_instance_id, status, created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 1)
        """,
        (
            order_id,
            order_no,
            context.body["customerId"],
            float(context.body["amountTotal"]),
            context.body.get("currency", "CNY"),
            context.body["deliveryDate"],
            context.body.get("remark"),
            json_dumps(context.body["items"]),
            context.body.get("status", STATUS_DRAFT),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="SALES_ORDER_CREATED",
        biz_type="SALES_ORDER",
        biz_id=order_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"orderId": order_id, "orderNo": order_no, "status": context.body.get("status", STATUS_DRAFT)}, context.request_id, status_code=201)


def _list_sales_orders(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "sales.manage")
    sql, params = build_list_sql(
        "sales_orders",
        keyword_columns=["order_no", "remark"],
        extra_filters={"status": "status", "customerId": "customer_id"},
        query=context.query,
    )

    def transform(item: dict[str, Any]) -> dict[str, Any]:
        item["items"] = json_loads(item.pop("items_json"), [])
        return item

    return page_from_sql(
        context.db,
        sql=sql,
        params=params,
        query=context.query,
        request_id=context.request_id,
        item_transform=transform,
    )


def _create_contract(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "contract.manage")
    require_fields(context.body, "salesOrderId", "amountTotal", "expireDate")
    sales_order = get_entity(context.db, "sales_orders", context.body["salesOrderId"])
    contract_no = context.body.get("contractNo") or generate_document_no("CT")
    existing = context.db.execute(
        "SELECT id FROM contracts WHERE contract_no = ?",
        (contract_no,),
    ).fetchone()
    if existing is not None:
        raise ConflictError("合同编号已存在")
    contract_id = generate_id("ct")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO contracts(
            id, contract_no, sales_order_id, amount_total, version_no, effective_date, expire_date,
            receipt_progress, attachments_json, workflow_instance_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, 1, NULL, ?, 0, ?, NULL, ?, ?, ?, ?, ?, 1)
        """,
        (
            contract_id,
            contract_no,
            sales_order["id"],
            float(context.body["amountTotal"]),
            context.body["expireDate"],
            json_dumps(context.body.get("attachments", [])),
            STATUS_PENDING,
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    workflow_result = create_workflow_instance(
        context.db,
        biz_type=BIZ_CONTRACT,
        biz_id=contract_id,
        title=f"合同审批 {contract_no}",
        payload={
            "salesOrderId": sales_order["id"],
            "amountTotal": float(context.body["amountTotal"]),
            "expireDate": context.body["expireDate"],
        },
        initiator_user_id=context.user["id"],
        request_id=context.request_id,
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="CONTRACT_CREATED",
        biz_type="CONTRACT",
        biz_id=contract_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response(
        {
            "contractId": contract_id,
            "status": STATUS_PENDING,
            "versionNo": 1,
            "contractNo": contract_no,
            "workflowInstanceId": workflow_result["instanceId"],
        },
        context.request_id,
        status_code=201,
    )


def _list_contracts(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "contract.manage")
    sql, params = build_list_sql(
        "contracts",
        keyword_columns=["contract_no"],
        extra_filters={"status": "status", "salesOrderId": "sales_order_id"},
        query=context.query,
    )

    def transform(item: dict[str, Any]) -> dict[str, Any]:
        item["attachments"] = json_loads(item.pop("attachments_json"), [])
        return item

    return page_from_sql(
        context.db,
        sql=sql,
        params=params,
        query=context.query,
        request_id=context.request_id,
        item_transform=transform,
    )


def register(router: Any) -> None:
    router.add("POST", "/api/v1/sales/orders", _create_sales_order)
    router.add("GET", "/api/v1/sales/orders", _list_sales_orders)
    router.add("POST", "/api/v1/contracts", _create_contract)
    router.add("GET", "/api/v1/contracts", _list_contracts)
