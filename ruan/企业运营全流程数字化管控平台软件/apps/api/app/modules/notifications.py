"""Notification endpoints."""

from __future__ import annotations

from typing import Any

from ..core.responses import json_response
from ..core.security import iso_now
from .common import build_list_sql, page_from_sql, require_permission


def _list_notifications(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "notification.view")
    sql = """
        SELECT * FROM notifications
        WHERE receiver_user_id = ?
        ORDER BY created_at DESC
    """
    rows = context.db.execute(sql, (context.user["id"],)).fetchall()
    items = [{key: row[key] for key in row.keys()} for row in rows]
    return json_response(items, context.request_id)


def _mark_read(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_permission(context.db, context.user, "notification.view")
    context.db.execute(
        """
        UPDATE notifications
        SET read_at = ?, updated_at = ?, updated_by = ?, version = version + 1
        WHERE id = ? AND receiver_user_id = ?
        """,
        (iso_now(), iso_now(), context.user["id"], context.path_params["notificationId"], context.user["id"]),
    )
    return json_response({"notificationId": context.path_params["notificationId"]}, context.request_id)


def register(router: Any) -> None:
    router.add("GET", "/api/v1/notifications", _list_notifications)
    router.add("POST", "/api/v1/notifications/{notificationId}/read", _mark_read)
