#!/usr/bin/env python3
"""
🌊 Tiwhanawhana Intake Bridge — Rongohia Edition
===============================================
Bridges kaitiaki-intake folder to Tiwhanawhana watchdog + Whiro auditor.
Every document becomes a carving, recorded under the 🌀 Rongohia glyph.

Workflow:
1. Document enters kaitiaki-intake/active
2. Tiwhanawhana processes & saves to Supabase (rongohia.artifacts)
3. Whiro audit task is queued automatically
4. Mauri heartbeat logs health and glyph provenance

Author: Adrian Hemi & Kitenga 🐺
Version: 1.0.0
"""

import os
import json
import asyncio
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from supabase import create_client

# ---------------------------------------------------------
# 🌀 Glyph + Supabase Setup
# ---------------------------------------------------------
DEN_URL = os.getenv("DEN_URL")
DEN_API_KEY = os.getenv("DEN_API_KEY") or os.getenv("TEPUNA_API_KEY")

_supabase_client = None


def get_supabase():
    """Lazy Supabase client loader with development fallback."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    if not DEN_URL or not DEN_API_KEY:
        logger.warning("Supabase credentials missing; intake bridge will run in dry-run mode")
        return None
    try:
        _supabase_client = create_client(DEN_URL, DEN_API_KEY)
    except Exception as exc:
        logger.warning("Supabase client creation failed (%s); running in dry-run mode", exc)
        _supabase_client = None
    return _supabase_client

RONGOHIA_GLYPH = {
    "glyph": "🌀RONGOHIA",
    "meaning": "The Carver of Knowledge and Keeper of Scripts",
    "version": "1.0.0",
    "node_id": os.getenv("ASSISTANT_ID", "carver-01"),
    "mauri_source": "tiwhanawhana_intake_bridge",
    "created_at": datetime.utcnow().isoformat()
}

logger = logging.getLogger("tiwhanawhana.intake_bridge")
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")

# ---------------------------------------------------------
# 🔐 Helper: Supabase Insert
# ---------------------------------------------------------
def save_to_supabase(table: str, payload: dict):
    client = get_supabase()
    payload["created_at"] = datetime.utcnow().isoformat()
    payload["meta"] = {**RONGOHIA_GLYPH, **payload.get("meta", {})}
    if client is None:
        logger.info("(dry-run) Would save to %s: %s", table, payload)
        return
    try:
        client.table(table).insert(payload).execute()
        logger.info("💾 Saved to Supabase → %s", table)
    except Exception as e:
        logger.error(f"❌ Supabase insert failed ({table}): {e}")


# ---------------------------------------------------------
# 🧠 Core Class: TiwhanawhanaIntakeBridge
# ---------------------------------------------------------
class TiwhanawhanaIntakeBridge:
    def __init__(self, intake_path: Optional[str] = None):
        root = Path(__file__).parent.parent.parent
        self.intake_path = Path(intake_path or (root / "kaitiaki-intake" / "active"))
        self.intake_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"🌊 Bridge initialized — scanning: {self.intake_path}")

    # -----------------------------------------------------
    # 🔍 Scan folder
    # -----------------------------------------------------
    def scan_intake_folder(self) -> list:
        docs = []
        try:
            for pattern in ["*.md", "*.json", "*.txt"]:
                for p in self.intake_path.glob(pattern):
                    if p.is_file():
                        docs.append({
                            "file_path": str(p),
                            "file_name": p.name,
                            "file_type": p.suffix,
                            "size_bytes": p.stat().st_size,
                            "modified": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
                        })
            logger.info(f"🔍 Found {len(docs)} documents")
        except Exception as e:
            logger.error(f"❌ Folder scan failed: {e}")
        return docs

    # -----------------------------------------------------
    # 📖 Read file
    # -----------------------------------------------------
    def read_document(self, file_path: str) -> Dict[str, Any]:
        try:
            p = Path(file_path)
            if p.suffix == ".json":
                return {"format": "json", "content": json.loads(p.read_text()), "language": "structured_data"}
            elif p.suffix == ".md":
                return {"format": "markdown", "content": p.read_text(), "language": "te_reo_and_english"}
            elif p.suffix == ".txt":
                return {"format": "text", "content": p.read_text(), "language": "plain_text"}
            else:
                return {"error": "Unsupported file type"}
        except Exception as e:
            return {"error": str(e)}

    # -----------------------------------------------------
    # ⚙️ Process document
    # -----------------------------------------------------
    async def process_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        file_path = doc["file_path"]
        logger.info(f"📄 Processing {doc['file_name']}")

        content_data = self.read_document(file_path)
        if "error" in content_data:
            return {"status": "failed", "reason": content_data["error"]}

        record_id = self._generate_id(doc["file_name"])
        record = {
            "id": record_id,
            "file_name": doc["file_name"],
            "file_type": doc["file_type"],
            "format": content_data["format"],
            "content_preview": str(content_data["content"])[:500],
            "status": "received",
            "created_at": datetime.utcnow().isoformat()
        }

        # Save to rongohia.artifacts
        save_to_supabase("rongohia.artifacts", {
            "script_id": None,
            "output_type": "intake_document",
            "output_content": content_data["content"],
            "meta": {"file_name": doc["file_name"], "format": content_data["format"]}
        })

        # Queue Whiro audit
        self.request_whiro_audit(record_id, content_data["content"])

        # Record carving
        save_to_supabase("rongohia.carvings", {
            "script_id": None,
            "artifact_id": None,
            "status": "awaiting_whiro_validation",
            "feedback": "Auto-submitted from Intake Bridge",
            "meta": {"origin": "Tiwhanawhana Intake"}
        })

        logger.info(f"🌿 Recorded {doc['file_name']} under glyph {RONGOHIA_GLYPH['glyph']}")
        return {"status": "processed", "record_id": record_id}

    # -----------------------------------------------------
    # 🛡️ Whiro audit request
    # -----------------------------------------------------
    def request_whiro_audit(self, doc_id: str, content: str):
        payload = {
            "task_type": "whiro_audit_document",
            "payload": {
                "document_id": doc_id,
                "content": str(content)[:5000],
                "audit_type": "cultural_compliance",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "tiwhanawhana_intake_bridge"
            },
            "status": "pending",
            "priority": 3
        }
        save_to_supabase("task_queue", payload)
        logger.info(f"🛡️ Whiro audit queued for {doc_id}")

    # -----------------------------------------------------
    # 💓 Mauri heartbeat
    # -----------------------------------------------------
    def log_heartbeat(self):
        heartbeat = {
            "rotation_nonce": hashlib.md5(datetime.utcnow().isoformat().encode()).hexdigest(),
            "signature": RONGOHIA_GLYPH["glyph"],
            "source": "intake_bridge",
        }
        save_to_supabase("rongohia.meta", heartbeat)
        logger.info("💓 Mauri heartbeat logged")

    # -----------------------------------------------------
    # 🔁 Intake loop
    # -----------------------------------------------------
    async def run_intake_loop(self, interval: int = 60):
        logger.info(f"🌀 Intake loop active (every {interval}s)")
        seen = set()
        while True:
            try:
                docs = self.scan_intake_folder()
                for doc in docs:
                    key = (doc["file_name"], doc["modified"])
                    if key not in seen:
                        await self.process_document(doc)
                        seen.add(key)
                self.log_heartbeat()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"❌ Loop error: {e}")
                await asyncio.sleep(interval)

    # -----------------------------------------------------
    # 🧬 ID generator
    # -----------------------------------------------------
    def _generate_id(self, name: str) -> str:
        ts = datetime.now(timezone.utc).isoformat()
        return f"intake_{hashlib.md5(f'{name}_{ts}'.encode()).hexdigest()[:12]}"


# ---------------------------------------------------------
# 🚀 Main CLI
# ---------------------------------------------------------
async def main():
    bridge = TiwhanawhanaIntakeBridge()
    docs = bridge.scan_intake_folder()

    for doc in docs:
        result = await bridge.process_document(doc)
        print(f"✅ {doc['file_name']} → {result['status']}")

    bridge.log_heartbeat()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "loop":
        asyncio.run(TiwhanawhanaIntakeBridge().run_intake_loop())
    else:
        asyncio.run(main())
