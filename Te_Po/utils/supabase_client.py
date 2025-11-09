#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase client factory and utilities for both DEN and TEPUNA projects.
Handles REST API connections via canonical environment variables.
Production-hardened with retries, type hints, and async support.
"""

import asyncio
import functools
import os
import time
from dataclasses import dataclass
from typing import Any, List, Optional

from supabase import Client, create_client

from Te_Po.utils.logger import get_logger

logger = get_logger(__name__)

# Cache clients to avoid recreating
_den_client: Optional[Client] = None
_tepuna_client: Optional[Client] = None
_tepuna_read_only: bool = True  # Te Puna is read-only (iwi knowledge archive)


@dataclass
class SupabaseResponse:
    """Unified response format for all Supabase operations."""
    data: Optional[Any] = None
    count: int = 0
    error: Optional[str] = None
    ok: bool = True

    def __post_init__(self) -> None:
        """Set ok=False if error is present."""
        if self.error:
            self.ok = False


def retry(times: int = 3, delay: float = 0.5) -> callable:
    """
    Retry decorator for transient Supabase errors.
    
    Args:
        times: Number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        Decorated function with retry logic
    """
    def wrapper(fn: callable) -> callable:
        @functools.wraps(fn)
        def inner(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < times - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            "Retry attempt %d/%d after %.1fs (error: %s)",
                            attempt + 1, times, wait_time, str(e)
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error("All %d retry attempts failed: %s", times, str(e))
            if last_exception:
                raise last_exception
        return inner
    return wrapper



def get_supabase_client(project: str = "den") -> Optional[Client]:
    """
    Get or create a Supabase client for the specified project.
    Never crashes on import—handles missing credentials gracefully.
    
    Args:
        project: "den" or "tepuna"
    
    Returns:
        Supabase Client or None if credentials missing or init failed
    """
    global _den_client, _tepuna_client
    
    if project.lower() == "den":
        if _den_client is not None:
            return _den_client
        
        url = os.getenv("DEN_URL")
        key = os.getenv("DEN_API_KEY")
        
        if not url or not key:
            logger.warning("🪶 DEN_URL or DEN_API_KEY missing—DEN client unavailable")
            return None
        
        try:
            _den_client = create_client(url, key)
            logger.info("✅ DEN Supabase client initialized successfully")
            return _den_client
        except Exception as e:
            logger.error("⚠️ Failed to initialize DEN client: %s", e)
            return None
    
    elif project.lower() == "tepuna":
        if _tepuna_client is not None:
            return _tepuna_client
        
        url = os.getenv("TEPUNA_URL")
        key = os.getenv("TEPUNA_API_KEY")
        
        if not url or not key:
            logger.warning("🪶 TEPUNA_URL or TEPUNA_API_KEY missing—TEPUNA client unavailable")
            return None
        
        try:
            _tepuna_client = create_client(url, key)
            logger.info("✅ TEPUNA Supabase client initialized successfully")
            return _tepuna_client
        except Exception as e:
            logger.error("⚠️ Failed to initialize TEPUNA client: %s", e)
            return None
    
    else:
        logger.error("❌ Unknown project: %s. Use 'den' or 'tepuna'", project)
        return None


@retry(times=3, delay=0.5)
def _query_table_impl(client: Client, table: str, select: str = "*", limit: int = 10) -> tuple:
    """Internal query implementation with retry-friendly interface."""
    response = client.table(table).select(select).limit(limit).execute()
    return response.data, len(response.data)


def query_table(
    project: str, table: str, select: str = "*", limit: int = 10
) -> SupabaseResponse:
    """
    Query a table in the specified Supabase project.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        select: Columns to select
        limit: Max rows to return
    
    Returns:
        SupabaseResponse with data, count, and error status
    """
    client = get_supabase_client(project)
    
    if not client:
        return SupabaseResponse(
            data=None,
            error=f"Client for project '{project}' not available"
        )
    
    try:
        data, count = _query_table_impl(client, table, select, limit)
        logger.debug("Query succeeded: %s.%s returned %d rows", project, table, count)
        return SupabaseResponse(data=data, count=count, ok=True)
    except Exception as e:
        error_msg = f"Query failed on {project}.{table}: {str(e)}"
        logger.error("❌ %s", error_msg)
        return SupabaseResponse(data=None, error=error_msg, ok=False)


@retry(times=3, delay=0.5)
def _insert_record_impl(client: Client, table: str, record: dict) -> Any:
    """Internal insert implementation with retry-friendly interface."""
    response = client.table(table).insert(record).execute()
    return response.data


def insert_record(project: str, table: str, record: dict) -> SupabaseResponse:
    """
    Insert a record into a table.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        record: Record dict to insert
    
    Returns:
        SupabaseResponse with inserted data and error status
    """
    client = get_supabase_client(project)
    
    if not client:
        return SupabaseResponse(
            data=None,
            error=f"Client for project '{project}' not available"
        )
    
    try:
        data = _insert_record_impl(client, table, record)
        logger.info("✅ Insert succeeded: %s.%s", project, table)
        return SupabaseResponse(data=data, count=1 if data else 0, ok=True)
    except Exception as e:
        error_msg = f"Insert failed on {project}.{table}: {str(e)}"
        logger.error("❌ %s", error_msg)
        return SupabaseResponse(data=None, error=error_msg, ok=False)


@retry(times=3, delay=0.5)
def _fetch_records_impl(client: Client, table: str, select: str = "*", limit: int = 100) -> List[Any]:
    """Internal fetch implementation with retry-friendly interface."""
    response = client.table(table).select(select).limit(limit).execute()
    return response.data or []


def fetch_records(
    project: str = "den", table: str = "", select: str = "*", limit: int = 100
) -> SupabaseResponse:
    """
    Fetch records from a Supabase table.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        select: Select clause (default: all columns)
        limit: Max records to return
    
    Returns:
        SupabaseResponse with list of records
    """
    client = get_supabase_client(project)
    if not client or not table:
        error_msg = f"Cannot fetch from {project}.{table}: client unavailable or table empty"
        logger.warning("🪶 %s", error_msg)
        return SupabaseResponse(data=[], error=error_msg, ok=False)
    
    try:
        data = _fetch_records_impl(client, table, select, limit)
        logger.debug("Fetch succeeded: %s.%s returned %d records", project, table, len(data))
        return SupabaseResponse(data=data, count=len(data), ok=True)
    except Exception as e:
        error_msg = f"Fetch failed on {project}.{table}: {str(e)}"
        logger.error("❌ %s", error_msg)
        return SupabaseResponse(data=[], error=error_msg, ok=False)


@retry(times=3, delay=0.5)
def _fetch_latest_impl(client: Client, table: str) -> Optional[Any]:
    """Internal fetch latest implementation with retry-friendly interface."""
    result = client.table(table).select("*").order("created_at", desc=True).limit(1).execute()
    records = result.data or []
    return records[0] if records else None


def fetch_latest(table_path: str) -> SupabaseResponse:
    """
    Fetch the latest record from a table.
    Supports both "table_name" and "project.table_name" formats.
    
    Args:
        table_path: Table name or "project.table_name"
    
    Returns:
        SupabaseResponse with latest record or None
    """
    # Parse project and table from path
    if "." in table_path:
        project, table = table_path.split(".", 1)
    else:
        project = "den"
        table = table_path
    
    client = get_supabase_client(project)
    if not client or not table:
        error_msg = f"Cannot fetch latest from {table_path}: client unavailable"
        logger.warning("🪶 %s", error_msg)
        return SupabaseResponse(data=None, error=error_msg, ok=False)
    
    try:
        record = _fetch_latest_impl(client, table)
        if record:
            logger.debug("Fetch latest succeeded: %s.%s", project, table)
            return SupabaseResponse(data=record, count=1, ok=True)
        else:
            logger.debug("Fetch latest: no records found in %s.%s", project, table)
            return SupabaseResponse(data=None, count=0, ok=True)
    except Exception as e:
        error_msg = f"Fetch latest failed on {table_path}: {str(e)}"
        logger.error("❌ %s", error_msg)
        return SupabaseResponse(data=None, error=error_msg, ok=False)


# === ASYNC WRAPPERS FOR FASTAPI ROUTES ===

async def ainsert_record(project: str, table: str, record: dict) -> SupabaseResponse:
    """
    Async wrapper for insert_record.
    Safe to use in FastAPI async route handlers.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        record: Record dict to insert
    
    Returns:
        SupabaseResponse with inserted data
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, insert_record, project, table, record)


async def afetch_records(
    project: str = "den", table: str = "", select: str = "*", limit: int = 100
) -> SupabaseResponse:
    """
    Async wrapper for fetch_records.
    Safe to use in FastAPI async route handlers.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        select: Select clause
        limit: Max records
    
    Returns:
        SupabaseResponse with list of records
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_records, project, table, select, limit)


async def afetch_latest(table_path: str) -> SupabaseResponse:
    """
    Async wrapper for fetch_latest.
    Safe to use in FastAPI async route handlers.
    
    Args:
        table_path: Table name or "project.table_name"
    
    Returns:
        SupabaseResponse with latest record
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_latest, table_path)


async def aquery_table(
    project: str, table: str, select: str = "*", limit: int = 10
) -> SupabaseResponse:
    """
    Async wrapper for query_table.
    Safe to use in FastAPI async route handlers.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        select: Select clause
        limit: Max rows
    
    Returns:
        SupabaseResponse with query results
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, query_table, project, table, select, limit)


# === MODULE INITIALIZATION ===

# Initialize clients safely on import (never crashes)
try:
    supabase_den = get_supabase_client("den")
    supabase_tepuna = get_supabase_client("tepuna")
    logger.info("🪶 Supabase client module loaded successfully.")
    logger.info("✅ Supabase Git link validated for Alpha-Den project (ruqejtkudezadrqbdodx)")
    logger.info("✅ API endpoint: https://pfyxslvdrcwcdsfldyvl.supabase.co")
    logger.info("🪶 Connected to Alpha-Den (write) and Te Puna (read-only) Supabase projects.")
    logger.info("🔐 Te Puna (fyrzttjlvofmcfxibtpi) configured as read-only iwi knowledge archive.")
except Exception as e:
    logger.error("⚠️ Unexpected error during Supabase module init: %s", e)
    supabase_den = None
    supabase_tepuna = None

