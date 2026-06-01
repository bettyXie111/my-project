# -*- coding: utf-8 -*-
from __future__ import annotations

"""
Static file helper used by the built-in HTTP server.

Goals:
- keep path traversal safe;
- provide consistent content-type;
- support simple cache headers to reduce reload overhead during review;
- avoid external dependencies.
"""

import hashlib
import mimetypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .errors import NotFound


TEXT_PREFIXES = ("text/",)
EXTRA_TEXT_TYPES = {
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".css": "text/css",
    ".html": "text/html",
    ".json": "application/json",
    ".md": "text/markdown",
    ".svg": "image/svg+xml",
}


def safe_join(root: Path, rel: str) -> Path | None:
    rel = rel.lstrip("/").replace("/", os.sep)
    target = (root / rel).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


def guess_content_type(path: Path) -> str:
    ctype, _ = mimetypes.guess_type(str(path))
    if ctype:
        return ctype
    return EXTRA_TEXT_TYPES.get(path.suffix.lower(), "application/octet-stream")


def is_text_type(content_type: str) -> bool:
    return any(content_type.startswith(p) for p in TEXT_PREFIXES) or content_type in EXTRA_TEXT_TYPES.values()


def compute_etag(data: bytes) -> str:
    # Weak etag is fine for local use.
    digest = hashlib.sha1(data).hexdigest()
    return f"W/\"{digest}\""


@dataclass(frozen=True)
class StaticResponse:
    status: int
    headers: dict[str, str]
    body: bytes


def build_static_response(
    *,
    root: Path,
    request_path: str,
    fallback: str = "index.html",
    cache_seconds: int = 30,
) -> StaticResponse:
    # Default "/" to index.
    path = request_path
    if path == "/" or path == "":
        path = "/" + fallback
    target = safe_join(root, path)
    if target is None or not target.exists() or not target.is_file():
        # SPA fallback
        target = root / fallback
        if not target.exists():
            raise NotFound("static file not found")

    data = target.read_bytes()
    ctype = guess_content_type(target)
    headers = {
        "Content-Type": f"{ctype}; charset=utf-8" if is_text_type(ctype) else ctype,
        "Content-Length": str(len(data)),
        "Cache-Control": f"public, max-age={max(cache_seconds,0)}",
        "ETag": compute_etag(data),
    }
    return StaticResponse(status=200, headers=headers, body=data)


def iter_files(root: Path, *, suffixes: Iterable[str] | None = None) -> list[Path]:
    out: list[Path] = []
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if suffixes is not None and p.suffix.lower() not in {s.lower() for s in suffixes}:
            continue
        out.append(p)
    return out


def build_manifest(root: Path) -> dict[str, str]:
    """
    Return {relative_path: etag} for quick integrity checks.
    """
    manifest: dict[str, str] = {}
    for p in iter_files(root):
        rel = str(p.relative_to(root)).replace("\\", "/")
        try:
            manifest[rel] = compute_etag(p.read_bytes())
        except Exception:
            manifest[rel] = "W/\"unreadable\""
    return manifest

