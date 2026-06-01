from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.trial import PlotCreate, TrialCreate, TrialDetail, TrialItem
from ..services.audit import write_audit
from ..services.trials import (
    add_plot,
    create_trial,
    get_trial,
    list_trials,
)


router = APIRouter(tags=["trials"])


@router.get("/trials", response_model=list[TrialItem])
def api_list_trials(q: str = "") -> list[TrialItem]:
    return list_trials(query=q.strip())


@router.post("/trials", response_model=TrialItem)
def api_create_trial(payload: TrialCreate) -> TrialItem:
    item = create_trial(payload)
    write_audit("trial.create", {"id": item.id, "name": item.name})
    return item


@router.get("/trials/{trial_id}", response_model=TrialDetail)
def api_get_trial(trial_id: str) -> TrialDetail:
    item = get_trial(trial_id)
    if not item:
        raise HTTPException(status_code=404, detail="trial_not_found")
    return item


@router.post("/trials/{trial_id}/plots", response_model=TrialDetail)
def api_add_plot(trial_id: str, payload: PlotCreate) -> TrialDetail:
    item = add_plot(trial_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="trial_not_found")
    write_audit("plot.create", {"trial_id": trial_id, "code": payload.code})
    return item

