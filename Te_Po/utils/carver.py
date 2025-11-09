# -*- coding: utf-8 -*-
from Te_Po.utils.safety_guard import safe_remove, safe_rmdir, safe_rename

# example:
def delete_path(path: str) -> None:
    # this will be blocked automatically for protected zones
    safe_remove(path)
# this will be blocked automatically for protected zones
    safe_rmdir(path)

import os, json, datetime
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client
from Te_Po.utils.safety_guard import protect_env

# 🛡️  enable protection first
protect_env()

# 🔧 load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
DEN_URL = os.getenv("DEN_URL")
DEN_API_KEY = os.getenv("DEN_API_KEY")

# 🌿 load mauri
mauri_path = Path(__file__).parent.parent / ".mauri" / "rongohia" / "mauri.json"
mauri = json.loads(mauri_path.read_text()) if mauri_path.exists() else {}

glyph = mauri.get("glyph", "🌀")
kaitiaki = mauri.get("name", "Rongohia")
print(f"{glyph} Carver reflection mode — {kaitiaki}")

# 🌐 connect Supabase
supabase = None
if DEN_URL and DEN_API_KEY:
    try:
        supabase = create_client(DEN_URL, DEN_API_KEY)
        print(f"🌐 Supabase connected → {DEN_URL}")
    except Exception as e:
        print(f"⚠️  Supabase unavailable: {e}")

# 🔍 reflection summary
def reflect_state():
    print("\n🌙 Carver reflection:")
    print(f"  🗓️  Time: {datetime.datetime.now(datetime.timezone.utc)}")
    print(f"  💽  Working dir: {Path.cwd()}")
    print(f"  🧩  Supabase: {'connected' if supabase else 'offline'}")
    print(f"  🔑  Kaitiaki: {kaitiaki}")
    print(f"  ⚙️  Mode: SAFE / non-destructive\n")

if __name__ == "__main__":
    reflect_state()
