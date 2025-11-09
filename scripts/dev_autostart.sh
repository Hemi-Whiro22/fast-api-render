#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "🌕 Awakening Tiwhanawhana orchestrator..."
python3 scripts/startup_cli.py || echo "⚠️ startup_cli.py exited early"

echo "🚀 Starting Te-Po..."
uvicorn Te_Po.core.main:app --reload &
BACKEND_PID=$!
sleep 2

echo "🎨 Starting frontend..."
cd frontend
npm run dev || {
  echo "⚠️ Frontend exited unexpectedly" >&2
  if kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}" || true
  fi
  exit 1
}
