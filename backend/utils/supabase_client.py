#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase client factory and utilities for both DEN and TEPUNA projects.
Handles REST API connections via canonical environment variables.
"""

import os
from typing import Optional
from supabase import Client, create_client
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Cache clients to avoid recreating
_den_client: Optional[Client] = None
_tepuna_client: Optional[Client] = None


def get_supabase_client(project: str = "den") -> Optional[Client]:
    """
    Get or create a Supabase client for the specified project.
    
    Args:
        project: "den" or "tepuna"
    
    Returns:
        Supabase Client or None if credentials missing
    """
    global _den_client, _tepuna_client
    
    if project.lower() == "den":
        if _den_client is not None:
            return _den_client
        
        url = os.getenv("DEN_URL")
        key = os.getenv("DEN_API_KEY")
        
        if not url or not key:
            logger.warning("DEN_URL or DEN_API_KEY missing—DEN client unavailable")
            return None
        
        try:
            _den_client = create_client(url, key)
            logger.info("✅ DEN Supabase client initialized")
            return _den_client
        except Exception as e:
            logger.error("Failed to create DEN client: %s", e)
            return None
    
    elif project.lower() == "tepuna":
        if _tepuna_client is not None:
            return _tepuna_client
        
        url = os.getenv("TEPUNA_URL")
        key = os.getenv("TEPUNA_API_KEY")
        
        if not url or not key:
            logger.warning("TEPUNA_URL or TEPUNA_API_KEY missing—TEPUNA client unavailable")
            return None
        
        try:
            _tepuna_client = create_client(url, key)
            logger.info("✅ TEPUNA Supabase client initialized")
            return _tepuna_client
        except Exception as e:
            logger.error("Failed to create TEPUNA client: %s", e)
            return None
    
    else:
        logger.error("Unknown project: %s. Use 'den' or 'tepuna'", project)
        return None


def query_table(project: str, table: str, select: str = "*", limit: int = 10) -> dict:
    """
    Query a table in the specified Supabase project.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        select: Columns to select
        limit: Max rows to return
    
    Returns:
        Response dict with data, count, error
    """
    client = get_supabase_client(project)
    
    if not client:
        return {"data": [], "count": 0, "error": f"Client for {project} not available"}
    
    try:
        response = client.table(table).select(select).limit(limit).execute()
        return {
            "data": response.data,
            "count": len(response.data),
            "error": None,
        }
    except Exception as e:
        logger.error("Query failed on %s.%s: %s", project, table, e)
        return {
            "data": [],
            "count": 0,
            "error": str(e),
        }


def insert_record(project: str, table: str, record: dict) -> dict:
    """
    Insert a record into a table.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        record: Record dict
    
    Returns:
        Response dict with data, error
    """
    client = get_supabase_client(project)
    
    if not client:
        return {"data": None, "error": f"Client for {project} not available"}
    
    try:
        response = client.table(table).insert(record).execute()
        return {
            "data": response.data,
            "error": None,
        }
    except Exception as e:
        logger.error("Insert failed on %s.%s: %s", project, table, e)
        return {
            "data": None,
            "error": str(e),
        }


def fetch_records(project: str = "den", table: str = "", select: str = "*", limit: int = 100) -> list:
    """
    Fetch records from a Supabase table.
    
    Args:
        project: "den" or "tepuna"
        table: Table name
        select: Select clause (default: all columns)
        limit: Max records to return
    
    Returns:
        List of records or empty list on error
    """
    client = get_supabase_client(project)
    if not client or not table:
        logger.warning("Cannot fetch from %s.%s: client unavailable or table empty", project, table)
        return []
    
    try:
        result = client.table(table).select(select).limit(limit).execute()
        return result.data or []
    except Exception as e:
        logger.error("Fetch failed on %s.%s: %s", project, table, e)
        return []


def fetch_latest(table_path: str) -> dict:
    """
    Fetch the latest record from a table.
    Supports both "table_name" and "project.table_name" formats.
    
    Args:
        table_path: Table name or "project.table_name"
    
    Returns:
        Latest record dict or empty dict on error
    """
    # Parse project and table from path
    if "." in table_path:
        project, table = table_path.split(".", 1)
    else:
        project = "den"
        table = table_path
    
    client = get_supabase_client(project)
    if not client or not table:
        logger.warning("Cannot fetch latest from %s: client unavailable", table_path)
        return {}
    
    try:
        result = client.table(table).select("*").order("created_at", desc=True).limit(1).execute()
        records = result.data or []
        return records[0] if records else {}
    except Exception as e:
        logger.error("Fetch latest failed on %s: %s", table_path, e)
        return {}


# Initialize clients on import (with fallback)
supabase_den = get_supabase_client("den")
supabase_tepuna = get_supabase_client("tepuna")

