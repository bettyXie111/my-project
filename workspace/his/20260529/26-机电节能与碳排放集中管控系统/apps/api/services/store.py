# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import uuid4


class InMemoryStore:
    def __init__(self) -> None:
        self._departments: dict[str, dict[str, Any]] = {}
        self._positions: dict[str, dict[str, Any]] = {}
        self._employees: dict[str, dict[str, Any]] = {}

    def _new_id(self) -> str:
        return uuid4().hex

    def list_departments(self) -> list[dict[str, Any]]:
        return list(self._departments.values())

    def create_department(self, name: str) -> str:
        _id = self._new_id()
        self._departments[_id] = {"id": _id, "name": name, "created_at": datetime.utcnow().isoformat()}
        return _id

    def delete_department(self, dept_id: str) -> bool:
        return self._departments.pop(dept_id, None) is not None

    def list_positions(self) -> list[dict[str, Any]]:
        return list(self._positions.values())

    def create_position(self, name: str, dept_id: str) -> str:
        _id = self._new_id()
        self._positions[_id] = {"id": _id, "name": name, "dept_id": dept_id, "created_at": datetime.utcnow().isoformat()}
        return _id

    def delete_position(self, pos_id: str) -> bool:
        return self._positions.pop(pos_id, None) is not None

    def list_employees(self) -> list[dict[str, Any]]:
        return list(self._employees.values())

    def create_employee(self, name: str, dept_id: str, title: str) -> str:
        _id = self._new_id()
        self._employees[_id] = {
            "id": _id,
            "name": name,
            "dept_id": dept_id,
            "title": title,
            "created_at": datetime.utcnow().isoformat(),
        }
        return _id

    def delete_employee(self, emp_id: str) -> bool:
        return self._employees.pop(emp_id, None) is not None
