"""pgvector helpers for Tiwhanawhana."""
from functools import lru_cache
import re
from typing import Any, Dict, List, Sequence

import psycopg
from psycopg import sql
from pgvector.psycopg import register_vector
from psycopg.types.json import Json

from Te_Po.core.config import get_settings

from Te_Po.utils import offline_store

_TABLE_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _identifier_parts(name: str) -> tuple[str, ...]:
    parts = [part.strip() for part in name.split(".") if part.strip()]
    if not parts or len(parts) > 2:
        raise ValueError(f"Identifier '{name}' is not permitted.")
    for part in parts:
        if not _TABLE_NAME_PATTERN.match(part):
            raise ValueError(f"Identifier '{name}' is not permitted.")
    return tuple(parts)


class PGVectorClient:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def _connect(self) -> psycopg.Connection:
        conn = psycopg.connect(self._dsn, autocommit=True)
        register_vector(conn)
        return conn

    def insert_embedding(
        self,
        table: str,
        content: str,
        embedding: Sequence[float],
        metadata: Dict[str, Any] | None = None,
    ) -> str:
        identifier = _identifier_parts(table)
        metadata_json = Json(metadata or {})
        with self._connect() as conn:
            with conn.cursor() as cursor:
                query = sql.SQL(
                    "INSERT INTO {table} (content, embedding, metadata) "
                    "VALUES (%s, %s, %s) RETURNING id"
                ).format(table=sql.Identifier(*identifier))
                cursor.execute(query, (content, embedding, metadata_json))
                row = cursor.fetchone()
        if not row:
            raise RuntimeError("Failed to persist embedding record.")
        return str(row[0])

    def search_embeddings(
        self,
        table: str,
        embedding: Sequence[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        identifier = _identifier_parts(table)
        with self._connect() as conn, conn.cursor() as cursor:
            query = sql.SQL(
                "SELECT id, content, metadata, created_at, "
                "1 - (embedding <=> %s::vector) AS similarity "
                "FROM {table} "
                "ORDER BY embedding <=> %s::vector "
                "LIMIT %s"
            ).format(table=sql.Identifier(*identifier))
            cursor.execute(query, (embedding, embedding, top_k))
            rows = cursor.fetchall()
        results: List[Dict[str, Any]] = []
        for row in rows:
            metadata = row[2]
            if isinstance(metadata, dict):
                metadata_obj = metadata
            else:
                metadata_obj = metadata.to_dict() if hasattr(metadata, "to_dict") else metadata
            results.append(
                {
                    "id": str(row[0]),
                    "content": row[1],
                    "metadata": metadata_obj,
                    "created_at": row[3],
                    "similarity": float(row[4]),
                }
            )
        return results


@lru_cache()
def get_pgvector_client() -> PGVectorClient:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("Database URL is not configured for pgvector.")
    return PGVectorClient(settings.database_url)


def store_embedding(
    table: str,
    content: str,
    embedding: Sequence[float],
    metadata: Dict[str, Any] | None = None,
) -> str:
    settings = get_settings()
    if settings.offline_mode:
        return offline_store.store_embedding(table, content, embedding, metadata)
    client = get_pgvector_client()
    return client.insert_embedding(table, content, embedding, metadata)


def search_embeddings(
    table: str,
    query_vector: Sequence[float],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    settings = get_settings()
    if settings.offline_mode:
        return offline_store.top_k_embeddings(table, query_vector, top_k)
    client = get_pgvector_client()
    return client.search_embeddings(table, query_vector, top_k)
