# -*- coding: utf-8 -*-
"""Render intake service."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException

from Te_Po.routes.tiwhanawhana.intake_bridge import TiwhanawhanaIntakeBridge
from Te_Po.utils.logger import get_logger
from Te_Po.utils.middleware.utf8_enforcer import apply_utf8_middleware
from Te_Po.utils.supabase_client import supabase
from Te_Po.utils.supabase_schema import ensure_rongohia_schema

logger = get_logger("services.intake")

app = FastAPI(title="Tiwhanawhana Intake Service", version="1.0.0")
apply_utf8_middleware(app)
router = APIRouter(prefix="/api/intake", tags=["intake"])
_bridge: TiwhanawhanaIntakeBridge | None = None


def get_bridge() -> TiwhanawhanaIntakeBridge:
    global _bridge
    if _bridge is None:
        _bridge = TiwhanawhanaIntakeBridge()
    return _bridge


@app.on_event("startup")
async def startup_event() -> None:
    if supabase is not None:
        await asyncio.to_thread(ensure_rongohia_schema, supabase)
    logger.info("🌊 Intake service ready")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/status")
async def status() -> dict[str, str]:
    bridge = get_bridge()
    return {
        "service": "intake",
        "state": "awake",
        "intake_path": str(bridge.intake_path),
    }


@router.get("/status")
async def intake_status() -> dict[str, object]:
    bridge = get_bridge()
    documents = bridge.scan_intake_folder()
    return {
        "status": "active",
        "documents_found": len(documents),
        "documents": documents,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/scan")
async def scan_intake(background_tasks: BackgroundTasks) -> dict[str, object]:
    bridge = get_bridge()
    documents = bridge.scan_intake_folder()

    async def process_all() -> None:
        for doc in documents:
            result = await bridge.process_document(doc)
            if result.get("status") == "processed":
                record = result.get("record", {})
                bridge.request_whiro_audit(
                    record.get("id"),
                    record.get("full_content"),
                )

    def schedule_all() -> None:
        logger.info("Scheduling intake processing for %s document(s)", len(documents))
        asyncio.create_task(process_all())

    background_tasks.add_task(schedule_all)

    return {
        "status": "queued",
        "documents_queued": len(documents),
    }


@router.post("/process/{document_name}")
async def process_document(document_name: str, background_tasks: BackgroundTasks) -> dict[str, object]:
    bridge = get_bridge()
    doc_path = bridge.intake_path / document_name
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    document = {
        "file_path": str(doc_path),
        "file_name": doc_path.name,
        "file_type": doc_path.suffix,
        "size_bytes": doc_path.stat().st_size,
        "modified": datetime.fromtimestamp(doc_path.stat().st_mtime, tz=timezone.utc).isoformat(),
    }

    async def process_one() -> None:
        result = await bridge.process_document(document)
        if result.get("status") == "processed":
            record = result.get("record", {})
            bridge.request_whiro_audit(
                record.get("id"),
                record.get("full_content"),
            )

    def schedule_one() -> None:
        logger.info("Scheduling intake processing for %s", document_name)
        asyncio.create_task(process_one())

    background_tasks.add_task(schedule_one)

    return {
        "status": "queued",
        "file_name": document_name,
    }


@router.post("/start-continuous-scan")
async def start_continuous_scan(background_tasks: BackgroundTasks) -> dict[str, object]:
    bridge = get_bridge()

    def schedule_loop() -> None:
        logger.info("Scheduling continuous intake scan (30s interval)")
        asyncio.create_task(bridge.run_intake_loop(interval=30))

    background_tasks.add_task(schedule_loop)

    return {
        "status": "started",
        "interval_seconds": 30,
    }


app.include_router(router)
