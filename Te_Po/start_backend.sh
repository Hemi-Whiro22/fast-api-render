#!/usr/bin/env bash
set -euo pipefail

uvicorn app.main:app --host 0.0.0.0 --port ${FASTAPI_PORT:-8000} --reload
