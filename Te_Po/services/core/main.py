# -*- coding: utf-8 -*-
"""Render-ready core service skeleton for Tiwhanawhana microservices."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI

from Te_Po.utils.logger import get_logger
from Te_Po.utils.middleware.utf8_enforcer import apply_utf8_middleware
from Te_Po.utils.supabase_client import supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.core")

app = FastAPI(title="Tiwhanawhana Core Service", version="1.0.0")
apply_utf8_middleware(app)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("🌊 Core service warming up")
    if supabase is None:
        logger.warning("Supabase unavailable — running in dry mode")
        return
    await asyncio.to_thread(ensure_rongohia_schema, supabase)
    logger.info("Supabase schema ensured for core service")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
    return {"status": "awake", "kaitiaki": "Tiwhanawhana"}


@app.get("/test")
async def read_test() -> dict[str, str]:
    return {"message": "pong"}
