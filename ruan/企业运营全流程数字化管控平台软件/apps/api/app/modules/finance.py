"""Budget, expense, payment, and receipt endpoints."""

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
    reserve_budget,
    save_idempotent_response,
    validate_budget,
)
from .constants import BIZ_EXPENSE, STATUS_APPROVED, STATUS_COMPLETED, STATUS_OPEN, STATUS_PENDING
from .workflows import create_workflow_instance


def _list_budgets(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    sql, params = build_list_sql(
        "budgets",
        keyword_columns=["budget_key"],
        extra_filters={"orgUnitId": "org_unit_id", "costCenterId": "cost_center_id", "status": "status"},
        query=context.query,
    )
    return page_from_sql(context.db, sql=sql, params=params, query=context.query, request_id=context.request_id)


def _create_budget(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    require_fields(
        context.body,
        "budgetYear",
        "budgetMonth",
        "orgUnitId",
        "costCenterId",
        "budgetAmount",
        "budgetKey",
    )
    budget_id = generate_id("budget")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO budgets(
            id, budget_year, budget_month, org_unit_id, project_id, cost_center_id,
            budget_key, budget_amount, used_amount, warning_amount, control_mode, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            budget_id,
            int(context.body["budgetYear"]),
            int(context.body["budgetMonth"]),
            context.body["orgUnitId"],
            context.body.get("projectId"),
            context.body["costCenterId"],
            context.body["budgetKey"],
            float(context.body["budgetAmount"]),
            float(context.body.get("warningAmount", 0)),
            context.body.get("controlMode", "HARD"),
            context.body.get("status", "ACTIVE"),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="BUDGET_CREATED",
        biz_type="BUDGET",
        biz_id=budget_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response({"budgetId": budget_id}, context.request_id, status_code=201)


def _create_expense_claim(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    require_fields(
        context.body,
        "claimUserId",
        "costCenterId",
        "amountTotal",
        "expenseType",
        "budgetKey",
    )
    budget_result = validate_budget(context.db, context.body["budgetKey"], float(context.body["amountTotal"]))
    reserve_budget(context.db, context.body["budgetKey"], float(context.body["amountTotal"]))
    claim_id = generate_id("claim")
    claim_no = generate_document_no("EC")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO expense_claims(
            id, claim_no, claim_user_id, cost_center_id, project_id, amount_total, expense_type,
            attachments_json, budget_key, budget_check_result, workflow_instance_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?, 1)
        """,
        (
            claim_id,
            claim_no,
            context.body["claimUserId"],
            context.body["costCenterId"],
            context.body.get("projectId"),
            float(context.body["amountTotal"]),
            context.body["expenseType"],
            json_dumps(context.body.get("attachments", [])),
            context.body["budgetKey"],
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
        biz_type=BIZ_EXPENSE,
        biz_id=claim_id,
        title=f"费用报销审批 {claim_no}",
        payload={
            "claimUserId": context.body["claimUserId"],
            "costCenterId": context.body["costCenterId"],
            "amountTotal": float(context.body["amountTotal"]),
            "budgetKey": context.body["budgetKey"],
        },
        initiator_user_id=context.user["id"],
        request_id=context.request_id,
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="EXPENSE_CLAIM_CREATED",
        biz_type="EXPENSE_CLAIM",
        biz_id=claim_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response(
        {
            "claimId": claim_id,
            "claimNo": claim_no,
            "status": STATUS_PENDING,
            "budgetCheckResult": budget_result,
            "workflowInstanceId": workflow["instanceId"],
        },
        context.request_id,
        status_code=201,
    )


def _list_expenses(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    sql, params = build_list_sql(
        "expense_claims",
        keyword_columns=["claim_no", "expense_type"],
        extra_filters={"status": "status", "claimUserId": "claim_user_id"},
        query=context.query,
    )

    def transform(item: dict[str, Any]) -> dict[str, Any]:
        item["attachments"] = json_loads(item.pop("attachments_json"), [])
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


def _validate_payment_source(connection: Any, source_type: str, source_id: str) -> dict[str, Any]:
    mapping = {
        "CONTRACT": "contracts",
        "PURCHASE_ORDER": "purchase_orders",
        "EXPENSE_CLAIM": "expense_claims",
    }
    if source_type not in mapping:
        raise ValidationError(f"不支持的付款来源类型: {source_type}")
    return get_entity(connection, mapping[source_type], source_id)


def _create_payment_request(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    require_fields(context.body, "sourceType", "sourceId", "payeeName", "amountTotal", "plannedDate")
    idem_key = context.header("idempotency-key")
    cached = load_idempotent_response(context.db, idem_key, context.path)
    if cached is not None:
        return json_response(cached, context.request_id)
    _validate_payment_source(context.db, context.body["sourceType"], context.body["sourceId"])
    payment_id = generate_id("pay")
    payment_no = generate_document_no("PAY")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO payment_requests(
            id, payment_no, source_type, source_id, payee_name, amount_total, planned_date, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            payment_id,
            payment_no,
            context.body["sourceType"],
            context.body["sourceId"],
            context.body["payeeName"],
            float(context.body["amountTotal"]),
            context.body["plannedDate"],
            STATUS_OPEN,
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    response = {"paymentId": payment_id, "paymentNo": payment_no, "status": STATUS_OPEN}
    save_idempotent_response(context.db, idem_key or payment_id, context.path, response)
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="PAYMENT_REQUEST_CREATED",
        biz_type="PAYMENT_REQUEST",
        biz_id=payment_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response(response, context.request_id, status_code=201)


def _list_payment_requests(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    sql, params = build_list_sql(
        "payment_requests",
        keyword_columns=["payment_no", "payee_name"],
        extra_filters={"status": "status", "sourceType": "source_type"},
        query=context.query,
    )
    return page_from_sql(context.db, sql=sql, params=params, query=context.query, request_id=context.request_id)


def _create_receipt_record(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    require_fields(context.body, "contractId", "amount", "receiptDate", "method")
    contract = get_entity(context.db, "contracts", context.body["contractId"])
    receipt_id = generate_id("receipt")
    receipt_no = generate_document_no("REC")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO receipt_records(
            id, receipt_no, contract_id, amount, receipt_date, method, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, 1)
        """,
        (
            receipt_id,
            receipt_no,
            contract["id"],
            float(context.body["amount"]),
            context.body["receiptDate"],
            context.body["method"],
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    total_row = context.db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total_amount FROM receipt_records WHERE contract_id = ?",
        (contract["id"],),
    ).fetchone()
    total_amount = float(total_row["total_amount"])
    progress = min(round(total_amount / float(contract["amount_total"]) * 100, 2), 100.0)
    contract_status = STATUS_COMPLETED if progress >= 100 else "EXECUTING"
    context.db.execute(
        """
        UPDATE contracts
        SET receipt_progress = ?, status = ?, updated_at = ?, updated_by = ?, version = version + 1
        WHERE id = ?
        """,
        (progress, contract_status, now, context.user["id"], contract["id"]),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="RECEIPT_REGISTERED",
        biz_type="CONTRACT",
        biz_id=contract["id"],
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response(
        {"receiptId": receipt_id, "contractReceiptProgress": progress},
        context.request_id,
        status_code=201,
    )


def _list_receipts(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "finance.manage")
    sql, params = build_list_sql(
        "receipt_records",
        keyword_columns=["receipt_no", "method"],
        extra_filters={"contractId": "contract_id"},
        query=context.query,
    )
    return page_from_sql(context.db, sql=sql, params=params, query=context.query, request_id=context.request_id)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/finance/budgets", _list_budgets)
    router.add("POST", "/api/v1/finance/budgets", _create_budget)
    router.add("POST", "/api/v1/finance/expenses", _create_expense_claim)
    router.add("GET", "/api/v1/finance/expenses", _list_expenses)
    router.add("POST", "/api/v1/finance/payment-requests", _create_payment_request)
    router.add("GET", "/api/v1/finance/payment-requests", _list_payment_requests)
    router.add("POST", "/api/v1/finance/receipts", _create_receipt_record)
    router.add("GET", "/api/v1/finance/receipts", _list_receipts)
