# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from .errors import ApiError, BadRequest, NotFound


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: dict[str, list[str]]
    headers: dict[str, str]
    body: bytes

    def json(self) -> dict[str, Any]:
        if not self.body:
            return {}
        try:
            return json.loads(self.body.decode("utf-8"))
        except Exception as exc:
            raise BadRequest("invalid_json") from exc

    def form(self) -> dict[str, str]:
        raw = parse_qs(self.body.decode("utf-8", errors="ignore"))
        return {k: (v[0] if v else "") for k, v in raw.items()}


Response = tuple[int, dict[str, str], bytes]
HandlerFn = Callable[[Request, dict[str, str]], Response]


def json_response(status: int, payload: dict[str, Any]) -> Response:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    return status, {"Content-Type": "application/json; charset=utf-8", "Content-Length": str(len(data))}, data


def text_response(status: int, text: str, *, content_type: str = "text/plain; charset=utf-8") -> Response:
    data = text.encode("utf-8")
    return status, {"Content-Type": content_type, "Content-Length": str(len(data))}, data


class Router:
    def __init__(self) -> None:
        self._routes: list[tuple[str, str, HandlerFn]] = []

    def add(self, method: str, pattern: str, handler: HandlerFn) -> None:
        self._routes.append((method.upper(), pattern, handler))

    def match(self, req: Request) -> tuple[HandlerFn, dict[str, str]]:
        for method, pattern, fn in self._routes:
            if method != req.method.upper():
                continue
            params = self._match_pattern(pattern, req.path)
            if params is not None:
                return fn, params
        raise NotFound()

    @staticmethod
    def _match_pattern(pattern: str, path: str) -> dict[str, str] | None:
        # Very small path param matcher: "/api/plans/{planId}/versions"
        p_parts = [p for p in pattern.split("/") if p]
        a_parts = [p for p in path.split("/") if p]
        if len(p_parts) != len(a_parts):
            return None
        params: dict[str, str] = {}
        for p, a in zip(p_parts, a_parts, strict=True):
            if p.startswith("{") and p.endswith("}"):
                params[p[1:-1]] = a
            elif p != a:
                return None
        return params


def build_request(method: str, raw_path: str, headers: dict[str, str], body: bytes) -> Request:
    parsed = urlparse(raw_path)
    return Request(method=method, path=parsed.path, query=parse_qs(parsed.query), headers=headers, body=body)


def handle_api_error(exc: ApiError) -> Response:
    return json_response(exc.status, {"ok": False, "error": exc.code, "message": exc.message})

