# -*- coding: utf-8 -*-
"""Tiwhanawhana embedding routes."""
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from Te_Po.services.tiwhanawhana import create_embedding
from Te_Po.utils.logger import get_logger
from Te_Po.utils.supabase_client import insert_record

router = APIRouter(prefix="/tiwhanawhana/embed", tags=["Tiwhanawhana - Embed"])
logger = get_logger(__name__)


class EmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1)
    translation_id: UUID | None = None
    meta: dict[str, object] | None = None


class EmbeddingResponse(BaseModel):
    embedding_length: int
    translation_id: UUID | None
    meta: dict[str, object]


@router.post("/", response_model=EmbeddingResponse)
async def create_embedding_route(payload: EmbeddingRequest) -> EmbeddingResponse:
    try:
        embedding_data = create_embedding(payload.text, payload.meta)
    except Exception as exc:  # noqa: BLE001
        logger.error("Embedding creation failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="Embedding service unavailable.") from exc

    record = {
        "translation_id": str(payload.translation_id)
        if payload.translation_id is not None
        else None,
        "text_chunk": embedding_data["content"],
        "embedding": embedding_data["embedding"],
        "meta": embedding_data["metadata"],
    }

    try:
        insert_record("tiwhanawhana.embeddings", record)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to log embedding: %s", exc)
        raise HTTPException(
            status_code=502, detail="Failed to record embedding.") from exc

    return EmbeddingResponse(
        embedding_length=len(embedding_data["embedding"]),
        translation_id=payload.translation_id,
        meta=embedding_data["metadata"],
    )
