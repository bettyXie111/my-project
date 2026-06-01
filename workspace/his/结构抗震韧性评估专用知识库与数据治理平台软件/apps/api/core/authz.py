from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from .security import TokenClaims, verify_token


ROLE_PERMS: dict[str, set[str]] = {
    "admin": {"*"},
    "engineer": {"projects:read", "structures:*", "datasets:read", "quality:read", "indicators:*", "assessments:*", "knowledge:*", "audit:read"},
    "governance": {"datasets:*", "quality:*", "projects:read", "structures:read", "audit:*", "knowledge:read", "indicators:read"},
    "reviewer": {"projects:read", "structures:read", "datasets:read", "quality:read", "assessments:review", "knowledge:read", "audit:read"},
}


def _has(permset: set[str], perm: str) -> bool:
    if "*" in permset:
        return True
    if perm in permset:
        return True
    prefix = perm.split(":")[0] + ":*"
    return prefix in permset


def require_user(request: Request) -> TokenClaims:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    try:
        return verify_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")


def require_perm(perm: str):
    def dep(claims: TokenClaims = Depends(require_user)) -> TokenClaims:
        perms = ROLE_PERMS.get(claims.role, set())
        if not _has(perms, perm):
            raise HTTPException(status_code=403, detail="forbidden")
        return claims

    return dep

