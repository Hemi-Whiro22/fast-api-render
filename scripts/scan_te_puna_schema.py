#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Te Puna Schema Scanner (Offline Demo Mode)
============================================
Generates schema alignment reports for Te Puna Supabase project.

When Render environment variables are set, uses live connection.
When run locally without credentials, generates demo schema based on typical iwi archive structure.

Usage:
    python scripts/scan_te_puna_schema.py [--demo]

Output:
    - logs/schema_te_puna.json (raw table/column metadata)
    - backend/schema_drift_report.json (alignment analysis)
    - logs/public_schema_te_puna.json (sanitized for iwi-ui)
    - backend/migration_suggestions.sql (non-destructive suggestions)
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

# Try to load credentials
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.expanduser("~/.env"))
except Exception:
    pass

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Te_Po.utils.logger import get_logger
from Te_Po.utils.supabase_client import get_supabase_client

logger = get_logger(__name__)

# Expected backend models schema
LOCAL_MODELS = {
    "ocr_logs": {
        "id": "uuid",
        "file_name": "text",
        "file_url": "text",
        "text_content": "text",
        "language_detected": "text",
        "meta": "jsonb",
        "created_at": "timestamp",
    },
    "translations": {
        "id": "uuid",
        "ocr_id": "uuid",
        "source_lang": "text",
        "target_lang": "text",
        "source_text": "text",
        "translated_text": "text",
        "model_used": "text",
        "confidence": "numeric",
        "meta": "jsonb",
        "created_at": "timestamp",
    },
    "memory_logs": {
        "id": "uuid",
        "memory_type": "text",
        "content": "text",
        "embedding": "vector",
        "related_task": "uuid",
        "meta": "jsonb",
        "created_at": "timestamp",
    },
    "task_queue": {
        "id": "uuid",
        "task_type": "text",
        "payload": "jsonb",
        "status": "text",
        "priority": "integer",
        "retries": "integer",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "completed_at": "timestamp",
    },
}

# Demo Te Puna schema (typical iwi archive structure)
DEMO_TEPUNA_SCHEMA = {
    "taonga_metadata": {
        "columns": [
            {"column_name": "id", "data_type": "uuid", "is_nullable": False},
            {"column_name": "name", "data_type": "text", "is_nullable": False},
            {"column_name": "description", "data_type": "text", "is_nullable": True},
            {"column_name": "cultural_significance", "data_type": "text", "is_nullable": True},
            {"column_name": "source", "data_type": "text", "is_nullable": True},
            {"column_name": "iwi", "data_type": "text", "is_nullable": True},
            {"column_name": "category", "data_type": "text", "is_nullable": True},
            {"column_name": "created_at", "data_type": "timestamp without time zone", "is_nullable": False},
            {"column_name": "updated_at", "data_type": "timestamp without time zone", "is_nullable": True},
        ],
        "column_count": 9,
    },
    "summaries": {
        "columns": [
            {"column_name": "id", "data_type": "uuid", "is_nullable": False},
            {"column_name": "document_id", "data_type": "uuid", "is_nullable": False},
            {"column_name": "summary_text", "data_type": "text", "is_nullable": False},
            {"column_name": "keywords", "data_type": "text", "is_nullable": True},
            {"column_name": "language", "data_type": "text", "is_nullable": False},
            {"column_name": "created_at", "data_type": "timestamp without time zone", "is_nullable": False},
        ],
        "column_count": 6,
    },
    "ocr_logs": {
        "columns": [
            {"column_name": "id", "data_type": "uuid", "is_nullable": False},
            {"column_name": "file_name", "data_type": "text", "is_nullable": True},
            {"column_name": "file_url", "data_type": "text", "is_nullable": True},
            {"column_name": "text_content", "data_type": "text", "is_nullable": False},
            {"column_name": "language_detected", "data_type": "text", "is_nullable": True},
            {"column_name": "confidence_score", "data_type": "numeric", "is_nullable": True},
            {"column_name": "meta", "data_type": "jsonb", "is_nullable": True},
            {"column_name": "created_at", "data_type": "timestamp without time zone", "is_nullable": False},
        ],
        "column_count": 8,
    },
    "translations": {
        "columns": [
            {"column_name": "id", "data_type": "uuid", "is_nullable": False},
            {"column_name": "ocr_id", "data_type": "uuid", "is_nullable": True},
            {"column_name": "source_lang", "data_type": "text", "is_nullable": False},
            {"column_name": "target_lang", "data_type": "text", "is_nullable": False},
            {"column_name": "source_text", "data_type": "text", "is_nullable": False},
            {"column_name": "translated_text", "data_type": "text", "is_nullable": False},
            {"column_name": "model_used", "data_type": "text", "is_nullable": True},
            {"column_name": "confidence", "data_type": "numeric", "is_nullable": True},
            {"column_name": "meta", "data_type": "jsonb", "is_nullable": True},
            {"column_name": "created_at", "data_type": "timestamp without time zone", "is_nullable": False},
        ],
        "column_count": 10,
    },
    "memory_logs": {
        "columns": [
            {"column_name": "id", "data_type": "uuid", "is_nullable": False},
            {"column_name": "memory_type", "data_type": "text", "is_nullable": False},
            {"column_name": "content", "data_type": "text", "is_nullable": False},
            {"column_name": "embedding", "data_type": "USER-DEFINED", "is_nullable": True},
            {"column_name": "related_task", "data_type": "uuid", "is_nullable": True},
            {"column_name": "meta", "data_type": "jsonb", "is_nullable": True},
            {"column_name": "created_at", "data_type": "timestamp without time zone", "is_nullable": False},
        ],
        "column_count": 7,
    },
}


def get_live_schema(project: str) -> Dict[str, Any]:
    """Try to get live schema from Supabase."""
    try:
        from Te_Po.utils.supabase_client import get_supabase_client
        
        client = get_supabase_client(project)
        if not client:
            logger.warning(f"⚠️ Could not connect to {project}, falling back to demo mode")
            return {}
        
        schema_data = {}
        try:
            tables_response = client.table("information_schema.tables").select(
                "table_name"
            ).eq("table_schema", "public").execute()
            
            if not tables_response.data:
                logger.warning(f"⚠️ No tables found in {project}")
                return {}
            
            table_names = [t["table_name"] for t in tables_response.data]
            logger.info(f"🪶 Found {len(table_names)} tables in {project}")
            
            for table_name in table_names:
                try:
                    columns_response = client.table("information_schema.columns").select(
                        "column_name, data_type, is_nullable, column_default"
                    ).eq("table_schema", "public").eq("table_name", table_name).execute()
                    
                    if columns_response.data:
                        schema_data[table_name] = {
                            "columns": columns_response.data,
                            "column_count": len(columns_response.data),
                        }
                        logger.info(f"✅ {project}.{table_name}: {len(columns_response.data)} columns")
                except Exception as e:
                    logger.warning(f"⚠️ Could not fetch columns for {table_name}: {e}")
            
            return schema_data
        except Exception as e:
            logger.warning(f"⚠️ Schema query failed: {e}")
            return {}
    except Exception as e:
        logger.warning(f"⚠️ Live schema unavailable: {e}")
        return {}


def normalize_type(pg_type: str) -> str:
    """Normalize PostgreSQL type names for comparison."""
    type_map = {
        "character varying": "text",
        "timestamp without time zone": "timestamp",
        "timestamp with time zone": "timestamp",
        "boolean": "boolean",
        "integer": "integer",
        "bigint": "integer",
        "numeric": "numeric",
        "double precision": "numeric",
        "uuid": "uuid",
        "json": "jsonb",
        "jsonb": "jsonb",
        "text": "text",
        "USER-DEFINED": "vector",  # pgvector
    }
    return type_map.get(pg_type, pg_type)


def generate_alignment_report(
    local_models: Dict[str, Dict[str, str]],
    remote_schema: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare local models to remote schema and generate alignment report.
    
    Args:
        local_models: Expected backend model schema
        remote_schema: Actual Te Puna schema
    
    Returns:
        Alignment report with match %, missing fields, type mismatches
    """
    report = {
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "project": "te_puna",
        "summary": {
            "local_tables": len(local_models),
            "remote_tables": len(remote_schema),
            "matched_tables": 0,
            "missing_tables": 0,
            "extra_tables": 0,
        },
        "tables": {},
    }
    
    # Check each local model
    for table_name, local_cols in local_models.items():
        if table_name not in remote_schema:
            report["summary"]["missing_tables"] += 1
            report["tables"][table_name] = {
                "status": "MISSING",
                "local_columns": local_cols,
                "remote_columns": {},
                "match_percentage": 0,
                "recommendations": [f"Table {table_name} does not exist in Te Puna"],
            }
            continue
        
        # Table exists, compare columns
        remote_cols = {
            col["column_name"]: normalize_type(col.get("data_type", "unknown"))
            for col in remote_schema[table_name].get("columns", [])
        }
        
        matched_fields = 0
        mismatches = []
        missing_fields = []
        
        for col_name, col_type in local_cols.items():
            if col_name not in remote_cols:
                missing_fields.append(col_name)
            elif normalize_type(col_type) != remote_cols[col_name]:
                mismatches.append({
                    "column": col_name,
                    "local_type": col_type,
                    "remote_type": remote_cols[col_name],
                })
            else:
                matched_fields += 1
        
        match_pct = (matched_fields / len(local_cols)) * 100 if local_cols else 0
        
        if match_pct == 100:
            report["summary"]["matched_tables"] += 1
            status = "ALIGNED"
        elif match_pct >= 70:
            status = "PARTIAL"
        else:
            status = "MISALIGNED"
        
        report["tables"][table_name] = {
            "status": status,
            "local_columns": local_cols,
            "remote_columns": remote_cols,
            "matched_columns": matched_fields,
            "total_columns": len(local_cols),
            "match_percentage": round(match_pct, 1),
            "missing_fields": missing_fields,
            "type_mismatches": mismatches,
            "extra_remote_columns": list(set(remote_cols.keys()) - set(local_cols.keys())),
            "recommendations": _get_recommendations(
                table_name, status, missing_fields, mismatches
            ),
        }
    
    # Check for extra remote tables
    for table_name in remote_schema.keys():
        if table_name not in local_models:
            report["summary"]["extra_tables"] += 1
            report["tables"][table_name] = {
                "status": "EXTRA",
                "local_columns": {},
                "remote_columns": {
                    col["column_name"]: normalize_type(col.get("data_type", "unknown"))
                    for col in remote_schema[table_name].get("columns", [])
                },
                "match_percentage": 0,
                "recommendations": [f"Extra table in Te Puna (may be reusable)"],
            }
    
    return report


def _get_recommendations(
    table_name: str, status: str, missing_fields: List[str], mismatches: List[Dict]
) -> List[str]:
    """Generate recommendations for alignment."""
    recs = []
    
    if status == "ALIGNED":
        recs.append(f"✅ {table_name} is fully aligned")
    elif status == "PARTIAL":
        if missing_fields:
            recs.append(
                f"⚠️ Add missing fields: {', '.join(missing_fields)}"
            )
        if mismatches:
            recs.append(
                f"⚠️ Fix type mismatches: {', '.join(m['column'] for m in mismatches)}"
            )
    else:  # MISALIGNED
        recs.append(f"❌ Significant schema drift detected")
        if missing_fields:
            recs.append(
                f"   Missing: {', '.join(missing_fields)}"
            )
        if mismatches:
            recs.append(
                f"   Type mismatches: {', '.join(m['column'] for m in mismatches)}"
            )
    
    return recs


def generate_public_schema(remote_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate sanitized public schema for IwiPortalPanel archive view.
    Include only table names, fields, and descriptions (no internal details).
    """
    public = {
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "project": "te_puna",
        "description": "Te Puna Read-Only Knowledge Archive",
        "access_level": "read-only",
        "tables": {},
    }
    
    table_descriptions = {
        "taonga_metadata": "Metadata about taonga (treasures) - cultural artifacts, resources",
        "summaries": "Document summaries and abstracts from processed sources",
        "memory_logs": "Historical logs of memory and knowledge processing",
        "ocr_logs": "Archived OCR extraction records (read-only)",
        "translations": "Archived translation records (read-only)",
        "task_queue": "Historical task records (read-only)",
    }
    
    for table_name, schema in remote_schema.items():
        columns = [
            {
                "name": col["column_name"],
                "type": normalize_type(col.get("data_type", "unknown")),
            }
            for col in schema.get("columns", [])
        ]
        
        public["tables"][table_name] = {
            "description": table_descriptions.get(
                table_name,
                f"Archive table: {table_name}"
            ),
            "column_count": len(columns),
            "columns": columns,
            "read_only": True,
        }
    
    return public


def main():
    """Main execution."""
    logger.info("🪶 Te Puna Schema Scanner starting...")
    
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    backend_dir = Path(__file__).parent.parent / "backend"
    backend_dir.mkdir(exist_ok=True)
    
    # 1. Try live connection, fall back to demo
    logger.info("⏳ Scanning Te Puna schema...")
    remote_schema = get_live_schema("tepuna")
    
    if not remote_schema:
        logger.info("🪶 Using demo schema (typical Te Puna archive structure)")
        remote_schema = DEMO_TEPUNA_SCHEMA
    else:
        logger.info("✅ Live schema retrieved from Te Puna")
    
    # Save raw schema
    schema_file = logs_dir / "schema_te_puna.json"
    with open(schema_file, "w") as f:
        json.dump(remote_schema, f, indent=2, default=str)
    logger.info(f"✅ Raw schema saved: {schema_file}")
    
    # 2. Generate alignment report
    logger.info("⏳ Analyzing schema alignment...")
    alignment_report = generate_alignment_report(LOCAL_MODELS, remote_schema)
    
    report_file = backend_dir / "schema_drift_report.json"
    with open(report_file, "w") as f:
        json.dump(alignment_report, f, indent=2, default=str)
    logger.info(f"✅ Alignment report saved: {report_file}")
    
    # Print summary
    summary = alignment_report["summary"]
    logger.info(
        f"📊 Alignment Summary:\n"
        f"   Local tables: {summary['local_tables']}\n"
        f"   Remote tables: {summary['remote_tables']}\n"
        f"   Matched: {summary['matched_tables']}\n"
        f"   Missing: {summary['missing_tables']}\n"
        f"   Extra in remote: {summary['extra_tables']}"
    )
    
    # 3. Generate public schema
    logger.info("⏳ Generating public schema for iwi-ui...")
    public_schema = generate_public_schema(remote_schema)
    
    public_file = logs_dir / "public_schema_te_puna.json"
    with open(public_file, "w") as f:
        json.dump(public_schema, f, indent=2, default=str)
    logger.info(f"✅ Public schema saved: {public_file}")
    
    # 4. Generate migration suggestions (non-destructive)
    logger.info("⏳ Generating migration suggestions...")
    migration_suggestions = generate_migration_suggestions(alignment_report)
    
    migration_file = backend_dir / "migration_suggestions.sql"
    with open(migration_file, "w") as f:
        f.write(migration_suggestions)
    logger.info(f"✅ Migration suggestions saved: {migration_file}")
    
    logger.info("🪶 Schema scan complete! All reports generated.")
    logger.info(f"   📁 logs/schema_te_puna.json")
    logger.info(f"   📁 backend/schema_drift_report.json")
    logger.info(f"   📁 logs/public_schema_te_puna.json")
    logger.info(f"   📁 backend/migration_suggestions.sql")


def generate_migration_suggestions(report: Dict[str, Any]) -> str:
    """Generate non-destructive SQL migration suggestions."""
    sql = [
        "-- Te Puna Schema Alignment Migration Suggestions",
        "-- READ-ONLY: Review before applying. No destructive operations.",
        f"-- Generated: {datetime.utcnow().isoformat()}",
        "",
    ]
    
    for table_name, table_info in report["tables"].items():
        if table_info["status"] == "ALIGNED":
            sql.append(f"-- ✅ {table_name}: Fully aligned, no changes needed")
            sql.append("")
            continue
        
        if table_info["status"] == "MISSING":
            sql.append(f"-- ❌ {table_name}: Table missing from Te Puna")
            sql.append(f"-- TODO: Review if this table should be created in Te Puna")
            sql.append("")
            continue
        
        # PARTIAL or MISALIGNED
        missing_fields = table_info.get("missing_fields", [])
        if missing_fields:
            sql.append(f"-- ⚠️ {table_name}: Adding missing fields (non-destructive)")
            for field_name in missing_fields:
                field_type = LOCAL_MODELS.get(table_name, {}).get(field_name, "text")
                sql.append(
                    f"-- ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {field_name} {field_type};"
                )
            sql.append("")
    
    return "\n".join(sql)


if __name__ == "__main__":
    main()
