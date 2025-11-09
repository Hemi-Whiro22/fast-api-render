"""Local SQLite fallback store for offline mode."""
from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Dict, Sequence

_DB_PATH = Path("data/tiwhanawhana.db")
_SUPPORTED_TABLES = {
    "ocr_logs",
    "translations",
    "embeddings",
    "ti_memory",
    "task_queue",
    "mauri_logs",
}


def _normalize_table_name(table: str) -> str:
    parts = table.split(".")
    normalized = parts[-1].strip()
    if normalized not in _SUPPORTED_TABLES:
        raise ValueError(f"Table '{table}' is not supported offline.")
    return normalized


def _ensure_database() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    for table in _SUPPORTED_TABLES:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id TEXT PRIMARY KEY,
                content TEXT,
                metadata TEXT,
                embedding TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    conn.commit()
    return conn


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(payload)
    item.setdefault("id", str(uuid.uuid4()))
    metadata = item.get("metadata")
    if metadata is not None and not isinstance(metadata, str):
        item["metadata"] = json.dumps(metadata)
    embedding = item.get("embedding")
    if embedding is not None and not isinstance(embedding, str):
        item["embedding"] = json.dumps(embedding)
    return item


def insert_record(table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    table_name = _normalize_table_name(table)
    conn = _ensure_database()
    item = _normalize_payload(payload)
    columns = ", ".join(item.keys())
    placeholders = ", ".join([":" + key for key in item.keys()])
    conn.execute(
        f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
        item,
    )
    conn.commit()
    return _row_to_dict(item)


def fetch_records(table: str, limit: int | None = None) -> list[Dict[str, Any]]:
    table_name = _normalize_table_name(table)
    conn = _ensure_database()
    query = f"SELECT * FROM {table_name} ORDER BY datetime(created_at) DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    rows = conn.execute(query).fetchall()
    return [_row_to_dict(row) for row in rows]


def store_embedding(
    table: str,
    content: str,
    embedding: Sequence[float],
    metadata: Dict[str, Any] | None = None,
) -> str:
    record = insert_record(
        table,
        {
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {},
        },
    )
    return str(record["id"])


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    if len(a) != len(b):
        raise ValueError(
            "Vectors must be the same length for cosine similarity.")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def top_k_embeddings(
    table: str,
    query_vector: Sequence[float],
    top_k: int = 5,
) -> list[Dict[str, Any]]:
    records = fetch_records(table)
    scored: list[tuple[float, Dict[str, Any]]] = []
    for record in records:
        embedding = record.get("embedding")
        if isinstance(embedding, str):
            embedding = json.loads(embedding)
        if not isinstance(embedding, Sequence):
            continue
        # type: ignore[arg-type]
        score = cosine_similarity(query_vector, embedding)
        scored.append((score, record))
    scored.sort(key=lambda item: item[0], reverse=True)
    results: list[Dict[str, Any]] = []
    for score, record in scored[:top_k]:
        enriched = dict(record)
        enriched["similarity"] = float(score)
        results.append(enriched)
    return results


def prune_embeddings(table: str, keep: int) -> None:
    records = fetch_records(table)
    if len(records) <= keep:
        return
    to_delete = records[keep:]
    conn = _ensure_database()
    table_name = _normalize_table_name(table)
    for record in to_delete:
        conn.execute(f"DELETE FROM {table_name} WHERE id = ?", (record["id"],))
    conn.commit()


def _row_to_dict(row: Any) -> Dict[str, Any]:
    if isinstance(row, dict):
        result = dict(row)
    else:
        result = {key: row[key] for key in row.keys()}
    for field in ("metadata", "embedding"):
        if field in result and isinstance(result[field], str):
            try:
                result[field] = json.loads(result[field])
            except json.JSONDecodeError:
                pass
    return result
