# -*- coding: utf-8 -*-
"""Render OCR microservice entrypoint."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError
import pytesseract

from Te_Po.config import get_settings
from Te_Po.services.tiwhanawhana import perform_ocr
from Te_Po.utils.logger import get_logger
from Te_Po.utils.middleware.utf8_enforcer import apply_utf8_middleware
from Te_Po.utils.openai_client import generate_embedding
from Te_Po.utils.pgvector_client import store_embedding
from Te_Po.utils.supabase_client import insert_record, supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.ocr")

app = FastAPI(title="Tiwhanawhana OCR Service", version="1.0.0")
apply_utf8_middleware(app)


@app.on_event("startup")
async def startup_event() -> None:
    if supabase is not None:
        await run_in_threadpool(ensure_rongohia_schema, supabase)
    logger.info("🌀 OCR service ready")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
    return {"service": "ocr", "state": "awake"}


@app.post("/api/ocr/extract")
async def extract_text(file: UploadFile = File(...)) -> dict[str, object]:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = await run_in_threadpool(perform_ocr, data)
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Invalid image payload.") from exc
    except pytesseract.TesseractNotFoundError as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Tesseract not available.") from exc

    settings = get_settings()
    ocr_table = settings.supabase_table_ocr_logs
    insert_record(
        ocr_table,
        {
            "content": result["text"],
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "bytes": len(data),
            },
        },
    )

    memory_table = settings.memory_table or settings.supabase_table_memory
    if memory_table:
        embedding = await run_in_threadpool(generate_embedding, result["text"])
        await run_in_threadpool(
            store_embedding,
            memory_table,
            result["text"],
            list(embedding),
            {"source": "ocr", "filename": file.filename},
        )

    return {"text": result["text"], "language": result["language"]}
