# -*- coding: utf-8 -*-
import unittest

from apps.api.domain.snapshot import summarize_snapshot, validate_snapshot


class SnapshotTest(unittest.TestCase):
    def test_validate_empty_snapshot(self) -> None:
        validate_snapshot(
            {
                "season": "春",
                "plants": [],
                "materials": [],
                "lights": [],
                "issues": [],
                "pavings": [],
            }
        )

    def test_summarize_counts(self) -> None:
        summary = summarize_snapshot(
            {
                "season": "秋",
                "plants": [{"id": "p1"}],
                "materials": [{"id": "m1"}, {"id": "m2"}],
                "lights": [],
                "issues": [{"id": "r1"}],
                "pavings": [{"id": "pv1"}, {"id": "pv2"}, {"id": "pv3"}],
            }
        )
        self.assertEqual(summary["season"], "秋")
        self.assertEqual(summary["counts"]["plants"], 1)
        self.assertEqual(summary["counts"]["materials"], 2)
        self.assertEqual(summary["counts"]["issues"], 1)
        self.assertEqual(summary["counts"]["pavings"], 3)

    def test_invalid_season_rejected(self) -> None:
        with self.assertRaises(Exception):
            validate_snapshot(
                {
                    "season": "雨季",
                    "plants": [],
                    "materials": [],
                    "lights": [],
                    "issues": [],
                    "pavings": [],
                }
            )


if __name__ == "__main__":
    unittest.main()

