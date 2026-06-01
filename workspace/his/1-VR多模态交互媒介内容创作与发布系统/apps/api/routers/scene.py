# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from apps.api.schemas.scene import SceneCreate, SceneNodeCreate, SceneNodeOut, SceneOut
from apps.api.services import scene_repo


router = APIRouter(prefix="/api/scenes", tags=["scenes"])


@router.post("", response_model=dict)
def create_scene(payload: SceneCreate):
    sid = scene_repo.create_scene(payload.project_id, payload.name)
    return {"id": sid}


@router.get("", response_model=list[SceneOut])
def list_scenes(project_id: str):
    return scene_repo.list_scenes(project_id)


@router.post("/nodes", response_model=dict)
def create_node(payload: SceneNodeCreate):
    nid = scene_repo.create_node(
        payload.scene_id,
        payload.parent_id,
        payload.name,
        payload.node_type,
        payload.transform_json,
        payload.asset_ref_id,
        payload.props_json,
    )
    return {"id": nid}


@router.get("/{scene_id}/nodes", response_model=list[SceneNodeOut])
def list_nodes(scene_id: str):
    return scene_repo.list_nodes(scene_id)
