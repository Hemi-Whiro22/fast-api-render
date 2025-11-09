# -*- coding: utf-8 -*-
"""Render memory service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from Te_Po.config import get_settings
from Te_Po.utils.logger import get_logger
from Te_Po.utils.middleware.utf8_enforcer import apply_utf8_middleware
from Te_Po.utils.openai_client import generate_embedding
from Te_Po.utils.pgvector_client import search_embeddings
from Te_Po.utils.supabase_client import fetch_records, insert_record, supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.memory")

app = FastAPI(title="Tiwhanawhana Memory Service", version="1.0.0")
apply_utf8_middleware(app)


class RetrievePayload(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=25)
    min_similarity: float | None = Field(default=None, ge=0.0, le=1.0)


@app.on_event("startup")
async def startup_event() -> None:
    if supabase is not None:
        await run_in_threadpool(ensure_rongohia_schema, supabase)
    logger.info("🧠 Memory service ready")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
    return {"service": "memory", "state": "awake"}


@app.get("/api/memory/records")
async def list_records() -> list[dict[str, Any]]:
    settings = get_settings()
    table = settings.supabase_table_memory
    result = await run_in_threadpool(fetch_records, table)
    data = result.get("data") if isinstance(result, dict) else result
    if data is None:
        return []
    return data


@app.post("/api/memory/retrieve")
async def retrieve_memories(payload: RetrievePayload) -> list[dict[str, Any]]:
    try:
        embedding = await run_in_threadpool(generate_embedding, payload.query)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate query embedding: %s", exc)
        raise HTTPException(status_code=502, detail="Embedding generation failed.") from exc

    settings = get_settings()
    table = settings.memory_table or settings.supabase_table_memory
    try:
        results = await run_in_threadpool(
            search_embeddings,
            table,
            list(embedding),
            payload.top_k,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Vector search failed: %s", exc)
        raise HTTPException(status_code=502, detail="Vector search unavailable.") from exc

    filtered: list[dict[str, Any]] = []
    threshold = payload.min_similarity if payload.min_similarity is not None else 0.0
    for item in results:
        similarity = float(item.get("similarity") or 0.0)
        if payload.min_similarity is not None and similarity < threshold:
            continue
        filtered.append({
            "id": str(item.get("id", "")),
            "content": item.get("content"),
            "metadata": item.get("metadata"),
            "created_at": item.get("created_at"),
            "similarity": similarity,
        })

    insert_record(
        settings.supabase_table_memory,
        {
            "memory_type": "search_query",
            "content": payload.query,
            "embedding": list(embedding),
            "metadata": {
                "top_k": payload.top_k,
                "min_similarity": payload.min_similarity,
                "result_count": len(filtered),
            },
        },
    )

    return filtered
