"""End-to-end integration tests for the performance platform."""

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


TEST_TEMP_DIR = tempfile.mkdtemp(prefix="performance-platform-tests-")
TEST_DB_PATH = str(Path(TEST_TEMP_DIR) / "test.sqlite3")
os.environ["APP_DATABASE_PATH"] = TEST_DB_PATH

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from app.core.seed import seed_database  # noqa: E402
from app.main import create_application  # noqa: E402


SCORE_CODES = [
    "KPI-DELIVERY",
    "KPI-COLLAB",
    "KPI-QUALITY",
    "KPI-INNOVATION",
    "KPI-CUSTOMER",
]


def score_payload(base_score: int, comment_prefix: str) -> list[dict]:
    return [
        {"code": code, "score": base_score + offset, "comment": f"{comment_prefix}-{code}"}
        for offset, code in enumerate(SCORE_CODES)
    ]


class PerformancePlatformIntegrationTests(unittest.TestCase):
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
        self.assertIn("多维度绩效评价与智能分析系统", html)
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
        self.assertIn("performance.plan.manage", payload["data"]["permissions"])

    def test_permission_denied_for_employee_on_audit_logs(self) -> None:
        status, payload = self.api_request("GET", "/api/v1/audit-logs", headers=self.auth_headers("sales01"))
        self.assertEqual(status, 403, payload)
        self.assertEqual(payload["code"], "AUTH_403_01")

    def test_plan_review_flow(self) -> None:
        admin_headers = self.auth_headers("admin")
        with self.db() as connection:
            sales_user = connection.execute("SELECT * FROM users WHERE username = 'sales01'").fetchone()
            manager_user = connection.execute("SELECT * FROM users WHERE username = 'fin01'").fetchone()

        create_cycle_status, create_cycle_payload = self.api_request(
            "POST",
            "/api/v1/performance/cycles",
            payload={
                "cycleCode": "2026FLOW",
                "cycleName": "2026 流程验证周期",
                "periodType": "SPECIAL",
                "startDate": "2026-08-01",
                "endDate": "2026-08-31",
                "selfReviewDeadline": "2026-09-03",
                "managerReviewDeadline": "2026-09-08",
            },
            headers=admin_headers,
        )
        self.assertEqual(create_cycle_status, 201, create_cycle_payload)
        cycle_id = create_cycle_payload["data"]["cycleId"]

        create_plan_status, create_plan_payload = self.api_request(
            "POST",
            "/api/v1/performance/plans",
            payload={
                "cycleId": cycle_id,
                "employeeUserId": sales_user["id"],
                "managerUserId": manager_user["id"],
                "orgUnitId": sales_user["org_unit_id"],
                "title": "销售团队 8 月绩效计划",
            },
            headers=admin_headers,
        )
        self.assertEqual(create_plan_status, 201, create_plan_payload)
        plan_id = create_plan_payload["data"]["planId"]

        submit_status, submit_payload = self.api_request(
            "POST",
            f"/api/v1/performance/plans/{plan_id}/submit",
            payload={},
            headers=admin_headers,
        )
        self.assertEqual(submit_status, 201, submit_payload)

        director_task = self.find_open_task(plan_id, "director")
        director_approve_status, director_approve_payload = self.api_request(
            "POST",
            f"/api/v1/approvals/tasks/{director_task['id']}/actions",
            payload={"action": "APPROVE", "comment": "绩效负责人通过"},
            headers=self.auth_headers("director"),
        )
        self.assertEqual(director_approve_status, 200, director_approve_payload)

        manager_task = self.find_open_task(plan_id, "fin01")
        manager_approve_status, manager_approve_payload = self.api_request(
            "POST",
            f"/api/v1/approvals/tasks/{manager_task['id']}/actions",
            payload={"action": "APPROVE", "comment": "直属经理确认通过"},
            headers=self.auth_headers("fin01"),
        )
        self.assertEqual(manager_approve_status, 200, manager_approve_payload)

        self_review_status, self_review_payload = self.api_request(
            "POST",
            f"/api/v1/performance/plans/{plan_id}/self-review",
            payload={
                "summary": "本周期按时完成销售线索转化和客户复盘工作。",
                "scores": score_payload(84, "self"),
            },
            headers=self.auth_headers("sales01"),
        )
        self.assertEqual(self_review_status, 200, self_review_payload)

        manager_review_status, manager_review_payload = self.api_request(
            "POST",
            f"/api/v1/performance/plans/{plan_id}/manager-review",
            payload={
                "summary": "本周期执行节奏稳定，可继续提升跨团队协作效率。",
                "scores": score_payload(88, "manager"),
            },
            headers=self.auth_headers("fin01"),
        )
        self.assertEqual(manager_review_status, 200, manager_review_payload)
        self.assertGreater(manager_review_payload["data"]["totalScore"], 0)
        self.assertIn(manager_review_payload["data"]["grade"], {"A", "B"})

        with self.db() as connection:
            plan_row = connection.execute("SELECT * FROM performance_plans WHERE id = ?", (plan_id,)).fetchone()
            self.assertEqual(plan_row["status"], "COMPLETED")
            self.assertIsNotNone(plan_row["manager_review_json"])

    def test_create_improvement_action_for_completed_plan(self) -> None:
        admin_headers = self.auth_headers("admin")
        with self.db() as connection:
            low_plan = connection.execute(
                "SELECT * FROM performance_plans WHERE status = 'COMPLETED' AND total_score < 75 ORDER BY created_at LIMIT 1"
            ).fetchone()
            owner_user = connection.execute("SELECT * FROM users WHERE username = 'proc01'").fetchone()
            sponsor_user = connection.execute("SELECT * FROM users WHERE username = 'director'").fetchone()

        create_status, create_payload = self.api_request(
            "POST",
            "/api/v1/performance/improvement-actions",
            payload={
                "planId": low_plan["id"],
                "ownerUserId": owner_user["id"],
                "sponsorUserId": sponsor_user["id"],
                "dueDate": "2026-08-15",
                "actionTitle": "低分项辅导行动",
                "actionDetail": "围绕协同与创新两个低分指标建立双周辅导机制。",
            },
            headers=admin_headers,
        )
        self.assertEqual(create_status, 201, create_payload)

        list_status, list_payload = self.api_request(
            "GET",
            "/api/v1/performance/improvement-actions?pageSize=20",
            headers=admin_headers,
        )
        self.assertEqual(list_status, 200, list_payload)
        self.assertTrue(any(item["actionNo"] for item in list_payload["data"]["items"]))

    def test_analytics_overview_contains_seed_metrics(self) -> None:
        status, payload = self.api_request(
            "GET",
            "/api/v1/performance/analytics/overview",
            headers=self.auth_headers("admin"),
        )
        self.assertEqual(status, 200, payload)
        self.assertGreater(payload["data"]["metrics"]["totalPlans"], 0)
        self.assertTrue(payload["data"]["gradeDistribution"])


if __name__ == "__main__":
    unittest.main()
