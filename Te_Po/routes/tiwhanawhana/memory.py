# -*- coding: utf-8 -*-
"""Tiwhanawhana memory routes."""
from fastapi import APIRouter, HTTPException, Query

from Te_Po.services.tiwhanawhana import search_memory
from Te_Po.utils.logger import get_logger
from Te_Po.utils.supabase_client import insert_record

router = APIRouter(prefix="/tiwhanawhana/memory",
                   tags=["Tiwhanawhana - Memory"])
logger = get_logger(__name__)


@router.get("/search")
async def memory_search(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=50)) -> dict[str, object]:
    try:
        search_payload = search_memory(q, limit)
    except Exception as exc:  # noqa: BLE001
        logger.error("Memory search failed: %s", exc)
        raise HTTPException(
            status_code=502, detail="Memory search unavailable.") from exc

    record = {
        "memory_type": "search_query",
        "content": q,
        "embedding": search_payload["query_embedding"],
        "related_task": None,
        "meta": {
            "limit": limit,
            "result_count": len(search_payload["results"]),
        },
    }

    try:
        insert_record("tiwhanawhana.ti_memory", record)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to log memory search: %s", exc)
        raise HTTPException(
            status_code=502, detail="Failed to log memory query.") from exc

    return {
        "query": q,
        "results": search_payload["results"],
    }
