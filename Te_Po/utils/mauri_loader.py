#!/usr/bin/env python3
"""
🌙 Mauri Loader — Tri-Contextual Trace Mode
------------------------------------------
Loads environment + mauri.json → emits mana-trace to Carver, Kitenga, and Whiro.
"""

import os, json, datetime, hashlib
from supabase import create_client
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 1️⃣ Load environment files in priority order
env_candidates = [
    ROOT / ".env.local",
    ROOT / ".env",
    ROOT / ".mauri" / "tiwhanawhana.env",
    ROOT / ".mauri" / ".env",
    ROOT / ".mauri" / "rongohia" / ".env",
]

loaded_any = False
for candidate in env_candidates:
    if candidate.exists():
        load_dotenv(candidate, override=False)
        print(f"🌿 Loaded environment from {candidate.relative_to(ROOT)}")
        loaded_any = True

if not loaded_any:
    print("⚠️  No environment files found — please create .env or .mauri/tiwhanawhana.env")

DEN_URL = os.getenv("DEN_URL")
DEN_API_KEY = os.getenv("DEN_API_KEY") or os.getenv("TEPUNA_API_KEY")

# 2️⃣ Load mauri.json
mauri_candidates = [
    ROOT / ".mauri" / "mauri.json",
    ROOT / ".mauri" / "rongohia" / "mauri.json",
]

mauri = {}
glyph, kaitiaki = "🌀", "Rongohia"
for mauri_path in mauri_candidates:
    if not mauri_path.exists():
        continue
    try:
        mauri = json.loads(mauri_path.read_text(encoding="utf-8"))
        glyph = mauri.get("glyph", glyph)
        kaitiaki = mauri.get("name", kaitiaki)
        print(f"{glyph} Kaitiaki: {kaitiaki} ready — mana aligned")
        break
    except json.JSONDecodeError as exc:
        print(f"⚠️  Unable to parse mauri metadata from {mauri_path}: {exc}")
else:
    print("⚠️  No mauri.json metadata found")

# 3️⃣ Supabase client
supabase = None
if DEN_URL and DEN_API_KEY:
    try:
        supabase = create_client(DEN_URL, DEN_API_KEY)
        print(f"🌐 Supabase connected → {DEN_URL}")
    except Exception as e:
        print(f"⚠️  Supabase connection failed: {e}")
else:
    print("⚠️  Supabase credentials missing")

# 4️⃣ Mana Trace writer
def write_mana_trace():
    timestamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    sig = hashlib.md5(timestamp.encode()).hexdigest()[:12]

    trace = {
        "signature": sig,
        "timestamp": timestamp,
        "environment": "dev",
        "kaitiaki": kaitiaki,
        "glyph": glyph,
        "host": os.uname().nodename,
        "cwd": str(Path.cwd()),
    }

    # Local save
    trace_dir = ROOT / ".mauri"
    trace_dir.mkdir(parents=True, exist_ok=True)
    (trace_dir / "trace.json").write_text(json.dumps(trace, indent=2))
    print(f"🌙 Mana-trace written locally: {trace_dir / 'trace.json'}")

def trace_reflector():
    """Reflect the most recent mana-trace from each context."""
    if not supabase:
        print("⚠️  Supabase not available — cannot reflect trace")
        return

    tables = ["carver_context_memory", "kitenga_context_memory", "whiro_context_memory"]
    print("\n🪞 Reflecting latest mana-traces:")
    for t in tables:
        try:
            res = supabase.table(t).select("id, context_name, created_at").order("created_at", desc=True).limit(1).execute()
            if res.data:
                entry = res.data[0]
                print(f"  ✅ {t}: {entry.get('context_name','—')} at {entry.get('created_at')}")
            else:
                print(f"  ⚠️  {t}: no entries yet")
        except Exception as e:
            print(f"  ⚠️  Failed to reflect from {t}: {e}")

def mana_drift_monitor():
    """Compare timestamps to detect drift."""
    if not supabase:
        print("⚠️  Supabase not available — cannot check drift")
        return

    tables = ["carver_context_memory", "kitenga_context_memory", "whiro_context_memory"]
    traces = {}
    for t in tables:
        try:
            res = supabase.table(t).select("created_at").order("created_at", desc=True).limit(1).execute()
            if res.data:
                ts = res.data[0].get("created_at")
                if ts and ts.endswith("Z"):
                    ts = ts[:-1] + "+00:00"
                traces[t] = datetime.datetime.fromisoformat(ts)
        except Exception as e:
            print(f"⚠️  Failed reading timestamp from {t}: {e}")

    if len(traces) < 3:
        print("⚠️  Not enough data for drift check.")
        return

    times = list(traces.values())
    delta = (max(times) - min(times)).total_seconds() / 60
    print("\n🕰️  Mana drift check:")
    if delta < 5:
        print(f"  🟢 All aligned — drift = {delta:.2f} min")
    else:
        print(f"  🟠 Drift detected: {delta:.2f} min")
        for k, v in traces.items():
            print(f"     - {k}: {v.isoformat()}")

if __name__ == "__main__":
    print("mauri_loader ran successfully")
    write_mana_trace()
    trace_reflector()
    mana_drift_monitor()
