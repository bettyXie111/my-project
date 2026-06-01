from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from apps.api.main import create_app


class SmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_health(self) -> None:
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_login_and_list_projects(self) -> None:
        token = self._login("admin", "admin123")
        r = self.client.get("/api/projects", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json(), list)

    def _login(self, username: str, password: str) -> str:
        r = self.client.post("/api/auth/login", json={"username": username, "password": password})
        self.assertEqual(r.status_code, 200)
        return r.json()["token"]


if __name__ == "__main__":
    unittest.main()

