#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌊 Tiwhanawhana Intake Endpoint
==============================
FastAPI routes to handle document intake from kaitiaki-intake folder
Integrates with Tiwhanawhana watchdog and Whiro auditor
"""

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime, timezone
import logging
import asyncio
import json

from Te_Po.routes.tiwhanawhana.intake_bridge import TiwhanawhanaIntakeBridge

logger = logging.getLogger("tiwhanawhana.intake")

router = APIRouter(prefix="/intake", tags=["intake"])

# Global bridge instance
_bridge = None

def get_bridge():
    """Get or create intake bridge"""
    global _bridge
    if _bridge is None:
        _bridge = TiwhanawhanaIntakeBridge()
    return _bridge


@router.get("/status")
async def intake_status():
    """Get intake folder status"""
    try:
        bridge = get_bridge()
        documents = bridge.scan_intake_folder()
        
        return {
            "status": "active",
            "intake_path": str(bridge.intake_path),
            "documents_found": len(documents),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "documents": documents
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@router.post("/scan")
async def scan_intake(background_tasks: BackgroundTasks):
    """Scan intake folder and process new documents"""
    try:
        bridge = get_bridge()
        documents = bridge.scan_intake_folder()
        
        # Process in background
        async def process_all():
            for doc in documents:
                result = await bridge.process_document(doc)
                if result["status"] == "processed":
                    bridge.request_whiro_audit(
                        result["record"]["id"],
                        result["record"]["full_content"]
                    )
        
        def schedule_process_all() -> None:
            logger.info("Scheduling intake processing for %s document(s)", len(documents))
            asyncio.create_task(process_all())

        background_tasks.add_task(schedule_process_all)
        
        return {
            "status": "scanning",
            "documents_queued": len(documents),
            "message": "Documents queued for processing. Check status for results."
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@router.post("/process/{document_name}")
async def process_document(document_name: str, background_tasks: BackgroundTasks):
    """Process a specific document from intake folder"""
    try:
        bridge = get_bridge()
        
        # Find the document
        doc_path = bridge.intake_path / document_name
        if not doc_path.exists():
            return JSONResponse(
                status_code=404,
                content={"status": "not_found", "error": f"Document not found: {document_name}"}
            )
        
        # Get document info
        doc_info = {
            "file_path": str(doc_path),
            "file_name": doc_path.name,
            "file_type": doc_path.suffix,
            "size_bytes": doc_path.stat().st_size,
            "modified": datetime.fromtimestamp(
                doc_path.stat().st_mtime,
                tz=timezone.utc
            ).isoformat()
        }
        
        # Process in background
        async def process_task():
            result = await bridge.process_document(doc_info)
            if result["status"] == "processed":
                bridge.request_whiro_audit(
                    result["record"]["id"],
                    result["record"]["full_content"]
                )
        
        def schedule_process_one() -> None:
            logger.info("Scheduling intake processing for %s", document_name)
            asyncio.create_task(process_task())

        background_tasks.add_task(schedule_process_one)
        
        return {
            "status": "processing",
            "file_name": document_name,
            "message": "Document queued for processing"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@router.get("/documents")
async def list_documents():
    """List all documents in intake folder"""
    try:
        bridge = get_bridge()
        documents = bridge.scan_intake_folder()
        
        return {
            "status": "success",
            "count": len(documents),
            "documents": documents,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@router.post("/start-continuous-scan")
async def start_continuous_scan(background_tasks: BackgroundTasks):
    """Start continuous intake scanning in background"""
    try:
        bridge = get_bridge()
        
        # Add to background tasks
        def schedule_continuous_loop() -> None:
            logger.info("Scheduling continuous intake scan (every %s s)", 30)
            asyncio.create_task(bridge.run_intake_loop(interval_seconds=30))

        background_tasks.add_task(schedule_continuous_loop)
        
        return {
            "status": "started",
            "message": "Continuous intake scanning started",
            "check_interval_seconds": 30,
            "note": "Check /intake/status for current documents"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )
