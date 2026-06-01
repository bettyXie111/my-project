from __future__ import annotations

import unittest
from datetime import date

from fastapi.testclient import TestClient

from ..main import create_app


class SmokeApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_health_list_endpoints(self) -> None:
        r = self.client.get("/api/varieties")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/api/traits")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/api/trials")
        self.assertEqual(r.status_code, 200)

    def test_create_and_score_minimal_flow(self) -> None:
        v = self.client.post("/api/varieties", json={"name": "鲁葵-试验A", "source": "试验站", "type": "品种"}).json()
        t = self.client.post(
            "/api/traits",
            json={
                "code": "PH",
                "name": "株高",
                "unit": "cm",
                "direction": "higher_is_better",
                "min_value": 10,
                "max_value": 300,
                "method": "拔节期至始花期测量主茎高度",
            },
        ).json()
        trl = self.client.post(
            "/api/trials",
            json={"name": "2026春季品比", "location": "南京试验田", "season": "2026S", "design": "randomized_block", "replicates": 3},
        ).json()
        detail = self.client.post(
            f"/api/trials/{trl['id']}/plots",
            json={"block": 1, "code": "B1-01", "variety_id": v["id"], "area_m2": 12.0, "management_tags": ["露地", "滴灌"]},
        ).json()
        plot_id = detail["plots"][0]["id"]

        obs = self.client.post(
            "/api/observations",
            json={"plot_id": plot_id, "trait_id": t["id"], "observed_at": date(2026, 5, 1).isoformat(), "value": 98.5, "operator": "tester"},
        )
        self.assertEqual(obs.status_code, 200)
        scores = self.client.get(f"/api/trials/{trl['id']}/scores").json()
        self.assertTrue(len(scores) >= 1)
        self.assertIn("total_score", scores[0])

