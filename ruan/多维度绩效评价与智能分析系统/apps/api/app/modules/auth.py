"""Authentication and current-user endpoints."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any

from ..core.config import settings
from ..core.exceptions import ConflictError, UnauthorizedError, ValidationError
from ..core.responses import json_response
from ..core.security import create_signed_token, generate_salt, hash_password, iso_now, verify_password
from .common import (
    audit_log,
    generate_id,
    get_data_scopes,
    get_permissions_for_user,
    json_loads,
    mask_user,
    require_fields,
)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _issue_tokens(connection: sqlite3.Connection, user: dict[str, Any]) -> dict[str, Any]:
    access_token = create_signed_token({"sub": user["id"], "type": "access"}, settings.access_token_minutes)
    refresh_token = create_signed_token({"sub": user["id"], "type": "refresh"}, settings.refresh_token_minutes)
    connection.execute(
        """
        INSERT INTO refresh_tokens(id, user_id, token, expires_at, revoked_at, created_at)
        VALUES (?, ?, ?, ?, NULL, ?)
        """,
        (
            generate_id("refresh"),
            user["id"],
            refresh_token,
            (datetime.utcnow() + timedelta(minutes=settings.refresh_token_minutes)).isoformat() + "Z",
            iso_now(),
        ),
    )
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": settings.access_token_minutes * 60,
    }


def _login(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_fields(context.body, "username", "password")
    user_row = context.db.execute(
        "SELECT * FROM users WHERE username = ?",
        (context.body["username"],),
    ).fetchone()
    if user_row is None:
        raise UnauthorizedError("用户名或密码错误")
    user = {key: user_row[key] for key in user_row.keys()}
    locked_until = _parse_datetime(user.get("locked_until"))
    if locked_until is not None and locked_until > datetime.utcnow().astimezone(locked_until.tzinfo):
        raise UnauthorizedError("账号已锁定，请稍后再试")
    if not verify_password(context.body["password"], user["password_salt"], user["password_hash"]):
        failed_count = int(user["failed_login_count"]) + 1
        locked_until_value = None
        if failed_count >= settings.password_fail_threshold:
            locked_until_value = (datetime.utcnow() + timedelta(minutes=settings.password_lock_minutes)).isoformat() + "Z"
        context.db.execute(
            """
            UPDATE users
            SET failed_login_count = ?, locked_until = ?, updated_at = ?, version = version + 1
            WHERE id = ?
            """,
            (failed_count, locked_until_value, iso_now(), user["id"]),
        )
        raise UnauthorizedError("用户名或密码错误")
    context.db.execute(
        """
        UPDATE users
        SET failed_login_count = 0, locked_until = NULL, updated_at = ?, version = version + 1
        WHERE id = ?
        """,
        (iso_now(), user["id"]),
    )
    tokens = _issue_tokens(context.db, user)
    audit_log(
        context.db,
        actor_user_id=user["id"],
        action_type="LOGIN_SUCCESS",
        biz_type="AUTH",
        biz_id=user["id"],
        diff={"username": user["username"]},
        request_id=context.request_id,
    )
    return json_response(
        {
            **tokens,
            "user": mask_user(user),
        },
        context.request_id,
    )


def _refresh(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    require_fields(context.body, "refreshToken")
    token = context.body["refreshToken"]
    row = context.db.execute(
        "SELECT * FROM refresh_tokens WHERE token = ? AND revoked_at IS NULL",
        (token,),
    ).fetchone()
    if row is None:
        raise UnauthorizedError("刷新令牌无效")
    token_row = {key: row[key] for key in row.keys()}
    if _parse_datetime(token_row["expires_at"]) <= datetime.utcnow().astimezone(_parse_datetime(token_row["expires_at"]).tzinfo):
        raise UnauthorizedError("刷新令牌已过期")
    user_row = context.db.execute(
        "SELECT * FROM users WHERE id = ? AND status = 'ACTIVE'",
        (token_row["user_id"],),
    ).fetchone()
    if user_row is None:
        raise UnauthorizedError()
    user = {key: user_row[key] for key in user_row.keys()}
    response = _issue_tokens(context.db, user)
    return json_response(response, context.request_id)


def _logout(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    refresh_token = context.body.get("refreshToken")
    if refresh_token:
        context.db.execute(
            "UPDATE refresh_tokens SET revoked_at = ? WHERE token = ?",
            (iso_now(), refresh_token),
        )
    audit_log(
        context.db,
        actor_user_id=context.user["id"],
        action_type="LOGOUT",
        biz_type="AUTH",
        biz_id=context.user["id"],
        diff={},
        request_id=context.request_id,
    )
    return json_response({"success": True}, context.request_id)


def _me(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    roles = json_loads(context.user["role_codes_json"], [])
    permissions = get_permissions_for_user(context.db, context.user)
    data_scopes = get_data_scopes(context.db, context.user)
    return json_response(
        {
            "user": mask_user(context.user),
            "roles": roles,
            "permissions": permissions,
            "dataScopes": data_scopes,
        },
        context.request_id,
    )


def _health(context: Any) -> tuple[int, list[tuple[str, str]], bytes]:
    user_count = context.db.execute("SELECT COUNT(1) AS total FROM users").fetchone()["total"]
    return json_response({"status": "UP", "users": user_count}, context.request_id)


def register(router: Any) -> None:
    router.add("POST", "/api/v1/auth/login", _login, auth_required=False)
    router.add("POST", "/api/v1/auth/refresh", _refresh, auth_required=False)
    router.add("POST", "/api/v1/auth/logout", _logout)
    router.add("GET", "/api/v1/users/me", _me)
    router.add("GET", "/api/v1/health", _health, auth_required=False)
