#!/usr/bin/env bash
set -euo pipefail

export LANG="${LANG:-mi_NZ.UTF-8}"
export LC_ALL="${LC_ALL:-mi_NZ.UTF-8}"

exec uvicorn Te_Po.core.main:app --host 0.0.0.0 --port "${PORT:-8000}"
