# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apps.api.services.store import InMemoryStore


router = APIRouter(prefix="/api/hr", tags=["hr"])


class DepartmentIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class PositionIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str


class EmployeeIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str
    title: str = Field(..., min_length=1, max_length=50)


def get_store() -> InMemoryStore:
    # module-level singleton to keep the example minimal.
    global _STORE
    try:
        return _STORE
    except NameError:
        _STORE = InMemoryStore()
        return _STORE


@router.get("/departments")
def list_departments() -> list[dict]:
    return get_store().list_departments()


@router.post("/departments")
def create_department(payload: DepartmentIn) -> dict:
    _id = get_store().create_department(payload.name)
    return {"id": _id}


@router.delete("/departments/{dept_id}")
def delete_department(dept_id: str) -> dict:
    ok = get_store().delete_department(dept_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}


@router.get("/positions")
def list_positions() -> list[dict]:
    return get_store().list_positions()


@router.post("/positions")
def create_position(payload: PositionIn) -> dict:
    _id = get_store().create_position(payload.name, payload.dept_id)
    return {"id": _id}


@router.delete("/positions/{pos_id}")
def delete_position(pos_id: str) -> dict:
    ok = get_store().delete_position(pos_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}


@router.get("/employees")
def list_employees() -> list[dict]:
    return get_store().list_employees()


@router.post("/employees")
def create_employee(payload: EmployeeIn) -> dict:
    _id = get_store().create_employee(payload.name, payload.dept_id, payload.title)
    return {"id": _id}


@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: str) -> dict:
    ok = get_store().delete_employee(emp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
