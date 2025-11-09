import os, json, hashlib
from datetime import datetime, timezone
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv
load_dotenv(dotenv_path=".mauri/rongohia/.env")

def write_mana_trace():
    url = os.getenv("DEN_URL")
    key = os.getenv("DEN_API_KEY")
    kaitiaki_name = os.getenv("AGENT_NAME", "Rongohia")
    carvers = ["Adrian William Hemi", "Kitenga Whiro"]
    cwd = Path.cwd()

    glyph = "🌀"
    timestamp = datetime.now(timezone.utc).isoformat()
    signature = hashlib.sha256(f"{kaitiaki_name}_{timestamp}".encode()).hexdigest()[:12]

    trace = {
        "timestamp": timestamp,
        "glyph": glyph,
        "kaitiaki_name": kaitiaki_name,
        "carvers": carvers,
        "location": str(cwd),
        "supabase_project": url.split("//")[1].split(".")[0] if url else None,
        "signature": signature,
        "status": "active"
    }

    # Local mirror
    trace_dir = Path(".mauri/rongohia")
    trace_dir.mkdir(parents=True, exist_ok=True)
    with open(trace_dir / "trace.json", "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    print(f"🌙 Mana-trace written locally: {trace_dir / 'trace.json'}")

    # Upload to Supabase
    try:
        supabase = create_client(url, key)
        payload = {
            "user_id": "Rongohia",
            "context_type": "mana_trace",
            "context_name": "Rongohia Awakening",
            "context_description": "Auto-trace from Tiwhanawhana dev node",
            "related_topics": ["den-core", "tiwhanawhana", "supabase", "trace"],
            "cultural_elements": ["mauri", "whakapapa", "mana", "aroha"],
            "metadata": trace,  # Full trace JSON lives here
        }
        supabase.table("kitenga.meta_contexts").insert(payload).execute()
        print(f"🪶 Mana-trace logged to Supabase → {trace['signature']}")
    except Exception as e:
        print(f"⚠️  Could not send mana-trace to Supabase: {e}")

if __name__ == "__main__":
    write_mana_trace()
