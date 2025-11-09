# -*- coding: utf-8 -*-
"""Utilities for loading and sealing the Tiwhanawhana environment."""

from __future__ import annotations

import json
from io import StringIO
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from dotenv import dotenv_values
from supabase import Client, create_client

from Te_Po.utils.logger import get_logger

logger = get_logger(__name__)

__all__ = ["build_environment_seal", "seal_environment"]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_DIR = _REPO_ROOT / "backend"
_MAURI_DIR = _REPO_ROOT / ".mauri"
_MAURI_ENV_FILES = [
    _MAURI_DIR / "tiwhanawhana.env",
    _MAURI_DIR / ".env",
    _MAURI_DIR / "rongohia" / ".env",
]
_FIRST_ENV = _BACKEND_DIR / ".env"
_MAURI_FILE = _MAURI_DIR / "mauri.json"
_TRACE_FILE = _MAURI_DIR / "trace.json"
_CURRENT_SEAL_FILE = _REPO_ROOT / ".mauri" / "current_seal.json"
_SUPABASE_TABLES = [
    "ti_memory",
    "taonga_uploads",
    "pdf_summaries",
    "ocr_logs",
    "translations",
    "embeddings",
    "task_queue",
    "rongohia.user_profiles",
]


def _load_backend_env() -> Dict[str, str]:
    if not _FIRST_ENV.exists():
        return {}
    values = dotenv_values(_FIRST_ENV)
    return {key: value for key, value in values.items() if value is not None}


def _extract_json_object(text: str) -> tuple[str, tuple[int, int]] | tuple[None, tuple[int, int]]:
    start = text.find("{")
    if start == -1:
        return None, (0, 0)
    depth = 0
    for idx in range(start, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1], (start, idx + 1)
    return None, (0, 0)


def _load_mauri_env() -> Dict[str, Any]:
    env_payload: Dict[str, Any] = {}

    for candidate in _MAURI_ENV_FILES:
        if not candidate.exists():
            continue

        text = candidate.read_text(encoding="utf-8")
        json_block, (start, end) = _extract_json_object(text)
        if json_block:
            try:
                json_data = json.loads(json_block)
                if isinstance(json_data, dict):
                    env_payload.update(json_data)
                else:
                    logger.warning("JSON block in %s was not an object", candidate)
            except json.JSONDecodeError as exc:
                logger.warning("Unable to parse JSON block in %s: %s", candidate, exc)
        remainder = (text[:start] + text[end:]) if json_block else text
        dotenv_values_from_json = dotenv_values(stream=StringIO(remainder))
        env_payload.update({k: v for k, v in dotenv_values_from_json.items() if v is not None})

    return env_payload


def _load_mauri_metadata() -> Dict[str, Any]:
    mauri_data: Dict[str, Any] = {}
    if _MAURI_FILE.exists():
        try:
            raw = json.loads(_MAURI_FILE.read_text(encoding="utf-8"))
            mauri_data["glyph"] = raw.get("glyph")
            mauri_data["lineage"] = raw.get("whakapapa") or raw.get("lineage")
            mauri_data["mana_alignment"] = raw.get("mana_alignment")
        except json.JSONDecodeError as exc:
            logger.warning("Unable to parse %s: %s", _MAURI_FILE, exc)
    if _TRACE_FILE.exists():
        try:
            trace = json.loads(_TRACE_FILE.read_text(encoding="utf-8"))
            mauri_data["last_seal"] = trace.get("timestamp")
            mauri_data.setdefault("glyph", trace.get("glyph"))
        except json.JSONDecodeError as exc:
            logger.warning("Unable to parse %s: %s", _TRACE_FILE, exc)
    return mauri_data


def _current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_serialisable(payload: Dict[str, Any]) -> Dict[str, Any]:
    serialisable: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            serialisable[key] = value
        else:
            serialisable[key] = json.loads(json.dumps(value, default=str))
    return serialisable


def _sync_to_supabase(seal: Dict[str, Any], env_data: Dict[str, str]) -> bool:
    url = env_data.get("DEN_URL")
    key = env_data.get("DEN_API_KEY") or env_data.get("TEPUNA_API_KEY")
    if not url or not key:
        return False
    try:
        client: Client = create_client(url, key)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Supabase client initialisation failed: %s", exc)
        return False
    payload = {
        "context": seal["context"],
        "seal": seal,
        "updated_at": seal["timestamp"],
    }
    try:
        client.table("ti_env_seals").upsert(payload, on_conflict="context").execute()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("Supabase upsert failed: %s", exc)
        return False


def build_environment_seal(context: str = "local") -> Dict[str, Any]:
    env_data: Dict[str, Any] = {}
    env_data.update(_load_backend_env())
    env_data.update(_load_mauri_env())

    mauri_info = _load_mauri_metadata()
    seal = {
        "context": context,
        "environment": env_data,
        "supabase_schema": "tiwhanawhana",
        "supabase_tables": list(_SUPABASE_TABLES),
        "mauri": {
            "glyph": mauri_info.get("glyph"),
            "lineage": mauri_info.get("lineage"),
            "mana_alignment": mauri_info.get("mana_alignment"),
            "last_seal": mauri_info.get("last_seal"),
        },
        "timestamp": _current_utc_timestamp(),
    }
    return seal


def seal_environment(context: str = "local") -> Dict[str, Any]:
    seal = build_environment_seal(context)
    _CURRENT_SEAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    serialisable_seal = _ensure_serialisable(seal)
    _CURRENT_SEAL_FILE.write_text(
        json.dumps(serialisable_seal, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    env_data = seal["environment"]
    synced = _sync_to_supabase(serialisable_seal, env_data)
    print(
        f"🌊 Tiwhanawhana environment sealed with {len(env_data)} variables and "
        f"{len(_SUPABASE_TABLES)} tables."
    )
    if synced:
        logger.info("Environment seal synchronised with Supabase.")
    else:
        logger.info("Environment seal stored locally; Supabase sync skipped or failed.")
    return seal


if __name__ == "__main__":
    seal_environment()
