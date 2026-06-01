"""End-to-end integration tests using the built-in WSGI server."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib import error, request
from wsgiref.simple_server import make_server


TEST_TEMP_DIR = tempfile.mkdtemp(prefix="ops-platform-tests-")
TEST_DB_PATH = str(Path(TEST_TEMP_DIR) / "test.sqlite3")
os.environ["APP_DATABASE_PATH"] = TEST_DB_PATH

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from app.core.seed import seed_database  # noqa: E402
from app.main import create_application  # noqa: E402


class OpsPlatformIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        seed_database(force=True)
        cls.httpd = make_server("127.0.0.1", 0, create_application())
        cls.base_url = f"http://127.0.0.1:{cls.httpd.server_port}"
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.httpd.shutdown()
        cls.thread.join(timeout=2)

    def setUp(self) -> None:
        seed_database(force=True)

    def api_request(self, method: str, path: str, payload: dict | None = None, headers: dict | None = None) -> tuple[int, dict]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request_headers = {"Content-Type": "application/json", **(headers or {})}
        req = request.Request(f"{self.base_url}{path}", data=data, method=method, headers=request_headers)
        try:
            with request.urlopen(req, timeout=10) as response:
                body = response.read().decode("utf-8")
                return response.getcode(), json.loads(body)
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            return exc.code, json.loads(body)

    def login(self, username: str, password: str = "admin123") -> dict:
        status, payload = self.api_request("POST", "/api/v1/auth/login", {"username": username, "password": password})
        self.assertEqual(status, 200, payload)
        return payload["data"]

    def auth_headers(self, username: str) -> dict:
        session = self.login(username)
        return {"Authorization": f"Bearer {session['accessToken']}"}

    def db(self) -> sqlite3.Connection:
        connection = sqlite3.connect(TEST_DB_PATH)
        connection.row_factory = sqlite3.Row
        return connection

    def find_open_task(self, biz_id: str, username: str) -> dict:
        headers = self.auth_headers(username)
        status, payload = self.api_request("GET", "/api/v1/approvals/tasks?view=todo", headers=headers)
        self.assertEqual(status, 200, payload)
        for item in payload["data"]:
            if item["biz_id"] == biz_id:
                return item
        self.fail(f"open task for {biz_id} not found")

    def test_root_serves_frontend_shell(self) -> None:
        with request.urlopen(f"{self.base_url}/", timeout=10) as response:
            html = response.read().decode("utf-8")
        self.assertIn("企业运营全流程数字化管控平台", html)
        self.assertIn("/src/app.js", html)

    def test_login_and_me(self) -> None:
        session = self.login("admin")
        status, payload = self.api_request(
            "GET",
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {session['accessToken']}"},
        )
        self.assertEqual(status, 200, payload)
        self.assertEqual(payload["data"]["user"]["username"], "admin")
        self.assertIn("iam.manage", payload["data"]["permissions"])

    def test_permission_denied_for_sales_on_audit_logs(self) -> None:
        status, payload = self.api_request("GET", "/api/v1/audit-logs", headers=self.auth_headers("sales01"))
        self.assertEqual(status, 403, payload)
        self.assertEqual(payload["code"], "AUTH_403_01")

    def test_procurement_to_inventory_flow(self) -> None:
        with self.db() as connection:
            budget = connection.execute("SELECT * FROM budgets ORDER BY created_at LIMIT 1").fetchone()
            item = connection.execute("SELECT * FROM item_master ORDER BY created_at LIMIT 1").fetchone()
            supplier = connection.execute("SELECT * FROM suppliers ORDER BY created_at LIMIT 1").fetchone()
            warehouse = connection.execute("SELECT * FROM warehouses ORDER BY created_at LIMIT 1").fetchone()
        admin_headers = {
            **self.auth_headers("admin"),
            "Idempotency-Key": "test-procurement-flow-001",
        }
        create_status, create_payload = self.api_request(
            "POST",
            "/api/v1/procurement/requests",
            payload={
                "requestOrgId": budget["org_unit_id"],
                "costCenterId": budget["cost_center_id"],
                "budgetKey": budget["budget_key"],
                "needDate": "2026-11-10",
                "items": [{"itemId": item["id"], "qty": 8, "unitPrice": 220}],
            },
            headers=admin_headers,
        )
        self.assertEqual(create_status, 201, create_payload)
        request_id = create_payload["data"]["requestId"]

        director_task = self.find_open_task(request_id, "director")
        approve_status, approve_payload = self.api_request(
            "POST",
            f"/api/v1/approvals/tasks/{director_task['id']}/actions",
            payload={"action": "APPROVE", "comment": "主管通过"},
            headers=self.auth_headers("director"),
        )
        self.assertEqual(approve_status, 200, approve_payload)

        finance_task = self.find_open_task(request_id, "fin01")
        approve2_status, approve2_payload = self.api_request(
            "POST",
            f"/api/v1/approvals/tasks/{finance_task['id']}/actions",
            payload={"action": "APPROVE", "comment": "财务通过"},
            headers=self.auth_headers("fin01"),
        )
        self.assertEqual(approve2_status, 200, approve2_payload)

        po_status, po_payload = self.api_request(
            "POST",
            "/api/v1/procurement/orders",
            payload={
                "requestId": request_id,
                "supplierId": supplier["id"],
                "expectedReceiptDate": "2026-11-20",
            },
            headers=self.auth_headers("admin"),
        )
        self.assertEqual(po_status, 201, po_payload)
        po_id = po_payload["data"]["poId"]

        receipt_status, receipt_payload = self.api_request(
            "POST",
            "/api/v1/inventory/receipts",
            payload={
                "purchaseOrderId": po_id,
                "warehouseId": warehouse["id"],
                "items": [{"itemId": item["id"], "qty": 8}],
            },
            headers={**self.auth_headers("wh01"), "Idempotency-Key": "receipt-flow-001"},
        )
        self.assertEqual(receipt_status, 201, receipt_payload)
        self.assertTrue(receipt_payload["data"]["receiptTxnIds"])

        with self.db() as connection:
            purchase_order = connection.execute("SELECT * FROM purchase_orders WHERE id = ?", (po_id,)).fetchone()
            self.assertIn(purchase_order["status"], {"PARTIAL", "COMPLETED"})
            balance = connection.execute(
                "SELECT * FROM stock_balances WHERE warehouse_id = ? AND item_id = ?",
                (warehouse["id"], item["id"]),
            ).fetchone()
            self.assertIsNotNone(balance)
            self.assertGreater(balance["qty_on_hand"], 0)

    def test_budget_blocking_for_expense_claim(self) -> None:
        with self.db() as connection:
            budget = connection.execute("SELECT * FROM budgets ORDER BY created_at LIMIT 1").fetchone()
            connection.execute(
                "UPDATE budgets SET used_amount = budget_amount, updated_at = ? WHERE id = ?",
                ("2026-05-12T00:00:00Z", budget["id"]),
            )
            connection.commit()
        status, payload = self.api_request(
            "POST",
            "/api/v1/finance/expenses",
            payload={
                "claimUserId": self.login("sales01")["user"]["id"],
                "costCenterId": budget["cost_center_id"],
                "amountTotal": 3000,
                "expenseType": "TRAVEL",
                "budgetKey": budget["budget_key"],
                "attachments": [{"name": "demo.pdf"}],
            },
            headers=self.auth_headers("admin"),
        )
        self.assertEqual(status, 409, payload)
        self.assertEqual(payload["code"], "BUDGET_409_01")

    def test_contract_and_receipt_flow(self) -> None:
        with self.db() as connection:
            customer = connection.execute("SELECT * FROM customers ORDER BY created_at LIMIT 1").fetchone()
            item = connection.execute("SELECT * FROM item_master ORDER BY created_at LIMIT 1").fetchone()
        create_order_status, create_order_payload = self.api_request(
            "POST",
            "/api/v1/sales/orders",
            payload={
                "customerId": customer["id"],
                "items": [{"itemId": item["id"], "qty": 5, "unitPrice": 600}],
                "amountTotal": 3000,
                "deliveryDate": "2026-11-30",
            },
            headers=self.auth_headers("admin"),
        )
        self.assertEqual(create_order_status, 201, create_order_payload)
        order_id = create_order_payload["data"]["orderId"]

        create_contract_status, create_contract_payload = self.api_request(
            "POST",
            "/api/v1/contracts",
            payload={
                "salesOrderId": order_id,
                "amountTotal": 5000,
                "expireDate": "2026-12-31",
                "attachments": [{"name": "contract.pdf"}],
            },
            headers=self.auth_headers("admin"),
        )
        self.assertEqual(create_contract_status, 201, create_contract_payload)
        contract_id = create_contract_payload["data"]["contractId"]

        director_task = self.find_open_task(contract_id, "director")
        self.api_request(
            "POST",
            f"/api/v1/approvals/tasks/{director_task['id']}/actions",
            payload={"action": "APPROVE", "comment": "业务通过"},
            headers=self.auth_headers("director"),
        )
        finance_task = self.find_open_task(contract_id, "fin01")
        self.api_request(
            "POST",
            f"/api/v1/approvals/tasks/{finance_task['id']}/actions",
            payload={"action": "APPROVE", "comment": "财务通过"},
            headers=self.auth_headers("fin01"),
        )

        receipt_status, receipt_payload = self.api_request(
            "POST",
            "/api/v1/finance/receipts",
            payload={
                "contractId": contract_id,
                "amount": 2600,
                "receiptDate": "2026-12-15",
                "method": "BANK_TRANSFER",
            },
            headers=self.auth_headers("admin"),
        )
        self.assertEqual(receipt_status, 201, receipt_payload)
        self.assertGreater(receipt_payload["data"]["contractReceiptProgress"], 0)

    def test_payment_request_idempotency(self) -> None:
        with self.db() as connection:
            expense = connection.execute(
                "SELECT * FROM expense_claims WHERE status = 'APPROVED' ORDER BY created_at LIMIT 1"
            ).fetchone()
        headers = {**self.auth_headers("admin"), "Idempotency-Key": "payment-repeat-001"}
        payload = {
            "sourceType": "EXPENSE_CLAIM",
            "sourceId": expense["id"],
            "payeeName": "深圳分公司",
            "amountTotal": 2888,
            "plannedDate": "2026-11-18",
        }
        first_status, first_payload = self.api_request(
            "POST",
            "/api/v1/finance/payment-requests",
            payload=payload,
            headers=headers,
        )
        second_status, second_payload = self.api_request(
            "POST",
            "/api/v1/finance/payment-requests",
            payload=payload,
            headers=headers,
        )
        self.assertEqual(first_status, 201, first_payload)
        self.assertEqual(second_status, 200, second_payload)
        self.assertEqual(first_payload["data"]["paymentId"], second_payload["data"]["paymentId"])
