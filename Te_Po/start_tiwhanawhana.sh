#!/usr/bin/env bash
set -e

# Resolve paths
SCRIPT_PATH="$(readlink -f "$0")"
REPO_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

cd "$REPO_DIR"

# Define the server command
SERVER_CMD="cd '$REPO_DIR' && PYTHONPATH=Te-Po ./.venv/bin/python -m uvicorn Te_Po.core.main:app --reload"

# Launch in new GNOME terminal if available
if command -v gnome-terminal >/dev/null 2>&1; then
  gnome-terminal --title="🐺 Tiwhanawhana Server" -- bash -c "$SERVER_CMD; exec bash"
else
  # fallback if no gnome-terminal
  bash -c "$SERVER_CMD"
fi
