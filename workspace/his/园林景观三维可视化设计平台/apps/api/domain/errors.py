# -*- coding: utf-8 -*-
from __future__ import annotations


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class BadRequest(ApiError):
    def __init__(self, message: str, *, code: str = "bad_request") -> None:
        super().__init__(400, code, message)


class Unauthorized(ApiError):
    def __init__(self, message: str = "unauthorized", *, code: str = "unauthorized") -> None:
        super().__init__(401, code, message)


class NotFound(ApiError):
    def __init__(self, message: str = "not_found", *, code: str = "not_found") -> None:
        super().__init__(404, code, message)


class Conflict(ApiError):
    def __init__(self, message: str = "conflict", *, code: str = "conflict") -> None:
        super().__init__(409, code, message)

