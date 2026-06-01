"""Procurement request and purchase order endpoints."""

from __future__ import annotations

from typing import Any

from ..core.exceptions import ConflictError
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
    load_idempotent_response,
    page_from_sql,
    require_fields,
    require_permission,
    reserve_budget,
    save_idempotent_response,
    validate_budget,
)
from .constants import BIZ_PROCUREMENT_REQUEST, STATUS_APPROVED, STATUS_OPEN, STATUS_PENDING
from .workflows import create_workflow_instance


def _create_procurement_request(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "procurement.manage")
    require_fields(context.body, "requestOrgId", "costCenterId", "budgetKey", "items", "needDate")
    idem_key = context.header("idempotency-key")
    cached = load_idempotent_response(context.db, idem_key, context.path)
    if cached is not None:
        return json_response(cached, context.request_id)
    amount_total = float(context.body.get("amountTotal") or 0)
    if amount_total <= 0:
        amount_total = sum(float(item["qty"]) * float(item["unitPrice"]) for item in context.body["items"])
    budget_result = validate_budget(context.db, context.body["budgetKey"], amount_total)
    reserve_budget(context.db, context.body["budgetKey"], amount_total)
    request_id = generate_id("pr")
    request_no = generate_document_no("PR")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO procurement_requests(
            id, request_no, request_org_id, cost_center_id, project_id, budget_key, amount_total,
            need_date, items_json, budget_check_result, workflow_instance_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 1)
        """,
        (
            request_id,
            request_no,
            context.body["requestOrgId"],
            context.body["costCenterId"],
            context.body.get("projectId"),
            context.body["budgetKey"],
            amount_total,
            context.body["needDate"],
            json_dumps(context.body["items"]),
            json_dumps(budget_result),
            STATUS_PENDING,
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    workflow = create_workflow_instance(
        context.db,
        biz_type=BIZ_PROCUREMENT_REQUEST,
        biz_id=request_id,
        title=f"采购申请审批 {request_no}",
        payload={
            "requestOrgId": context.body["requestOrgId"],
            "amountTotal": amount_total,
            "budgetKey": context.body["budgetKey"],
        },
        initiator_user_id=context.user["id"],
        request_id=context.request_id,
    )
    response = {
        "requestId": request_id,
        "requestNo": request_no,
        "budgetCheckResult": budget_result,
        "workflowInstanceId": workflow["instanceId"],
        "status": STATUS_PENDING,
    }
    save_idempotent_response(context.db, idem_key or request_id, context.path, response)
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PROCUREMENT_REQUEST_CREATED",
        biz_type="PROCUREMENT_REQUEST",
        biz_id=request_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response(response, context.request_id, status_code=201)


def _list_procurement_requests(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "procurement.manage")
    sql, params = build_list_sql(
        "procurement_requests",
        keyword_columns=["request_no", "budget_key"],
        extra_filters={"status": "status", "requestOrgId": "request_org_id"},
        query=context.query,
    )

    def transform(item: dict[str, Any]) -> dict[str, Any]:
        item["items"] = json_loads(item.pop("items_json"), [])
        item["budgetCheckResult"] = json_loads(item.pop("budget_check_result"), {})
        return item

    return page_from_sql(
        context.db,
        sql=sql,
        params=params,
        query=context.query,
        request_id=context.request_id,
        item_transform=transform,
    )


def _create_purchase_order(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "procurement.manage")
    require_fields(context.body, "requestId", "supplierId", "expectedReceiptDate")
    request = get_entity(context.db, "procurement_requests", context.body["requestId"])
    if request["status"] != STATUS_APPROVED:
        raise ConflictError("采购申请尚未审批通过")
    supplier = get_entity(context.db, "suppliers", context.body["supplierId"])
    items = context.body.get("items") or json_loads(request["items_json"], [])
    amount_total = sum(float(item["qty"]) * float(item["unitPrice"]) for item in items)
    po_id = generate_id("po")
    po_no = generate_document_no("PO")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO purchase_orders(
            id, po_no, request_id, supplier_id, amount_total, expected_receipt_date,
            items_json, received_amount, execution_rate, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, 1)
        """,
        (
            po_id,
            po_no,
            request["id"],
            supplier["id"],
            amount_total,
            context.body["expectedReceiptDate"],
            json_dumps(items),
            STATUS_OPEN,
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PURCHASE_ORDER_CREATED",
        biz_type="PURCHASE_ORDER",
        biz_id=po_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"poId": po_id, "poNo": po_no, "status": STATUS_OPEN}, context.request_id, status_code=201)


def _list_purchase_orders(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "procurement.manage")
    sql, params = build_list_sql(
        "purchase_orders",
        keyword_columns=["po_no"],
        extra_filters={"status": "status", "supplierId": "supplier_id", "requestId": "request_id"},
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


def register(router: Any) -> None:
    router.add("POST", "/api/v1/procurement/requests", _create_procurement_request)
    router.add("GET", "/api/v1/procurement/requests", _list_procurement_requests)
    router.add("POST", "/api/v1/procurement/orders", _create_purchase_order)
    router.add("GET", "/api/v1/procurement/orders", _list_purchase_orders)
