# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from apps.api.main import create_app


class HealthEndpointTests(unittest.TestCase):
    def test_health_ok(self) -> None:
        client = TestClient(create_app())
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "ok")


if __name__ == "__main__":
    unittest.main()

