"""Helpers for JSON and text responses."""

from __future__ import annotations

import json
from typing import Any


def json_response(
    data: Any,
    request_id: str,
    *,
    code: str = "OK",
    message: str = "成功",
    status_code: int = 200,
) -> tuple[int, list[tuple[str, str]], bytes]:
    body = json.dumps(
        {
            "code": code,
            "message": message,
            "requestId": request_id,
            "data": data,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    return status_code, headers, body


def page_response(
    items: list[Any],
    page: int,
    page_size: int,
    total: int,
    request_id: str,
) -> tuple[int, list[tuple[str, str]], bytes]:
    return json_response(
        {
            "items": items,
            "page": page,
            "pageSize": page_size,
            "total": total,
        },
        request_id,
    )


def text_response(
    text: str,
    *,
    status_code: int = 200,
    content_type: str = "text/plain; charset=utf-8",
) -> tuple[int, list[tuple[str, str]], bytes]:
    body = text.encode("utf-8")
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
    ]
    return status_code, headers, body
