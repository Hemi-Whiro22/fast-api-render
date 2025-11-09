# -*- coding: utf-8 -*-
"""Translation routes."""
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from Te_Po.config import get_settings
from Te_Po.utils.logger import get_logger
from Te_Po.utils.openai_client import translate_text as openai_translate
from Te_Po.utils.supabase_client import insert_record

router = APIRouter()
logger = get_logger(__name__)


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1)
    target_language: str = Field(default="te reo Māori")

    model_config = {"protected_namespaces": ()}


class TranslationResponse(BaseModel):
    translation: str
    target_language: str
    created_at: datetime

    model_config = {"protected_namespaces": ()}


@router.post("/", response_model=TranslationResponse)
async def translate(payload: TranslationRequest) -> TranslationResponse:
    settings = get_settings()
    logger.info("Translating text into %s", payload.target_language)

    try:
        translated = await run_in_threadpool(
            openai_translate,
            payload.text,
            payload.target_language,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Translation failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="Translation service failed.") from exc

    table = settings.supabase_table_translations or "translations"

    record = insert_record(
        table,
        {
            "content": translated,
            "metadata": {
                "source_text": payload.text,
                "target_language": payload.target_language,
            },
        },
    )

    created_at = record.get("created_at", datetime.utcnow())
    return TranslationResponse(
        translation=translated.strip(),
        target_language=payload.target_language,
        created_at=created_at,
    )
