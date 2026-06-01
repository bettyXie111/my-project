# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest


class HealthTest(unittest.TestCase):
    def test_import_app(self) -> None:
        from apps.api.main import app

        self.assertIsNotNone(app)

    def test_health_endpoint(self) -> None:
        from fastapi.testclient import TestClient
        from apps.api.main import app

        c = TestClient(app)
        r = c.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("status"), "ok")


if __name__ == "__main__":
    unittest.main()
