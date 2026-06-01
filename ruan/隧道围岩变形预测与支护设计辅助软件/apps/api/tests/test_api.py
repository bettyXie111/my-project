from __future__ import annotations

import json
import os
import sys
import threading
import time
import unittest
from http.client import HTTPConnection
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = PROJECT_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

import main as api_main  # noqa: E402


class TunnelApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ["APP_PORT"] = "8026"
        api_main.PORT = 8026
        api_main.REPOSITORY.ensure_seeded()
        cls.server = api_main.ThreadingHTTPServer(("127.0.0.1", 8026), api_main.TunnelAssistantHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, dict]:
        connection = HTTPConnection("127.0.0.1", 8026, timeout=10)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        payload = json.dumps(body or {}, ensure_ascii=False).encode("utf-8")
        connection.request(method, path, body=payload if method == "POST" else None, headers=headers)
        response = connection.getresponse()
        raw = response.read().decode("utf-8")
        connection.close()
        return response.status, json.loads(raw)

    def login(self) -> str:
        status, data = self.request("POST", "/api/auth/login", {"username": "admin", "password": "admin123"})
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertIn("token", data)
        return data["token"]

    def test_login_failure(self) -> None:
        status, data = self.request("POST", "/api/auth/login", {"username": "admin", "password": "wrong"})
        self.assertEqual(status, 401)
        self.assertFalse(data["ok"])

    def test_dashboard_requires_auth(self) -> None:
        status, data = self.request("GET", "/api/dashboard")
        self.assertEqual(status, 401)
        self.assertFalse(data["ok"])

    def test_dashboard_snapshot(self) -> None:
        token = self.login()
        status, data = self.request("GET", "/api/dashboard", token=token)
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        snapshot = data["data"]
        self.assertGreaterEqual(snapshot["totalSections"], 10)
        self.assertIn("statusBoard", snapshot)
        self.assertGreater(len(snapshot["alerts"]), 0)

    def test_section_detail_and_filters(self) -> None:
        token = self.login()
        status, data = self.request("GET", "/api/sections?risk=HIGH", token=token)
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertGreater(len(data["items"]), 0)
        section_id = data["items"][0]["id"]
        status, detail = self.request("GET", f"/api/sections/{section_id}", token=token)
        self.assertEqual(status, 200)
        self.assertEqual(detail["item"]["id"], section_id)
        self.assertIn("monitoring", detail["item"])

    def test_prediction_flow(self) -> None:
        token = self.login()
        status, data = self.request(
            "POST",
            "/api/predictions",
            {
                "sectionId": "SEC-005",
                "scenarioName": "暴雨叠加快速进尺",
                "excavationIntensity": 1.3,
                "rainfallFactor": 1.1,
                "safetyFactor": 1.05,
            },
            token=token,
        )
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        item = data["item"]
        self.assertEqual(item["sectionId"], "SEC-005")
        self.assertEqual(len(item["predictedConvergence"]), 7)
        self.assertIn(item["riskLevel"], {"LOW", "MEDIUM", "HIGH", "CRITICAL"})

    def test_recommendation_flow(self) -> None:
        token = self.login()
        status, data = self.request(
            "POST",
            "/api/recommendations",
            {
                "sectionId": "SEC-008",
                "scenarioName": "深埋软岩加固复核",
                "excavationIntensity": 1.25,
                "rainfallFactor": 0.8,
                "safetyFactor": 1.1,
            },
            token=token,
        )
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        item = data["item"]
        self.assertEqual(item["sectionId"], "SEC-008")
        self.assertIn("materialPlan", item)
        self.assertGreater(item["comparison"]["initialShotcreteThicknessCm"], 0)

    def test_contract_endpoint(self) -> None:
        status, data = self.request("GET", "/api/contracts")
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])

    def test_static_index(self) -> None:
        connection = HTTPConnection("127.0.0.1", 8026, timeout=10)
        connection.request("GET", "/")
        response = connection.getresponse()
        html = response.read().decode("utf-8")
        connection.close()
        self.assertEqual(response.status, 200)
        self.assertIn("隧道围岩变形预测与支护设计辅助软件", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)

