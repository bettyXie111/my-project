"""Dashboard aggregation endpoint."""

from __future__ import annotations

from typing import Any

from ..core.responses import json_response
from .common import require_permission


def _scalar(connection: Any, sql: str, params: tuple[Any, ...] = ()) -> Any:
    return connection.execute(sql, params).fetchone()[0]


def _operations_dashboard(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "dashboard.view")
    sales_kpi = {
        "orderCount": _scalar(context.db, "SELECT COUNT(1) FROM sales_orders"),
        "orderAmount": round(float(_scalar(context.db, "SELECT COALESCE(SUM(amount_total), 0) FROM sales_orders")), 2),
        "contractCount": _scalar(context.db, "SELECT COUNT(1) FROM contracts"),
        "effectiveContractCount": _scalar(context.db, "SELECT COUNT(1) FROM contracts WHERE status IN ('EFFECTIVE', 'EXECUTING', 'COMPLETED')"),
    }
    procurement_kpi = {
        "requestCount": _scalar(context.db, "SELECT COUNT(1) FROM procurement_requests"),
        "pendingRequestCount": _scalar(context.db, "SELECT COUNT(1) FROM procurement_requests WHERE status = 'PENDING_APPROVAL'"),
        "poCount": _scalar(context.db, "SELECT COUNT(1) FROM purchase_orders"),
        "poAmount": round(float(_scalar(context.db, "SELECT COALESCE(SUM(amount_total), 0) FROM purchase_orders")), 2),
    }
    inventory_kpi = {
        "warehouseCount": _scalar(context.db, "SELECT COUNT(1) FROM warehouses WHERE status = 'ACTIVE'"),
        "stockSkuCount": _scalar(context.db, "SELECT COUNT(1) FROM stock_balances"),
        "stockQty": round(float(_scalar(context.db, "SELECT COALESCE(SUM(qty_on_hand), 0) FROM stock_balances")), 2),
        "receiptTxnCount": _scalar(context.db, "SELECT COUNT(1) FROM inventory_txns WHERE txn_type = 'RECEIPT'"),
    }
    expense_kpi = {
        "claimCount": _scalar(context.db, "SELECT COUNT(1) FROM expense_claims"),
        "claimAmount": round(float(_scalar(context.db, "SELECT COALESCE(SUM(amount_total), 0) FROM expense_claims")), 2),
        "paymentCount": _scalar(context.db, "SELECT COUNT(1) FROM payment_requests"),
        "receiptAmount": round(float(_scalar(context.db, "SELECT COALESCE(SUM(amount), 0) FROM receipt_records")), 2),
    }
    todo_kpi = {
        "todoCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM approval_tasks WHERE assignee_user_id = ? AND status = 'OPEN'",
            (context.user["id"],),
        ),
        "doneCount": _scalar(
            context.db,
            "SELECT COUNT(1) FROM approval_tasks WHERE assignee_user_id = ? AND status = 'DONE'",
            (context.user["id"],),
        ),
        "unreadNotifications": _scalar(
            context.db,
            "SELECT COUNT(1) FROM notifications WHERE receiver_user_id = ? AND read_at IS NULL",
            (context.user["id"],),
        ),
    }
    alerts = []
    contract_rows = context.db.execute(
        """
        SELECT contract_no, expire_date FROM contracts
        WHERE status IN ('EFFECTIVE', 'EXECUTING') ORDER BY expire_date ASC LIMIT 5
        """
    ).fetchall()
    for row in contract_rows:
        alerts.append({"type": "CONTRACT_EXPIRE", "label": row["contract_no"], "value": row["expire_date"]})
    stock_rows = context.db.execute(
        """
        SELECT b.item_id, b.qty_on_hand, i.safety_stock
        FROM stock_balances b
        JOIN item_master i ON i.id = b.item_id
        WHERE b.qty_on_hand < i.safety_stock
        LIMIT 5
        """
    ).fetchall()
    for row in stock_rows:
        alerts.append(
            {
                "type": "LOW_STOCK",
                "label": row["item_id"],
                "value": f"{row['qty_on_hand']}/{row['safety_stock']}",
            }
        )
    return json_response(
        {
            "salesKpi": sales_kpi,
            "procurementKpi": procurement_kpi,
            "inventoryKpi": inventory_kpi,
            "expenseKpi": expense_kpi,
            "todoKpi": todo_kpi,
            "alerts": alerts,
        },
        context.request_id,
    )


def register(router: Any) -> None:
    router.add("GET", "/api/v1/dashboard/operations", _operations_dashboard)
