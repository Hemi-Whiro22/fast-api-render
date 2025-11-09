"""OpenAI client helpers."""
from functools import lru_cache
import hashlib
from typing import Sequence

from openai import OpenAI

from Te_Po.core.config import get_settings




@lru_cache()
def get_openai_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key is not configured.")
    return OpenAI(api_key=settings.openai_api_key)


def translate_text(
    text: str,
    target_language: str,
    context: str | None = None,
) -> str:
    settings = get_settings()
    if settings.offline_mode:
        prefix = f"[{target_language}]"
        if context:
            prefix += " (offline context)"
        return f"{prefix} {text}"
    client = get_openai_client()
    system_message = (
        f"Translate the user's text into {target_language} while preserving nuance and macrons."
    )
    if context:
        system_message += f" Context: {context.strip()}"
    response = client.responses.create(
        model=settings.translation_model,
        input=[
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": text},
        ],
    )
    return response.output_text.strip()


def generate_embedding(text: str) -> Sequence[float]:
    settings = get_settings()
    if settings.offline_mode:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        # Produce deterministic pseudo embedding of length 32
        return [byte / 255.0 for byte in digest[:32]]
    client = get_openai_client()
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=text,
    )
    return response.data[0].embedding
