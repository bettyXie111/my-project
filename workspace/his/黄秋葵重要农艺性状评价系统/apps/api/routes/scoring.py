from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas.scoring import ScoreBreakdown, ScoreProfileCreate, ScoreProfileItem
from ..services.audit import write_audit
from ..services.scoring import (
    calculate_scores,
    create_profile,
    get_profile,
    list_profiles,
)


router = APIRouter(tags=["scoring"])


@router.get("/score-profiles", response_model=list[ScoreProfileItem])
def api_list_profiles(q: str = "") -> list[ScoreProfileItem]:
    return list_profiles(query=q.strip())


@router.post("/score-profiles", response_model=ScoreProfileItem)
def api_create_profile(payload: ScoreProfileCreate) -> ScoreProfileItem:
    item = create_profile(payload)
    write_audit("score_profile.create", {"id": item.id, "name": item.name})
    return item


@router.get("/score-profiles/{profile_id}", response_model=ScoreProfileItem)
def api_get_profile(profile_id: str) -> ScoreProfileItem:
    item = get_profile(profile_id)
    if not item:
        raise HTTPException(status_code=404, detail="profile_not_found")
    return item


@router.get("/trials/{trial_id}/scores", response_model=list[ScoreBreakdown])
def api_trial_scores(trial_id: str, profile_id: str = "") -> list[ScoreBreakdown]:
    scores = calculate_scores(trial_id=trial_id, profile_id=profile_id.strip())
    if scores is None:
        raise HTTPException(status_code=404, detail="trial_not_found")
    write_audit("score.calculate", {"trial_id": trial_id, "profile_id": profile_id})
    return scores

