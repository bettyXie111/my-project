"""Custom exceptions and response mapping."""

from __future__ import annotations


class AppError(Exception):
    """Base application error."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class ValidationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(400, "REQ_400_01", message)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "未登录或令牌无效") -> None:
        super().__init__(401, "AUTH_401_01", message)


class ForbiddenError(AppError):
    def __init__(self, message: str = "权限不足") -> None:
        super().__init__(403, "AUTH_403_01", message)


class NotFoundError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(404, "REQ_404_01", message)


class ConflictError(AppError):
    def __init__(self, message: str, code: str = "REQ_409_01") -> None:
        super().__init__(409, code, message)


class FileTooLargeError(AppError):
    def __init__(self, message: str = "附件大小超限") -> None:
        super().__init__(413, "FILE_413_01", message)
