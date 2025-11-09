# -*- coding: utf-8 -*-
"""Render embed service."""

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
from Te_Po.utils.pgvector_client import store_embedding
from Te_Po.utils.supabase_client import insert_record, supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.embed")

app = FastAPI(title="Tiwhanawhana Embed Service", version="1.0.0")
apply_utf8_middleware(app)


class EmbeddingPayload(BaseModel):
	text: str = Field(..., min_length=1)
	metadata: dict[str, Any] | None = None


@app.on_event("startup")
async def startup_event() -> None:
	if supabase is not None:
		await run_in_threadpool(ensure_rongohia_schema, supabase)
	logger.info("🧠 Embed service ready")


@app.get("/health")
async def health() -> dict[str, str]:
	return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
	return {"service": "embed", "state": "awake"}


@app.post("/api/embed/create")
async def create_embedding_route(payload: EmbeddingPayload) -> dict[str, object]:
	try:
		embedding = await run_in_threadpool(generate_embedding, payload.text)
	except Exception as exc:  # noqa: BLE001
		logger.error("Embedding generation failed: %s", exc)
		raise HTTPException(status_code=502, detail="Embedding generation failed.") from exc

	vector = list(embedding)
	metadata = payload.metadata or {}

	settings = get_settings()
	insert_record(
		settings.supabase_table_embeddings,
		{
			"content": payload.text,
			"metadata": metadata,
			"embedding": vector,
		},
	)

	try:
		record_id = await run_in_threadpool(
			store_embedding,
			settings.supabase_table_embeddings,
			payload.text,
			vector,
			metadata,
		)
	except Exception as exc:  # noqa: BLE001
		logger.error("Vector store write failed: %s", exc)
		raise HTTPException(status_code=500, detail="Vector storage failed.") from exc

	return {
		"embedding_id": record_id,
		"vector_length": len(vector),
		"timestamp": datetime.now(timezone.utc).isoformat(),
	}
