# -*- coding: utf-8 -*-
"""Memory routes."""
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from Te_Po.config import get_settings
from Te_Po.utils.logger import get_logger
from Te_Po.utils.supabase_client import fetch_records
from Te_Po.utils.openai_client import generate_embedding
from Te_Po.utils.pgvector_client import search_embeddings

router = APIRouter()
logger = get_logger(__name__)


class MemoryRetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=25)
    min_similarity: float | None = Field(default=None, ge=0.0, le=1.0)


class MemoryRetrieveResult(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] | None = None
    created_at: datetime | None = None
    similarity: float


@router.get("/")
async def list_memories() -> List[Dict[str, object]]:
    settings = get_settings()
    table = settings.supabase_table_memory or "ti_memory"
    try:
        records = fetch_records(table)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load memory records: %s", exc)
        raise HTTPException(
            status_code=502, detail="Unable to fetch memory records.") from exc
    return records


@router.post("/retrieve", response_model=List[MemoryRetrieveResult])
async def retrieve_memories(payload: MemoryRetrieveRequest) -> List[MemoryRetrieveResult]:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query text is required.")

    settings = get_settings()
    table = settings.memory_table or settings.supabase_table_memory or "ti_memory"

    try:
        embedding = await run_in_threadpool(generate_embedding, payload.query)
        results = await run_in_threadpool(
            search_embeddings,
            table,
            list(embedding),
            payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Vector retrieval failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="Vector search is unavailable.") from exc

    filtered: List[MemoryRetrieveResult] = []
    min_similarity = payload.min_similarity if payload.min_similarity is not None else 0.0
    for item in results:
        similarity = float(item.get("similarity") or 0.0)
        if payload.min_similarity is not None and similarity < min_similarity:
            continue
        metadata_value = item.get("metadata")
        if metadata_value is not None and not isinstance(metadata_value, dict):
            try:
                metadata_value = dict(metadata_value)
            except (TypeError, ValueError):
                metadata_value = {"value": metadata_value}
        filtered.append(
            MemoryRetrieveResult(
                id=str(item.get("id", "")),
                content=str(item.get("content", "")),
                metadata=metadata_value,
                created_at=item.get("created_at"),
                similarity=similarity,
            )
        )

    return filtered
