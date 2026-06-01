from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.observation import ObservationCreate, ObservationItem, ObservationUpdate
from ..services.audit import write_audit
from ..services.observations import (
    create_observation,
    get_observation,
    list_observations,
    update_observation_status,
)


router = APIRouter(tags=["observations"])


@router.get("/observations", response_model=list[ObservationItem])
def api_list_observations(trial_id: str = "", plot_id: str = "", trait_id: str = "") -> list[ObservationItem]:
    return list_observations(trial_id=trial_id.strip(), plot_id=plot_id.strip(), trait_id=trait_id.strip())


@router.get("/observations/{obs_id}", response_model=ObservationItem)
def api_get_observation(obs_id: str) -> ObservationItem:
    item = get_observation(obs_id)
    if not item:
        raise HTTPException(status_code=404, detail="observation_not_found")
    return item


@router.post("/observations", response_model=ObservationItem)
def api_create_observation(payload: ObservationCreate) -> ObservationItem:
    item = create_observation(payload)
    write_audit("observation.create", {"id": item.id, "plot_id": item.plot_id, "trait_id": item.trait_id})
    return item


@router.put("/observations/{obs_id}/status", response_model=ObservationItem)
def api_update_observation_status(obs_id: str, payload: ObservationUpdate) -> ObservationItem:
    item = update_observation_status(obs_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="observation_not_found")
    write_audit("observation.status", {"id": item.id, "status": item.status})
    return item

