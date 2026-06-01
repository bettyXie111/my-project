"""Inventory receipt and stock endpoints."""

from __future__ import annotations

from typing import Any

from ..core.exceptions import ValidationError
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
    save_idempotent_response,
)
from .constants import STATUS_COMPLETED, STATUS_OPEN, STATUS_PARTIAL


def _upsert_stock_balance(connection: Any, warehouse_id: str, item_id: str, qty: float, actor_user_id: str) -> dict[str, Any]:
    existing = connection.execute(
        """
        SELECT * FROM stock_balances
        WHERE warehouse_id = ? AND item_id = ?
        """,
        (warehouse_id, item_id),
    ).fetchone()
    now = iso_now()
    if existing is None:
        balance_id = generate_id("stock")
        connection.execute(
            """
            INSERT INTO stock_balances(
                id, warehouse_id, item_id, qty_on_hand, qty_reserved, status,
                created_at, created_by, updated_at, updated_by, version
            ) VALUES (?, ?, ?, ?, 0, 'ACTIVE', ?, ?, ?, ?, 1)
            """,
            (balance_id, warehouse_id, item_id, qty, now, actor_user_id, now, actor_user_id),
        )
        return {
            "balanceId": balance_id,
            "warehouseId": warehouse_id,
            "itemId": item_id,
            "beforeQty": 0,
            "afterQty": qty,
        }
    balance = {key: existing[key] for key in existing.keys()}
    before_qty = float(balance["qty_on_hand"])
    after_qty = before_qty + qty
    connection.execute(
        """
        UPDATE stock_balances
        SET qty_on_hand = ?, updated_at = ?, updated_by = ?, version = version + 1
        WHERE id = ?
        """,
        (after_qty, now, actor_user_id, balance["id"]),
    )
    return {
        "balanceId": balance["id"],
        "warehouseId": warehouse_id,
        "itemId": item_id,
        "beforeQty": before_qty,
        "afterQty": after_qty,
    }


def _receive_inventory(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "inventory.manage")
    require_fields(context.body, "purchaseOrderId", "warehouseId", "items")
    idem_key = context.header("idempotency-key")
    cached = load_idempotent_response(context.db, idem_key, context.path)
    if cached is not None:
        return json_response(cached, context.request_id)
    purchase_order = get_entity(context.db, "purchase_orders", context.body["purchaseOrderId"])
    warehouse = get_entity(context.db, "warehouses", context.body["warehouseId"])
    po_items = {item["itemId"]: item for item in json_loads(purchase_order["items_json"], [])}
    stock_changes = []
    txn_ids = []
    receipt_amount = 0.0
    now = iso_now()
    for item in context.body["items"]:
        if item["itemId"] not in po_items:
            raise ValidationError(f"物料不在采购订单中: {item['itemId']}")
        qty = float(item["qty"])
        unit_price = float(po_items[item["itemId"]]["unitPrice"])
        receipt_amount += qty * unit_price
        stock_change = _upsert_stock_balance(
            context.db,
            warehouse_id=warehouse["id"],
            item_id=item["itemId"],
            qty=qty,
            actor_user_id=context.user["id"],
        )
        stock_changes.append(stock_change)
        txn_id = generate_id("txn")
        txn_ids.append(txn_id)
        context.db.execute(
            """
            INSERT INTO inventory_txns(
                id, txn_no, warehouse_id, item_id, txn_type, qty,
                biz_ref_type, biz_ref_id, remark, status,
                created_at, created_by, updated_at, updated_by, version
            ) VALUES (?, ?, ?, ?, 'RECEIPT', ?, 'PURCHASE_ORDER', ?, ?, 'ACTIVE', ?, ?, ?, ?, 1)
            """,
            (
                txn_id,
                generate_document_no("IT"),
                warehouse["id"],
                item["itemId"],
                qty,
                purchase_order["id"],
                context.body.get("remark"),
                now,
                context.user["id"],
                now,
                context.user["id"],
            ),
        )
    new_received = float(purchase_order["received_amount"]) + receipt_amount
    execution_rate = min(round(new_received / float(purchase_order["amount_total"]) * 100, 2), 100.0)
    status = STATUS_COMPLETED if execution_rate >= 100 else STATUS_PARTIAL
    context.db.execute(
        """
        UPDATE purchase_orders
        SET received_amount = ?, execution_rate = ?, status = ?, updated_at = ?, updated_by = ?, version = version + 1
        WHERE id = ?
        """,
        (new_received, execution_rate, status, now, context.user["id"], purchase_order["id"]),
    )
    response = {"receiptTxnIds": txn_ids, "stockChanges": stock_changes}
    save_idempotent_response(context.db, idem_key or purchase_order["id"], context.path, response)
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="INVENTORY_RECEIVED",
        biz_type="PURCHASE_ORDER",
        biz_id=purchase_order["id"],
        diff={"warehouseId": warehouse["id"], "items": context.body["items"]},
        request_id=context.request_id,
    )
    return json_response(response, context.request_id, status_code=201)


def _list_balances(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "inventory.manage")
    sql, params = build_list_sql(
        "stock_balances",
        keyword_columns=[],
        extra_filters={"warehouseId": "warehouse_id"},
        query=context.query,
    )
    return page_from_sql(context.db, sql=sql, params=params, query=context.query, request_id=context.request_id)


def _list_transactions(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "inventory.manage")
    sql, params = build_list_sql(
        "inventory_txns",
        keyword_columns=["txn_no", "biz_ref_id"],
        extra_filters={"warehouseId": "warehouse_id", "itemId": "item_id"},
        query=context.query,
    )
    return page_from_sql(context.db, sql=sql, params=params, query=context.query, request_id=context.request_id)


def register(router: Any) -> None:
    router.add("POST", "/api/v1/inventory/receipts", _receive_inventory)
    router.add("GET", "/api/v1/inventory/balances", _list_balances)
    router.add("GET", "/api/v1/inventory/transactions", _list_transactions)
