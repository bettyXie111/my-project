from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class ProjectRepository:
    """Repository backed by a JSON file so the demo can run without third-party services."""

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path

    def ensure_seeded(self) -> None:
        if self.data_path.exists():
            return
        from seed_data import build_demo_dataset

        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_path.write_text(
            json.dumps(build_demo_dataset(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load(self) -> dict[str, Any]:
        self.ensure_seeded()
        return json.loads(self.data_path.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.data_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def meta(self) -> dict[str, Any]:
        dataset = self.load()
        return dataset.get("meta", {})

    def users(self) -> list[dict[str, Any]]:
        dataset = self.load()
        return dataset.get("users", [])

    def projects(self) -> list[dict[str, Any]]:
        dataset = self.load()
        return dataset.get("projects", [])

    def sections(self) -> list[dict[str, Any]]:
        dataset = self.load()
        return dataset.get("sections", [])

    def support_templates(self) -> list[dict[str, Any]]:
        dataset = self.load()
        return dataset.get("supportTemplates", [])

    def report_templates(self) -> list[dict[str, Any]]:
        dataset = self.load()
        return dataset.get("reportTemplates", [])

    def get_user(self, username: str) -> dict[str, Any] | None:
        for user in self.users():
            if user["username"] == username:
                return user
        return None

    def get_section(self, section_id: str) -> dict[str, Any] | None:
        for section in self.sections():
            if section["id"] == section_id:
                return section
        return None

    def search_sections(self, keyword: str = "", risk: str = "") -> list[dict[str, Any]]:
        keyword_lower = keyword.lower().strip()
        risk_upper = risk.upper().strip()
        matched: list[dict[str, Any]] = []
        for section in self.sections():
            if keyword_lower and keyword_lower not in " ".join(
                [
                    section["id"],
                    section["name"],
                    section["zone"],
                    section["rockGrade"],
                ]
            ).lower():
                continue
            if risk_upper and section.get("currentRisk", "").upper() != risk_upper:
                continue
            matched.append(section)
        return matched

    def append_prediction(self, prediction: dict[str, Any]) -> None:
        dataset = self.load()
        dataset.setdefault("predictions", []).append(prediction)
        self.save(dataset)

    def append_recommendation(self, recommendation: dict[str, Any]) -> None:
        dataset = self.load()
        dataset.setdefault("recommendations", []).append(recommendation)
        dataset.setdefault("auditTrail", []).append(
            {
                "id": recommendation["id"],
                "type": "support_recommendation",
                "sectionId": recommendation["sectionId"],
                "createdAt": recommendation["generatedAt"],
                "summary": recommendation["summary"],
            }
        )
        self.save(dataset)

    def recent_predictions(self, limit: int = 8) -> list[dict[str, Any]]:
        dataset = self.load()
        items = dataset.get("predictions", [])
        return deepcopy(sorted(items, key=lambda item: item["generatedAt"], reverse=True)[:limit])

    def recent_recommendations(self, limit: int = 8) -> list[dict[str, Any]]:
        dataset = self.load()
        items = dataset.get("recommendations", [])
        return deepcopy(sorted(items, key=lambda item: item["generatedAt"], reverse=True)[:limit])

