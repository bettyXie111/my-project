# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from apps.api.schemas.interaction import InteractionCreate, InteractionOut
from apps.api.services import interaction_repo


router = APIRouter(prefix="/api/interactions", tags=["interactions"])


@router.post("", response_model=dict)
def create_interaction(payload: InteractionCreate):
    iid = interaction_repo.create_interaction(payload.project_id, payload.scene_id, payload.name, payload.enabled, payload.graph_json)
    return {"id": iid}


@router.get("", response_model=list[InteractionOut])
def list_interactions(project_id: str):
    return interaction_repo.list_interactions(project_id)
