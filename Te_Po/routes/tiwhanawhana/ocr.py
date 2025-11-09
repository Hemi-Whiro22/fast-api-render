# -*- coding: utf-8 -*-
"""Tiwhanawhana OCR route."""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from Te_Po.services.tiwhanawhana import OCRImageError, OCRServiceError, perform_ocr
from Te_Po.utils.logger import get_logger
from Te_Po.utils.supabase_client import insert_record

router = APIRouter(prefix="/tiwhanawhana/ocr", tags=["Tiwhanawhana - OCR"])
logger = get_logger(__name__)


@router.post("/")
async def upload_image(file: UploadFile = File(...)) -> dict[str, str]:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = await run_in_threadpool(perform_ocr, data)
    except OCRImageError as exc:
        raise HTTPException(
            status_code=400, detail="Invalid image file.") from exc
    except OCRServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected OCR failure: %s", exc)
        raise HTTPException(
            status_code=502, detail="OCR service unavailable.") from exc

    payload = {
        "file_name": file.filename,
        "file_url": None,
        "text_content": result["text"],
        "language_detected": result["language"],
        "meta": {
            "content_type": file.content_type,
            "bytes": len(data),
        },
    }

    try:
        insert_record("tiwhanawhana.ocr_logs", payload)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to log OCR upload: %s", exc)
        raise HTTPException(
            status_code=502, detail="Failed to log OCR result.") from exc

    return {
        "text": result["text"],
        "language": result["language"],
    }
