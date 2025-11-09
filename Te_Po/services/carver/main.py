# -*- coding: utf-8 -*-
"""Render carving service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from Te_Po.utils.logger import get_logger
from Te_Po.utils.middleware.utf8_enforcer import apply_utf8_middleware
from Te_Po.utils.openai_client import generate_embedding
from Te_Po.utils.supabase_client import insert_record, supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.carving")

app = FastAPI(title="Tiwhanawhana Carving Service", version="1.0.0")
apply_utf8_middleware(app)


class CarvingPayload(BaseModel):
    prompt: str = Field(..., min_length=1)
    context: dict[str, Any] | None = None


@app.on_event("startup")
async def startup_event() -> None:
    if supabase is not None:
        await run_in_threadpool(ensure_rongohia_schema, supabase)
    logger.info("🪶 Carving service ready")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
    return {"service": "carving", "state": "awake"}


@app.post("/api/carving/render")
async def render_carving(payload: CarvingPayload) -> dict[str, object]:
    try:
        embedding = await run_in_threadpool(generate_embedding, payload.prompt)
    except Exception as exc:  # noqa: BLE001
        logger.error("Carving embedding failed: %s", exc)
        raise HTTPException(status_code=502, detail="Carving model unavailable.") from exc

    metadata = payload.context or {}
    insert_record(
        "rongohia.carvings",
        {
            "output_type": "carving_prompt",
            "output_content": payload.prompt,
            "meta": metadata,
            "embedding": list(embedding),
        },
    )

    return {
        "prompt": payload.prompt,
        "vector_length": len(embedding),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
