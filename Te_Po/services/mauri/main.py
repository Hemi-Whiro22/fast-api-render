# -*- coding: utf-8 -*-
"""Render mauri service."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from Te_Po.config import get_settings
from Te_Po.services.tiwhanawhana import log_mauri
from Te_Po.utils.logger import get_logger
from Te_Po.utils.middleware.utf8_enforcer import apply_utf8_middleware
from Te_Po.utils.supabase_client import fetch_latest, insert_record, supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.mauri")

app = FastAPI(title="Tiwhanawhana Mauri Service", version="1.0.0")
apply_utf8_middleware(app)


class MauriPayload(BaseModel):
    phase: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    tohu_id: str | None = None
    meta: dict[str, object] | None = None


@app.on_event("startup")
async def startup_event() -> None:
    if supabase is not None:
        await run_in_threadpool(ensure_rongohia_schema, supabase)
    logger.info("💓 Mauri service ready")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
    return {"service": "mauri", "state": "awake"}


@app.post("/api/mauri/log")
async def mauri_log(payload: MauriPayload) -> dict[str, object]:
    record = log_mauri(
        payload.phase,
        payload.message,
        tohu_id=payload.tohu_id,
        meta=payload.meta,
    )

    settings = get_settings()
    try:
        insert_record("tiwhanawhana.mauri_logs", record)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to persist mauri log: %s", exc)
        raise HTTPException(status_code=502, detail="Supabase logging failed.") from exc

    return {
        "phase": payload.phase,
        "message": payload.message,
        "meta": record["meta"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/mauri/status")
async def mauri_status() -> dict[str, object]:
    settings = get_settings()
    try:
        latest = fetch_latest("tiwhanawhana.mauri_logs")
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch mauri logs: %s", exc)
        raise HTTPException(status_code=502, detail="Supabase fetch failed.") from exc

    data = latest.get("data") if isinstance(latest, dict) else latest
    if not data:
        return {"status": "unknown", "message": "No mauri logs found."}

    entry = data[0] if isinstance(data, list) else data
    return {
        "status": entry.get("phase", "unknown"),
        "message": entry.get("message"),
        "meta": entry.get("meta", {}),
    }
