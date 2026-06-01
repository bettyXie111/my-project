"""Token and password helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from .config import settings
from .exceptions import UnauthorizedError


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utcnow().replace(microsecond=0).isoformat()


def base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def base64url_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode((raw + padding).encode("ascii"))


def generate_salt() -> str:
    return base64url_encode(os.urandom(16))


def hash_password(password: str, salt: str) -> str:
    salt_bytes = base64url_decode(salt)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt_bytes,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return derived.hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password, salt), expected_hash)


def create_signed_token(payload: dict[str, Any], expires_minutes: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload_data = dict(payload)
    payload_data["exp"] = int((utcnow() + timedelta(minutes=expires_minutes)).timestamp())
    payload_data.setdefault("jti", uuid.uuid4().hex)
    header_b64 = base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = base64url_encode(
        json.dumps(payload_data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(
        settings.token_secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{header_b64}.{payload_b64}.{base64url_encode(signature)}"


def decode_signed_token(token: str) -> dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise UnauthorizedError() from exc
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_signature = hmac.new(
        settings.token_secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(base64url_decode(signature_b64), expected_signature):
        raise UnauthorizedError()
    payload = json.loads(base64url_decode(payload_b64).decode("utf-8"))
    if int(payload["exp"]) < int(utcnow().timestamp()):
        raise UnauthorizedError("令牌已过期")
    return payload
