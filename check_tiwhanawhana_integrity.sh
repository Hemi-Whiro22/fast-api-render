#!/usr/bin/env bash
# check_tiwhanawhana_integrity.sh
# Verifies package setup and UTF-8 readiness after re-org

set -e
cd ~/Desktop/tiwhanawhana

echo "🐺 Checking Tiwhanawhana package health..."
echo "------------------------------------------"

# 1️⃣ Ensure backend/core/main.py exists
test -f backend/core/main.py && echo "✅ FastAPI entrypoint found"

# 2️⃣ Confirm all code folders contain __init__.py
echo "🧩 Missing __init__.py files (should be empty list):"
find backend -type d \( -path "*/__pycache__" -prune \) -o -type d -exec bash -c 'test -f "{}/__init__.py" || echo "❌ {}"' \;

# 3️⃣ Check UTF-8 header in Python files
echo "🔤 Files missing UTF-8 header:"
grep -L "# -*- coding: utf-8 -*-" $(find backend -type f -name "*.py") || echo "✅ All have UTF-8 headers"

# 4️⃣ Run import test under PYTHONPATH=backend
echo "🧠 Testing imports..."
PYTHONPATH=backend ./.venv/bin/python - <<'PYCODE'
import importlib, sys
try:
    app = importlib.import_module("Te_Po.core.main")
    print("✅ Te_Po.core.main imported successfully")
except Exception as e:
    print("❌ Import failed:", e)
    sys.exit(1)
PYCODE

# 5️⃣ Optional quick boot test (comment out if not needed)
# PYTHONPATH=Te-Po ./.venv/bin/python -m uvicorn Te_Po.core.main:app --reload --port 8001

echo "------------------------------------------"
echo "🌊 Verification complete — review ❌ lines if any."
echo "🐺 Tiwhanawhana is ready to roar!"