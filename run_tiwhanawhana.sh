#!/usr/bin/env bash
# Simple helper to launch the Tiwhanawhana FastAPI application with logging.
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOG_DIR="$REPO_ROOT/logs"
VENV_PATH="$REPO_ROOT/.venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "Missing virtual environment at $VENV_PATH" >&2
    exit 1
fi

# Activate the virtual environment
# shellcheck source=/dev/null
source "$VENV_PATH/bin/activate"

export LANG="mi_NZ.UTF-8"
export LC_ALL="mi_NZ.UTF-8"
export PYTHONPATH="$REPO_ROOT"

mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$LOG_DIR/tiwhanawhana-$TIMESTAMP.log"

echo "Writing Tiwhanawhana logs to $LOG_FILE"

exec uvicorn Te_Po.core.main:app --reload >>"$LOG_FILE" 2>&1
