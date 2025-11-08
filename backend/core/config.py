"""Pydantic settings wired to the secure environment loader."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import BaseSettings, Field

from .env_loader import load_env

_env_state = load_env()


class Settings(BaseSettings):
    """Application settings sourced from validated environment variables."""

    supabase_url: Optional[str] = Field(default=None, alias="DEN_URL")
    supabase_service_role_key: Optional[str] = Field(default=None, alias="DEN_API_KEY")
    supabase_anon_key: Optional[str] = Field(default=None, alias="TEPUNA_API_KEY")
    supabase_publishable_key: Optional[str] = Field(default=None, alias="TEPUNA_URL")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        allow_population_by_field_name = True

    lang: str = "mi_NZ.UTF-8"
    lc_all: str = "mi_NZ.UTF-8"

    offline_mode: bool = False
    database_url: Optional[str] = None
    memory_table: Optional[str] = None

    # OpenAI models
    translation_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # OCR / tooling
    tesseract_path: str | None = None

    # Supabase table aliases
    supabase_table_ocr_logs: str = "ocr_logs"
    supabase_table_translations: str = "translations"
    supabase_table_embeddings: str = "embeddings"
    supabase_table_memory: str = "ti_memory"

    def summary(self) -> Dict[str, Any]:  # noqa: D401
        """Return a masked snapshot of sensitive settings for diagnostics."""
        return {
            "context": _env_state.get("context", "local"),
            "loaded_keys": _env_state.get("loaded_keys", []),
            "masked_secrets": _env_state.get("masked_preview", {}),
            "utf8_status": _env_state.get("utf8_status", {}),
            "source": _env_state.get("source", "system"),
        }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_settings_summary() -> Dict[str, Any]:
    """Expose the masked summary without instantiating a new settings object."""
    return get_settings().summary()


settings = get_settings()
