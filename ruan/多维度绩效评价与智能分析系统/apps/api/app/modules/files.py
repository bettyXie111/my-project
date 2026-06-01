"""File metadata and presign endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import settings
from ..core.exceptions import FileTooLargeError, ValidationError
from ..core.responses import json_response
from ..core.security import iso_now
from .common import audit_log, generate_id, require_fields, require_permission


ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".xlsx", ".csv"}


def _presign(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    require_fields(context.body, "fileName", "contentType", "bizRefType")
    suffix = Path(context.body["fileName"]).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValidationError("文件类型不允许")
    size_bytes = int(context.body.get("sizeBytes", 0))
    if size_bytes and size_bytes > settings.attachment_max_size:
        raise FileTooLargeError()
    object_key = f"{context.body['bizRefType'].lower()}/{generate_id('asset')}{suffix}"
    asset_id = generate_id("file")
    now = iso_now()
    context.db.execute(
        """
        INSERT INTO file_assets(
            id, file_name, object_key, content_type, size_bytes, biz_ref_type, biz_ref_id, status,
            created_at, created_by, updated_at, updated_by, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, 1)
        """,
        (
            asset_id,
            context.body["fileName"],
            object_key,
            context.body["contentType"],
            size_bytes,
            context.body["bizRefType"],
            context.body.get("bizRefId"),
            now,
            context.user["id"],
            now,
            context.user["id"],
        ),
    )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="FILE_PRESIGNED",
        biz_type="FILE_ASSET",
        biz_id=asset_id,
        diff=context.body,
        request_id=context.request_id,
    )
    return json_response(
        {
            "uploadUrl": f"/mock-storage/{object_key}",
            "objectKey": object_key,
            "expireAt": now,
            "fileAssetId": asset_id,
        },
        context.request_id,
        status_code=201,
    )


def _list_assets(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "masterdata.manage")
    rows = context.db.execute(
        "SELECT * FROM file_assets ORDER BY created_at DESC LIMIT 100"
    ).fetchall()
    items = [{key: row[key] for key in row.keys()} for row in rows]
    return json_response(items, context.request_id)


def register(router: Any) -> None:
    router.add("POST", "/api/v1/files/presign", _presign)
    router.add("GET", "/api/v1/files/assets", _list_assets)
