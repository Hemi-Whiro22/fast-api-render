"""Centralised environment loader for sensitive configuration."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

logger = logging.getLogger("core.env_loader")

_ROOT = Path(__file__).resolve().parents[2]
_CRITICAL_KEYS = ("DEN_URL", "DEN_API_KEY", "OPENAI_API_KEY")
_SOURCE_KEY = "ENV_SOURCE"
_LOCALE_DEFAULT = "mi_NZ.UTF-8"
_LOG_PATH = _ROOT / "logs" / "env_validation.log"
_ENV_CONTEXT_VARS = ("RENDER", "RENDER_SERVICE_ID", "RENDER_INTERNAL_HOSTNAME")

_env_cache: dict[str, Any] | None = None


def _mask(value: str | None) -> str:
    """Return a masked preview of a secret without exposing its contents."""
    if not value:
        return "missing"
    prefix = value[:6]
    return f"{prefix}…"


def _detect_environment() -> str:
    for key in _ENV_CONTEXT_VARS:
        if os.getenv(key):
            return "render"
    return "local"


def _log_validation(
    loaded_keys: list[str],
    missing_keys: list[str],
    utf8_status: dict[str, str],
    utf8_verified: bool,
    masked_preview: dict[str, str],
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    context = _detect_environment()
    source = os.getenv(_SOURCE_KEY, "system")
    line = (
        f"{timestamp} context={context} source={source} "
        f"loaded_keys={loaded_keys} missing_keys={missing_keys} "
        f"utf8_status={utf8_status} UTF-8 verified: {utf8_verified} "
        f"masked_summary={masked_preview}\n"
    )
    with _LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line)


def load_env() -> dict[str, Any]:
    """Load environment variables with secure defaults and validation."""
    global _env_cache  # noqa: PLW0603

    if _env_cache is not None:
        return _env_cache

    # Ensure UTF-8 locale defaults are set before other imports rely on them.
    os.environ.setdefault("LANG", _LOCALE_DEFAULT)
    os.environ.setdefault("LC_ALL", _LOCALE_DEFAULT)

    # Load environment files in a deterministic order. Render env vars already present will win.
    source = []
    env_sources = [
        (_ROOT / ".env.local", ".env.local"),
        (_ROOT / ".env", ".env"),
        (_ROOT / ".mauri" / "tiwhanawhana.env", ".mauri/tiwhanawhana.env"),
        (_ROOT / ".mauri" / ".env", ".mauri/.env"),
        (_ROOT / ".mauri" / "rongohia" / ".env", ".mauri/rongohia/.env"),
    ]

    for path, label in env_sources:
        if path.exists():
            load_dotenv(dotenv_path=path, override=False)
            source.append(label)

    if source:
        os.environ[_SOURCE_KEY] = "+".join(source)
    else:
        os.environ.setdefault(_SOURCE_KEY, "system")

    loaded_keys: list[str] = []
    missing_keys: list[str] = []
    masked_preview: dict[str, str] = {}

    for key in _CRITICAL_KEYS:
        value = os.getenv(key)
        if value:
            loaded_keys.append(key)
            masked_preview[key] = _mask(value)
        else:
            missing_keys.append(key)
            masked_preview[key] = "missing"

    lang_value = os.getenv("LANG", _LOCALE_DEFAULT)
    lc_all_value = os.getenv("LC_ALL", _LOCALE_DEFAULT)
    utf8_verified = all(
        value and "utf-8" in value.lower() for value in (lang_value, lc_all_value)
    )
    utf8_status = {
        "LANG": lang_value,
        "LC_ALL": lc_all_value,
        "verified": utf8_verified,
    }

    if missing_keys:
        _log_validation(loaded_keys, missing_keys, utf8_status, utf8_verified, masked_preview)
        logger.warning(
            "Missing environment variables: %s (continuing with defaults)", ", ".join(missing_keys)
        )
    else:
        logger.info("Loaded environment keys: %s", masked_preview)
    
    logger.info("Locale configuration: %s", utf8_status)
    logger.info("UTF-8 verified: %s", utf8_verified)

    _log_validation(loaded_keys, missing_keys, utf8_status, utf8_verified, masked_preview)

    _env_cache = {
        "loaded_keys": loaded_keys,
        "missing_keys": missing_keys,
        "masked_preview": masked_preview,
        "utf8_status": utf8_status,
        "utf8_verified": utf8_verified,
        "context": _detect_environment(),
        "source": os.getenv(_SOURCE_KEY, "system"),
    }
    return _env_cache
