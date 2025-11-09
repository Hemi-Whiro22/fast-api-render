# -*- coding: utf-8 -*-
"""Render translate service."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from Te_Po.config import get_settings
from Te_Po.utils.logger import get_logger
from Te_Po.utils.middleware.utf8_enforcer import apply_utf8_middleware
from Te_Po.utils.openai_client import translate_text
from Te_Po.utils.supabase_client import insert_record, supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.translate")

app = FastAPI(title="Tiwhanawhana Translate Service", version="1.0.0")
apply_utf8_middleware(app)


class TranslationPayload(BaseModel):
    text: str = Field(..., min_length=1)
    target_language: str = Field(default="te reo Māori")
    context: str | None = None


@app.on_event("startup")
async def startup_event() -> None:
    if supabase is not None:
        await run_in_threadpool(ensure_rongohia_schema, supabase)
    logger.info("🗣️ Translate service ready")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
    return {"service": "translate", "state": "awake"}


@app.post("/api/translate/perform")
async def perform_translation(payload: TranslationPayload) -> dict[str, object]:
    try:
        translated = await run_in_threadpool(
            translate_text,
            payload.text,
            payload.target_language,
            payload.context,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Translation failed: %s", exc)
        raise HTTPException(status_code=502, detail="Translation service unavailable.") from exc

    settings = get_settings()
    insert_record(
        settings.supabase_table_translations,
        {
            "content": translated,
            "metadata": payload.model_dump(),
        },
    )

    return {
        "translation": translated,
        "target_language": payload.target_language,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
