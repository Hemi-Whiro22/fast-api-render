# -*- coding: utf-8 -*-
"""OCR routes."""
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError
import pytesseract
from pydantic import BaseModel

from backend.core.config import get_settings
from backend.utils.logger import get_logger
from backend.utils.openai_client import generate_embedding
from backend.utils.pgvector_client import store_embedding
from backend.utils.supabase_client import insert_record

router = APIRouter()
logger = get_logger(__name__)


class OCRResponse(BaseModel):
    filename: str
    text: str
    confidence: float
    created_at: datetime


def _extract_text(image_bytes: bytes) -> tuple[str, float]:
    with Image.open(BytesIO(image_bytes)) as image:
        text = pytesseract.image_to_string(image)
        data = pytesseract.image_to_data(
            image, output_type=pytesseract.Output.DICT)
    confidences = [float(conf) for conf in data.get(
        "conf", []) if conf not in {"-1", -1}]
    confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return text, confidence


@router.post("/", response_model=OCRResponse)
async def upload_ocr(file: UploadFile = File(...)) -> OCRResponse:
    settings = get_settings()
    filename = file.filename or "upload"
    logger.info("Received OCR upload: %s", filename)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if settings.tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path
    try:
        text, confidence = await run_in_threadpool(_extract_text, data)
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=400, detail="Uploaded file is not a valid image.") from exc
    except pytesseract.TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=500, detail="Tesseract OCR binary is not available on the server.") from exc

    confidence_normalized = round(confidence / 100.0, 4)
    metadata = {
        "filename": filename,
        "content_type": file.content_type,
        "bytes": len(data),
        "confidence": confidence_normalized,
    }

    ocr_table = settings.supabase_table_ocr_logs or "ocr_logs"

    record = insert_record(
        ocr_table,
        {
            "content": text,
            "metadata": metadata,
        },
    )

    memory_table = settings.memory_table

    if memory_table:
        embedding = await run_in_threadpool(generate_embedding, text)
        embedding_vector = list(embedding)
        try:
            await run_in_threadpool(
                store_embedding,
                memory_table,
                text,
                embedding_vector,
                {"source": "ocr", **metadata},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist OCR embedding: %s", exc)

    created_at = record.get("created_at", datetime.utcnow())
    return OCRResponse(
        filename=filename,
        text=text.strip(),
        confidence=confidence_normalized,
        created_at=created_at,
    )
