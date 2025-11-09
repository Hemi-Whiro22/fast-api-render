# -*- coding: utf-8 -*-
"""Tiwhanawhana mauri routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from Te_Po.services.tiwhanawhana import log_mauri
from Te_Po.utils.logger import get_logger
from Te_Po.utils.supabase_client import fetch_latest, insert_record

router = APIRouter(prefix="/tiwhanawhana/mauri", tags=["Tiwhanawhana - Mauri"])
logger = get_logger(__name__)


class MauriLogRequest(BaseModel):
    phase: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    tohu_id: str | None = None
    meta: dict[str, object] | None = None


@router.get("/status")
async def mauri_status() -> dict[str, object]:
    try:
        latest = fetch_latest("tiwhanawhana.mauri_logs")
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch mauri status: %s", exc)
        raise HTTPException(
            status_code=502, detail="Mauri status unavailable.") from exc

    if not latest:
        return {"status": "unknown", "message": "No mauri logs found."}

    return {
        "status": latest.get("phase", "unknown"),
        "message": latest.get("message"),
        "meta": latest.get("meta", {}),
    }


@router.post("/log")
async def mauri_log(payload: MauriLogRequest) -> dict[str, object]:
    record = log_mauri(
        payload.phase,
        payload.message,
        tohu_id=payload.tohu_id,
        meta=payload.meta,
    )

    try:
        result = insert_record("den", "mauri_logs", record)
        if result.get("error"):
            raise Exception(result["error"])
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to log mauri entry: %s", exc)
        raise HTTPException(
            status_code=502, detail="Failed to log mauri entry.") from exc

    return {
        "phase": payload.phase,
        "message": payload.message,
        "meta": record.get("meta", {}),
    }
