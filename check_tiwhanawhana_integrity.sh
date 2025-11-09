#!/usr/bin/env bash
# check_tiwhanawhana_integrity.sh
# Verifies package setup and UTF-8 readiness after re-org

set -e
cd ~/Desktop/tiwhanawhana

echo "🐺 Checking Tiwhanawhana package health..."
echo "------------------------------------------"

# 1️⃣ Ensure Te_Po/core/main.py exists (AwaNet realm structure)
test -f Te_Po/core/main.py && echo "✅ Te_Po FastAPI entrypoint found"

# 2️⃣ Check if all Python modules have __init__.py files

find Te_Po -type d \( -path "*/__pycache__" -prune \) -o -type d -exec bash -c 'test -f "{}/__init__.py" || echo "❌ {}"' \;

# 3️⃣ Check if all .py files have correct encoding headers
grep -L "# -*- coding: utf-8 -*-" $(find Te_Po -type f -name "*.py") || echo "✅ All have UTF-8 headers"

# 4️⃣ Run import test under PYTHONPATH=. for Te_Po

PYTHONPATH=. ./.venv/bin/python - <<'PYCODE'

# 5️⃣ Optional quick boot test (comment out if not needed)
# PYTHONPATH=Te-Po ./.venv/bin/python -m uvicorn Te_Po.core.main:app --reload --port 8001

echo "------------------------------------------"
echo "🌊 Verification complete — review ❌ lines if any."
echo "🐺 Tiwhanawhana is ready to roar!"