"""Minimal WSGI router and request context."""

from __future__ import annotations

import json
import mimetypes
import re
import sqlite3
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.parse import parse_qs

from .config import settings
from .database import get_connection
from .exceptions import AppError, NotFoundError, UnauthorizedError
from .responses import json_response
from .security import decode_signed_token


Handler = Callable[["RequestContext"], tuple[int, list[tuple[str, str]], bytes]]


@dataclass
class Route:
    method: str
    path: str
    handler: Handler
    auth_required: bool = True
    permission: str | None = None
    compiled: re.Pattern[str] = field(init=False)

    def __post_init__(self) -> None:
        pattern = re.sub(r"{([a-zA-Z_][a-zA-Z0-9_]*)}", r"(?P<\1>[^/]+)", self.path)
        self.compiled = re.compile(f"^{pattern}$")


@dataclass
class RequestContext:
    method: str
    path: str
    headers: dict[str, str]
    query: dict[str, Any]
    body: dict[str, Any]
    raw_body: bytes
    path_params: dict[str, str]
    request_id: str
    db: Any
    user: dict[str, Any] | None = None

    def header(self, name: str) -> str | None:
        return self.headers.get(name.lower())


class Router:
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add(
        self,
        method: str,
        path: str,
        handler: Handler,
        *,
        auth_required: bool = True,
        permission: str | None = None,
    ) -> None:
        self.routes.append(
            Route(
                method=method.upper(),
                path=path,
                handler=handler,
                auth_required=auth_required,
                permission=permission,
            )
        )

    def match(self, method: str, path: str) -> tuple[Route, dict[str, str]]:
        for route in self.routes:
            if route.method != method.upper():
                continue
            match = route.compiled.match(path)
            if match:
                return route, match.groupdict()
        raise NotFoundError(f"接口不存在: {path}")


def parse_query(environ: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}


def parse_body(environ: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    try:
        body_size = int(environ.get("CONTENT_LENGTH", "0") or 0)
    except ValueError:
        body_size = 0
    raw_body = environ["wsgi.input"].read(body_size) if body_size > 0 else b""
    if not raw_body:
        return raw_body, {}
    if "application/json" in environ.get("CONTENT_TYPE", ""):
        return raw_body, json.loads(raw_body.decode("utf-8"))
    return raw_body, {}


def collect_headers(environ: dict[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key, value in environ.items():
        if key.startswith("HTTP_"):
            headers[key[5:].replace("_", "-").lower()] = value
    if environ.get("CONTENT_TYPE"):
        headers["content-type"] = environ["CONTENT_TYPE"]
    return headers


def load_user_from_token(token: str, connection: Any) -> dict[str, Any]:
    payload = decode_signed_token(token)
    row = connection.execute(
        "SELECT * FROM users WHERE id = ? AND status = 'ACTIVE'",
        (payload["sub"],),
    ).fetchone()
    if row is None:
        raise UnauthorizedError()
    user = {key: row[key] for key in row.keys()}
    user["token_payload"] = payload
    return user


def authenticate(route: Route, headers: dict[str, str], connection: Any) -> dict[str, Any] | None:
    if not route.auth_required:
        return None
    authorization = headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    token = authorization.split(" ", 1)[1]
    return load_user_from_token(token, connection)


def status_text(status_code: int) -> str:
    mapping = {
        200: "200 OK",
        201: "201 Created",
        400: "400 Bad Request",
        401: "401 Unauthorized",
        403: "403 Forbidden",
        404: "404 Not Found",
        409: "409 Conflict",
        413: "413 Payload Too Large",
        500: "500 Internal Server Error",
    }
    return mapping.get(status_code, f"{status_code} OK")


def serve_static(path: str) -> tuple[int, list[tuple[str, str]], bytes]:
    safe_path = path.lstrip("/") or "index.html"
    candidate = (settings.web_root / safe_path).resolve()
    if not str(candidate).startswith(str(settings.web_root.resolve())) or not candidate.exists():
        candidate = settings.web_root / "index.html"
    content = candidate.read_bytes()
    mime_type, _ = mimetypes.guess_type(str(candidate))
    return 200, [
        ("Content-Type", f"{mime_type or 'text/html'}; charset=utf-8"),
        ("Content-Length", str(len(content))),
    ], content


class Application:
    def __init__(self, router: Router) -> None:
        self.router = router

    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        path = environ.get("PATH_INFO", "/")
        if not path.startswith(settings.api_prefix):
            status_code, headers, body = serve_static(path)
            start_response(status_text(status_code), headers)
            return [body]

        request_id = environ.get("HTTP_X_REQUEST_ID") or f"req_{abs(hash(path + environ.get('REQUEST_METHOD', 'GET')))}"
        method = environ.get("REQUEST_METHOD", "GET").upper()
        query = parse_query(environ)
        headers = collect_headers(environ)
        raw_body, body = parse_body(environ)
        connection = get_connection()
        try:
            route, path_params = self.router.match(method, path)
            user = authenticate(route, headers, connection)
            context = RequestContext(
                method=method,
                path=path,
                headers=headers,
                query=query,
                body=body,
                raw_body=raw_body,
                path_params=path_params,
                request_id=request_id,
                db=connection,
                user=user,
            )
            status_code, response_headers, response_body = route.handler(context)
            connection.commit()
        except AppError as exc:
            connection.rollback()
            status_code, response_headers, response_body = json_response(
                {},
                request_id,
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
            )
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            traceback.print_exc()
            status_code, response_headers, response_body = json_response(
                {},
                request_id,
                code="REQ_409_01",
                message=f"数据约束冲突: {exc}",
                status_code=409,
            )
        except Exception:
            connection.rollback()
            traceback.print_exc()
            status_code, response_headers, response_body = json_response(
                {},
                request_id,
                code="SYS_500_01",
                message="系统内部错误",
                status_code=500,
            )
        finally:
            connection.close()
        start_response(status_text(status_code), response_headers)
        return [response_body]
