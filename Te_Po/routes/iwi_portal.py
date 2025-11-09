# -*- coding: utf-8 -*-
"""
Iwi Portal Routes — OCR, Translation, Archive, Ingestion
Bridges Alpha-Den (operational) and Te Puna (archive, read-only).
"""

from datetime import datetime
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from PIL import Image
import pytesseract

from Te_Po.utils.logger import get_logger
from Te_Po.utils.openai_client import generate_embedding
from Te_Po.utils.supabase_client import (
    afetch_records,
    ainsert_record,
    SupabaseResponse,
)

router = APIRouter()
logger = get_logger(__name__)


# === SCHEMAS ===

class OCRRequest(BaseModel):
    """File upload metadata for OCR."""
    pass


class OCRResponse(BaseModel):
    """OCR result with confidence score."""
    filename: str
    text: str
    confidence: float
    created_at: datetime
    saved_to: str = "Alpha-Den"


class TranslateRequest(BaseModel):
    """Text translation request."""
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"


class TranslateResponse(BaseModel):
    """Translation result."""
    original_text: str
    translated_text: str
    confidence: float = 0.9
    target_lang: str
    created_at: datetime
    saved_to: str = "Alpha-Den"


class ArchiveRecord(BaseModel):
    """Record from Te Puna archive."""
    id: str
    title: str
    content: str
    source: str
    created_at: datetime


class IngestRequest(BaseModel):
    """Ingestion metadata."""
    title: str
    content: str
    source: str
    file_type: str = "text"
    metadata: Optional[dict] = None


# === ROUTES ===

@router.post("/ocr", response_model=OCRResponse)
async def upload_ocr(file: UploadFile = File(...)) -> OCRResponse:
    """
    Upload image, extract text via pytesseract, save to Alpha-Den.
    Supports Māori language extraction.
    """
    filename = file.filename or "upload"
    logger.info("🪶 Received OCR upload: %s", filename)
    
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    try:
        # Extract text from image
        image = Image.open(BytesIO(data))
        text = await run_in_threadpool(
            pytesseract.image_to_string,
            image,
            lang="mri+eng"  # Māori + English
        )
        
        # Extract confidence
        ocr_data = await run_in_threadpool(
            pytesseract.image_to_data,
            image,
            output_type=pytesseract.Output.DICT
        )
        confidences = [
            float(conf) for conf in ocr_data.get("conf", [])
            if conf not in {"-1", -1}
        ]
        confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0
        
        # Save to Alpha-Den
        record = {
            "filename": filename,
            "content": text.strip(),
            "confidence": round(confidence, 4),
            "content_type": file.content_type,
            "bytes": len(data),
            "source": "ocr_portal",
        }
        
        result = await ainsert_record("den", "ocr_logs", record)
        if not result.ok:
            logger.warning("⚠️ Failed to save OCR result: %s", result.error)
        
        logger.info("✅ OCR processed: %s (confidence: %.2f%%)", filename, confidence * 100)
        
        return OCRResponse(
            filename=filename,
            text=text.strip()[:500],  # Return first 500 chars
            confidence=confidence,
            created_at=datetime.utcnow(),
            saved_to="Alpha-Den"
        )
    
    except Exception as e:
        logger.error("❌ OCR failed: %s", e)
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}") from e


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(payload: TranslateRequest) -> TranslateResponse:
    """
    Translate text via OpenAI, save result to Alpha-Den.
    Supports Māori ↔ English bidirectional translation.
    """
    logger.info("🪶 Translation request: %s → %s", payload.source_lang, payload.target_lang)
    
    if not payload.text or len(payload.text) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    try:
        # TODO: Implement OpenAI translation
        # For now, stub with placeholder
        translated = f"[Translation pending: {payload.text[:50]}...]"
        
        # Save to Alpha-Den
        record = {
            "original_text": payload.text,
            "translated_text": translated,
            "source_lang": payload.source_lang,
            "target_lang": payload.target_lang,
            "source": "portal_translate",
        }
        
        result = await ainsert_record("den", "translations", record)
        if not result.ok:
            logger.warning("⚠️ Failed to save translation: %s", result.error)
        
        logger.info("✅ Translation saved to Alpha-Den")
        
        return TranslateResponse(
            original_text=payload.text,
            translated_text=translated,
            target_lang=payload.target_lang,
            created_at=datetime.utcnow(),
            saved_to="Alpha-Den"
        )
    
    except Exception as e:
        logger.error("❌ Translation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}") from e


@router.get("/archive")
async def fetch_archive(limit: int = 20) -> SupabaseResponse:
    """
    Fetch records from Te Puna (read-only iwi knowledge archive).
    """
    logger.info("🪶 Fetching archive from Te Puna (limit: %d)", limit)
    
    try:
        result = await afetch_records(
            project="tepuna",
            table="summaries",
            select="*",
            limit=limit
        )
        
        if result.ok:
            logger.info("✅ Archive fetch succeeded: %d records", result.count)
        else:
            logger.warning("⚠️ Archive fetch warning: %s", result.error)
        
        return result
    
    except Exception as e:
        logger.error("❌ Archive fetch failed: %s", e)
        return SupabaseResponse(
            data=[],
            error=f"Archive fetch failed: {str(e)}",
            ok=False
        )


@router.post("/ingest")
async def ingest_record(payload: IngestRequest) -> SupabaseResponse:
    """
    Accept uploaded content metadata and save to Alpha-Den.
    Used for bulk ingestion workflows.
    """
    logger.info("🪶 Ingest request: %s (%s)", payload.title, payload.file_type)
    
    if not payload.title or len(payload.title) == 0:
        raise HTTPException(status_code=400, detail="Title cannot be empty.")
    
    try:
        record = {
            "title": payload.title,
            "content": payload.content,
            "source": payload.source,
            "file_type": payload.file_type,
            "metadata": payload.metadata or {},
            "ingested_at": datetime.utcnow().isoformat(),
        }
        
        result = await ainsert_record("den", "memory_logs", record)
        
        if result.ok:
            logger.info("✅ Ingest succeeded: %s", payload.title)
        else:
            logger.error("❌ Ingest failed: %s", result.error)
        
        return result
    
    except Exception as e:
        logger.error("❌ Ingest error: %s", e)
        return SupabaseResponse(
            data=None,
            error=f"Ingest failed: {str(e)}",
            ok=False
        )


@router.get("/status")
async def portal_status() -> dict:
    """Health check for Iwi Portal."""
    return {
        "status": "online",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ["ocr", "translate", "archive", "ingest"],
        "den_status": "operational",
        "tepuna_status": "read-only",
    }
