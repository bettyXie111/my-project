# -*- coding: utf-8 -*-
from __future__ import annotations

import secrets
from dataclasses import dataclass

from .errors import Unauthorized


@dataclass(frozen=True)
class User:
    username: str
    role: str


_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "designer": {"password": "design123", "role": "designer"},
    "reviewer": {"password": "review123", "role": "reviewer"},
}


def authenticate(username: str, password: str) -> User:
    record = _USERS.get(username)
    if not record or record["password"] != password:
        raise Unauthorized("invalid_credentials", code="invalid_credentials")
    return User(username=username, role=record["role"])


def issue_token(user: User) -> str:
    # Local demo token. Server keeps no session; token only used for UI hints.
    return f"demo-{user.role}-{secrets.token_hex(8)}"

