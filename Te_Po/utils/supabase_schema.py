# -*- coding: utf-8 -*-
"""Supabase schema helpers for the Rongohia namespace."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Te_Po.utils.logger import get_logger

logger = get_logger("supabase.schema")
_LOG_PATH = Path("logs/supabase_migration.log")

_SCHEMA_SQL = """
create schema if not exists public;
create schema if not exists public.rongohia;
create table if not exists public.rongohia.service_health (
    id uuid primary key default gen_random_uuid(),
    service text not null,
    status text not null,
    checked_at timestamptz not null default now()
);
"""


def ensure_rongohia_schema(client: Any) -> None:
    """Ensure baseline tables exist inside public.rongohia.

    Skips execution when the Supabase client is missing (development mode).
    """
    if client is None:
        logger.warning("Supabase client missing; skipping schema ensure")
        return
    try:
        client.rpc("exec_sql", {"sql": _SCHEMA_SQL}).execute()
        _append_log("schema ensured")
    except Exception as exc:  # noqa: BLE001
        logger.error("Supabase schema ensure failed: %s", exc)
        _append_log(f"schema ensure failed: {exc}")


def _append_log(message: str) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"{datetime.now(timezone.utc).isoformat()} {message}\n")
