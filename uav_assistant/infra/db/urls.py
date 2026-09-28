from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL


ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def load_environment() -> None:
    load_dotenv(dotenv_path=ENV_FILE)


def required_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required env var: {key}")
    return value


def build_postgres_url() -> URL:
    load_environment()
    return URL.create(
        drivername=required_env("PGASYNCDRIVER"),
        username=required_env("PGROLE"),
        password=required_env("PGPASSWORD"),
        host=required_env("PGHOST"),
        port=int(required_env("PGPORT")),
        database=required_env("PGDATABASE"),
    )


def get_mongodb_uri() -> str:
    load_environment()
    return required_env("MONGODB_URI")


def get_mongodb_database() -> str:
    load_environment()
    return required_env("MONGODB_DATABASE")
