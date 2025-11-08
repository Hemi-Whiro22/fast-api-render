# -*- coding: utf-8 -*-
"""Render-ready FastAPI entrypoint with secure environment introspection."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI

from backend.core.config import get_settings, get_settings_summary
from backend.core.env_loader import load_env
from backend.routes import embed, memory, ocr, translate
from backend.routes.tiwhanawhana import intake, mauri
from backend.utils.env_validator import validate_environment_and_locale
from backend.utils.logger import get_logger
from backend.utils.middleware.utf8_enforcer import apply_utf8_middleware
from backend.utils.safety_guard import safety_guard
from contextlib import asynccontextmanager

# Ensure secrets and locale are loaded before the application boots.
_env_state = load_env()
_ = get_settings()
_logger = get_logger("core.main")
_logger.info("Masked environment preview: %s", _env_state["masked_preview"])
_logger.info("UTF-8 verified: %s", _env_state.get("utf8_verified"))
_logger.info("Environment source precedence: %s", _env_state.get("source"))

validation_results = validate_environment_and_locale()

app = FastAPI(title="Tiwhanawhana Core Service", version="1.0.0")
apply_utf8_middleware(app)

app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
app.include_router(translate.router, prefix="/translate", tags=["Translate"])
app.include_router(embed.router, prefix="/embed", tags=["Embed"])
app.include_router(memory.router, prefix="/memory", tags=["Memory"])
app.include_router(mauri.router, prefix="/mauri", tags=["Mauri"])
app.include_router(intake.router, tags=["Intake"])


@app.on_event("startup")
async def startup_event() -> None:
    summary = get_settings_summary()
    _logger.info("Environment summary: %s", summary)
    if validation_results["overall_ready"]:
        _logger.info("Startup validation passed — UTF-8 enforced and secrets loaded.")
    else:
        _logger.warning("Startup validation reported warnings: %s", validation_results)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/env/health")
async def env_health() -> dict[str, object]:
    summary = get_settings_summary()
    return {
        "utf8_status": summary.get("utf8_status", {}),
        "loaded_keys": summary.get("loaded_keys", []),
        "source": summary.get("source", "system"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "awake", "message": "Tiwhanawhana core is flowing 🌊"}