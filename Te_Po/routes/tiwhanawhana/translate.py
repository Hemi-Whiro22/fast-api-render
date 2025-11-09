# -*- coding: utf-8 -*-
"""Tiwhanawhana translation routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from Te_Po.utils.logger import get_logger
from Te_Po.utils.openai_client import translate_text
from Te_Po.utils.supabase_client import insert_record

router = APIRouter(prefix="/tiwhanawhana/translate",
                   tags=["Tiwhanawhana - Translate"])
logger = get_logger(__name__)


class TranslationRequest(BaseModel):
    source_text: str = Field(..., min_length=1)
    target_lang: str = Field(default="te reo Māori")
    source_lang: str | None = None
    model_hint: str | None = None
    meta: dict[str, object] | None = None

    model_config = {"protected_namespaces": ()}


@router.post("/")
async def translate_payload(payload: TranslationRequest) -> dict[str, object]:
    try:
        translated = translate_text(
            payload.source_text, payload.target_lang, context=payload.source_lang)
    except Exception as exc:  # noqa: BLE001
        logger.error("Translation failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="Translation service unavailable.") from exc

    record = {
        "ocr_id": None,
        "source_lang": payload.source_lang,
        "target_lang": payload.target_lang,
        "source_text": payload.source_text,
        "translated_text": translated,
        "model_used": payload.model_hint,
        "confidence": None,
        "meta": payload.meta or {},
    }

    try:
        insert_record("tiwhanawhana.translations", record)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to log translation: %s", exc)
        raise HTTPException(
            status_code=502, detail="Failed to record translation.") from exc

    return {
        "translated_text": translated,
        "target_lang": payload.target_lang,
    }
