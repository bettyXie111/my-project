# -*- coding: utf-8 -*-
from __future__ import annotations

import secrets
import time


def new_id(prefix: str) -> str:
    # Stable-enough for local use; easy to read in exported CSV.
    ts = int(time.time() * 1000)
    rnd = secrets.token_hex(3)
    return f"{prefix}-{ts:x}-{rnd}"

