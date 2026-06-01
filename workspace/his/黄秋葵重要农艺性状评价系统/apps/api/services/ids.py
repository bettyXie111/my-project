from __future__ import annotations

import secrets
import string


ALPHABET = string.ascii_lowercase + string.digits


def short_id(prefix: str) -> str:
    token = "".join(secrets.choice(ALPHABET) for _ in range(10))
    prefix = prefix.strip().lower().replace("_", "-")
    if not prefix:
        prefix = "id"
    return f"{prefix}_{token}"

