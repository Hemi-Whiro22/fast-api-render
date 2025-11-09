# -*- coding: utf-8 -*-
"""Core service helpers for Tiwhanawhana routes."""
from __future__ import annotations

from io import BytesIO
import json
from typing import Any, Dict, List

from PIL import Image, UnidentifiedImageError
import pytesseract

from Te_Po.config import get_settings
from Te_Po.utils.logger import get_logger
from Te_Po.utils.offline_store import cosine_similarity
from Te_Po.utils.openai_client import generate_embedding
from Te_Po.utils.supabase_client import fetch_records

logger = get_logger(__name__)


class OCRImageError(ValueError):
    """Raised when the provided bytes are not a valid image."""


class OCRServiceError(RuntimeError):
    """Raised when the OCR service cannot be executed."""


def perform_ocr(image_bytes: bytes) -> Dict[str, str]:
    settings = get_settings()
    if settings.tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_path

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            text = pytesseract.image_to_string(image)
    except UnidentifiedImageError as exc:  # noqa: BLE001
        raise OCRImageError("Invalid image payload.") from exc
    except pytesseract.TesseractNotFoundError as exc:  # noqa: BLE001
        raise OCRServiceError("Tesseract binary not available.") from exc
    except Exception as exc:  # noqa: BLE001
        raise OCRServiceError("Unexpected OCR failure.") from exc

    return {
        "text": text.strip(),
        "language": "auto",
    }


def create_embedding(text: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    try:
        vector = list(generate_embedding(text))
    except Exception as exc:  # noqa: BLE001
        logger.error("Embedding helper failed: %s", exc)
        raise
    return {
        "content": text,
        "embedding": vector,
        "metadata": metadata or {},
    }


def _deserialize_embedding(embedding: Any) -> List[float] | None:
    if embedding is None:
        return None
    if isinstance(embedding, list):
        return [float(value) for value in embedding]
    if isinstance(embedding, str):
        try:
            parsed = json.loads(embedding)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, list):
            return [float(value) for value in parsed]
    return None


def search_memory(query: str, top_k: int = 5) -> Dict[str, Any]:
    try:
        query_vector = list(generate_embedding(query))
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to generate query embedding: %s", exc)
        raise

    try:
        records = fetch_records("tiwhanawhana.ti_memory")
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch memory records: %s", exc)
        raise

    scored: List[tuple[float, Dict[str, Any]]] = []
    for record in records:
        embedding = _deserialize_embedding(record.get("embedding"))
        if not embedding:
            continue
        try:
            score = cosine_similarity(query_vector, embedding)
        except ValueError:
            continue
        enriched = dict(record)
        enriched["similarity"] = float(score)
        scored.append((float(score), enriched))

    scored.sort(key=lambda item: item[0], reverse=True)
    results = [item[1] for item in scored[:top_k]]
    return {
        "query_embedding": query_vector,
        "results": results,
    }


def log_mauri(
    phase: str,
    message: str,
    *,
    tohu_id: str | None = None,
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "phase": phase,
        "message": message,
        "tohu_id": tohu_id,
        "meta": meta or {},
    }
