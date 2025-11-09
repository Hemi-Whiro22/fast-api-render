#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Supabase connectivity via REST API (FastAPI) and PostgreSQL.
Uses service-role keys from environment to authenticate both connections.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure we can import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

# Load environment in priority order
env_candidates = [
    Path(__file__).resolve().parents[1] / ".env.local",
    Path(__file__).resolve().parents[1] / ".env",
    Path(__file__).resolve().parents[1] / ".mauri" / "tiwhanawhana.env",
    Path(__file__).resolve().parents[1] / ".mauri" / ".env",
]

for candidate in env_candidates:
    if candidate.exists():
        load_dotenv(candidate, override=False)
        print(f"✅ Loaded env from {candidate.name}")

# ============================================================================
# TEST 1: REST API (FastAPI + Supabase Client)
# ============================================================================
def test_rest_api():
    """Test Supabase REST API using service-role key."""
    print("\n" + "=" * 70)
    print("🌐 TEST 1: REST API Connection (FastAPI)")
    print("=" * 70)
    
    try:
        from supabase import create_client
    except ImportError:
        print("❌ supabase package not installed. Run: pip install supabase")
        return False
    
    den_url = os.getenv("DEN_URL")
    den_key = os.getenv("DEN_API_KEY")
    tepuna_url = os.getenv("TEPUNA_URL")
    tepuna_key = os.getenv("TEPUNA_API_KEY")
    
    if not all([den_url, den_key, tepuna_url, tepuna_key]):
        print("❌ Missing Supabase credentials:")
        print(f"   DEN_URL: {'✓' if den_url else '✗'}")
        print(f"   DEN_API_KEY: {'✓' if den_key else '✗'}")
        print(f"   TEPUNA_URL: {'✓' if tepuna_url else '✗'}")
        print(f"   TEPUNA_API_KEY: {'✓' if tepuna_key else '✗'}")
        return False
    
    # Test DEN project
    print("\n🔗 DEN Project (Service Role):")
    try:
        den_client = create_client(den_url, den_key)
        print(f"   ✓ Client created")
        
        # Try a simple query on any table; if ti_memory doesn't exist, try alternatives
        try:
            result = den_client.table("ti_memory").select("id").limit(1).execute()
            table_used = "ti_memory"
        except Exception:
            # Try alternative table names
            for table_name in ["koru_context_memo", "public.koru_context_memo", "task_queue", "mauri_logs"]:
                try:
                    result = den_client.table(table_name).select("id").limit(1).execute()
                    table_used = table_name
                    break
                except Exception:
                    continue
            else:
                raise Exception("No queryable tables found")
        
        print(f"   ✓ Query successful: {table_used} table accessible")
        print(f"   ✓ Records found: {len(result.data)}")
        den_ok = True
    except Exception as e:
        print(f"   ✗ Error: {str(e)[:100]}")
        den_ok = False
    
    # Test TEPUNA project
    print("\n🔗 TEPUNA Project (Service Role):")
    try:
        tepuna_client = create_client(tepuna_url, tepuna_key)
        print(f"   ✓ Client created")
        
        # Try a simple query on any table; if ti_memory doesn't exist, try alternatives
        try:
            result = tepuna_client.table("ti_memory").select("id").limit(1).execute()
            table_used = "ti_memory"
        except Exception:
            # Try alternative table names
            for table_name in ["koru_context_memo", "public.koru_context_memo", "task_queue", "mauri_logs"]:
                try:
                    result = tepuna_client.table(table_name).select("id").limit(1).execute()
                    table_used = table_name
                    break
                except Exception:
                    continue
            else:
                raise Exception("No queryable tables found")
        
        print(f"   ✓ Query successful: {table_used} table accessible")
        print(f"   ✓ Records found: {len(result.data)}")
        tepuna_ok = True
    except Exception as e:
        print(f"   ✗ Error: {str(e)[:100]}")
        tepuna_ok = False
    
    return den_ok and tepuna_ok


# ============================================================================
# TEST 2: PostgreSQL Direct Connection
# ============================================================================
def test_postgres_connection():
    """Test PostgreSQL direct connection using connection strings."""
    print("\n" + "=" * 70)
    print("🐘 TEST 2: PostgreSQL Direct Connection")
    print("=" * 70)
    
    try:
        import psycopg2
    except ImportError:
        print("⚠️  psycopg2 not installed. Run: pip install psycopg2-binary")
        print("   Skipping PostgreSQL direct test.")
        return None
    
    den_db_url = os.getenv("DEN_DB_URL")
    tepuna_db_url = os.getenv("TEPUNA_DB_URL")
    
    if not den_db_url or not tepuna_db_url:
        print("❌ Missing PostgreSQL connection strings:")
        print(f"   DEN_DB_URL: {'✓' if den_db_url else '✗'}")
        print(f"   TEPUNA_DB_URL: {'✓' if tepuna_db_url else '✗'}")
        print("   (These are typically set to placeholders; real DBs require actual credentials)")
        return None
    
    # Test DEN project
    print("\n🔗 DEN Database (PostgreSQL):")
    try:
        # Note: Connection strings with placeholders will fail; that's expected
        if "<" in den_db_url:
            print(f"   ⚠️  Connection string has placeholder: {den_db_url[:50]}...")
            print(f"   (This is expected; real credentials needed for full test)")
            den_ok = None
        else:
            conn = psycopg2.connect(den_db_url)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ti_memory;")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            print(f"   ✓ Connected and queried: {count} records in ti_memory")
            den_ok = True
    except Exception as e:
        print(f"   ✗ Connection failed: {str(e)[:100]}")
        den_ok = False
    
    # Test TEPUNA project
    print("\n🔗 TEPUNA Database (PostgreSQL):")
    try:
        if "<" in tepuna_db_url:
            print(f"   ⚠️  Connection string has placeholder: {tepuna_db_url[:50]}...")
            print(f"   (This is expected; real credentials needed for full test)")
            tepuna_ok = None
        else:
            conn = psycopg2.connect(tepuna_db_url)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ti_memory;")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            print(f"   ✓ Connected and queried: {count} records in ti_memory")
            tepuna_ok = True
    except Exception as e:
        print(f"   ✗ Connection failed: {str(e)[:100]}")
        tepuna_ok = False
    
    return den_ok and tepuna_ok if den_ok is not None and tepuna_ok is not None else None


# ============================================================================
# TEST 3: Core.main FastAPI Integration
# ============================================================================
def test_fastapi_integration():
    """Test that core.main can load with the keys."""
    print("\n" + "=" * 70)
    print("🚀 TEST 3: FastAPI (core.main) Integration")
    print("=" * 70)
    
    try:
        # Import the main app to verify it boots with the keys
        from Te_Po.core.main import app
        print("   ✓ backend.core.main loaded successfully")
        
        # Check if the app has the expected routes
        routes = [route.path for route in app.routes]
        expected_routes = ["/health", "/env/health", "/"]
        found = [r for r in expected_routes if any(r in route for route in routes)]
        print(f"   ✓ Routes loaded: {len(routes)} total")
        print(f"   ✓ Health endpoints: {found}")
        
        return True
    except Exception as e:
        print(f"   ✗ Error loading app: {str(e)[:100]}")
        return False


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Run all tests."""
    print("🌊 Tiwhanawhana Supabase Connection Tests")
    print(f"   Time: {datetime.now(timezone.utc).isoformat()}")
    
    results = {}
    
    # Test REST API
    results["REST API"] = test_rest_api()
    
    # Test PostgreSQL
    results["PostgreSQL"] = test_postgres_connection()
    
    # Test FastAPI integration
    results["FastAPI"] = test_fastapi_integration()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"{status} | {test_name}")
    
    all_passed = all(v for v in results.values() if v is not None)
    
    if all_passed:
        print("\n🎉 All tests passed! Supabase connectivity is working.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
