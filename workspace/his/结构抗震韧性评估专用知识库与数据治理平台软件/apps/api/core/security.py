from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass


SECRET = "resilience-kb-governance-secret"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("utf-8"))


def _sign(payload_b64: str) -> str:
    sig = hmac.new(SECRET.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    return _b64url(sig)


def issue_token(subject: str, role: str, ttl_seconds: int = 12 * 3600) -> str:
    payload = {"sub": subject, "role": role, "exp": int(time.time()) + ttl_seconds}
    payload_b64 = _b64url(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    return f"{payload_b64}.{_sign(payload_b64)}"


@dataclass(frozen=True)
class TokenClaims:
    sub: str
    role: str


def verify_token(token: str) -> TokenClaims:
    parts = token.split(".")
    if len(parts) != 2:
        raise ValueError("invalid token format")
    payload_b64, sig = parts
    if not hmac.compare_digest(_sign(payload_b64), sig):
        raise ValueError("invalid signature")
    payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("token expired")
    return TokenClaims(sub=str(payload["sub"]), role=str(payload["role"]))

