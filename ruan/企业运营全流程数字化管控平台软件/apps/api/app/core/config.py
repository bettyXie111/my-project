"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Settings:
    """Runtime settings."""

    app_name: str = "企业运营全流程数字化管控平台"
    api_prefix: str = "/api/v1"
    host: str = os.environ.get("APP_HOST", "127.0.0.1")
    port: int = int(os.environ.get("APP_PORT", "8000"))
    database_path: Path = Path(
        os.environ.get(
            "APP_DATABASE_PATH",
            str(REPO_ROOT / "apps" / "api" / "data.sqlite3"),
        )
    )
    migrations_dir: Path = REPO_ROOT / "apps" / "api" / "migrations"
    web_root: Path = REPO_ROOT / "apps" / "web"
    access_token_minutes: int = int(os.environ.get("APP_ACCESS_TOKEN_MINUTES", "60"))
    refresh_token_minutes: int = int(os.environ.get("APP_REFRESH_TOKEN_MINUTES", "1440"))
    password_lock_minutes: int = int(os.environ.get("APP_PASSWORD_LOCK_MINUTES", "15"))
    password_fail_threshold: int = int(os.environ.get("APP_PASSWORD_FAIL_THRESHOLD", "5"))
    token_secret: str = os.environ.get(
        "APP_TOKEN_SECRET",
        "local-demo-secret-key-change-before-production",
    )
    attachment_max_size: int = int(os.environ.get("APP_ATTACHMENT_MAX_SIZE", "10485760"))
    enable_hard_budget_control: bool = os.environ.get(
        "APP_ENABLE_HARD_BUDGET_CONTROL",
        "1",
    ) == "1"


settings = Settings()
