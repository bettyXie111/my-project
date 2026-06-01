# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


def new_id() -> str:
    return uuid4().hex


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()


def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def csv_tags(tags: list[str]) -> str:
    clean = []
    for t in tags:
        t = (t or "").strip()
        if not t:
            continue
        if "," in t:
            t = t.replace(",", " ")
        clean.append(t)
    # de-dup, keep order
    seen = set()
    out = []
    for t in clean:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return ",".join(out)


def parse_tags(tags_csv: str) -> list[str]:
    items = []
    for t in (tags_csv or "").split(","):
        t = t.strip()
        if t:
            items.append(t)
    return items
