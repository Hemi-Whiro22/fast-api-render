# -*- coding: utf-8 -*-
"""Embedding routes."""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from Te_Po.config import get_settings
from Te_Po.utils.logger import get_logger
from Te_Po.utils.openai_client import generate_embedding
from Te_Po.utils.pgvector_client import get_pgvector_client
from Te_Po.utils.supabase_client import insert_record

router = APIRouter()
logger = get_logger(__name__)


class EmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1)
    metadata: Dict[str, Any] | None = None


class EmbeddingResponse(BaseModel):
    embedding_id: str
    created_at: datetime


@router.post("/", response_model=EmbeddingResponse)
async def create_embedding(payload: EmbeddingRequest) -> EmbeddingResponse:
    settings = get_settings()
    logger.info("Creating embedding (%s characters)", len(payload.text))

    try:
        embedding = await run_in_threadpool(generate_embedding, payload.text)
    except Exception as exc:  # noqa: BLE001
        logger.error("Embedding generation failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="Embedding generation failed.") from exc

    embedding_vector = list(embedding)
    metadata = payload.metadata or {}

    table = settings.supabase_table_embeddings or "embeddings"

    record = insert_record(
        table,
        {
            "content": payload.text,
            "metadata": metadata,
            "embedding": embedding_vector,
        },
    )

    pgvector_client = get_pgvector_client()
    try:
        embedding_id = await run_in_threadpool(
            pgvector_client.insert_embedding,
            table,
            payload.text,
            embedding_vector,
            metadata,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to persist embedding in pgvector: %s", exc)
        raise HTTPException(
            status_code=500, detail="Could not persist embedding.") from exc

    created_at = record.get("created_at", datetime.utcnow())
    return EmbeddingResponse(embedding_id=embedding_id, created_at=created_at)
