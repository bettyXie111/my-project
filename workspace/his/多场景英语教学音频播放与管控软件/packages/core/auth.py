from __future__ import annotations

from .crypto import hash_password
from .store import db


def authenticate_user(username: str, password: str) -> dict | None:
    user = db.get_user_by_username(username)
    if not user:
        return None
    if user["password_hash"] != hash_password(password):
        return None
    return {k: v for k, v in user.items() if k != "password_hash"}
