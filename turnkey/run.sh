#!/usr/bin/env bash
set -eo pipefail

VENV="/opt/venvs/critical-rag"
PROJECT_DIR="/opt/critical-rag"

cd "$PROJECT_DIR"
exec "$VENV/bin/python3" "$PROJECT_DIR/run.py" "$@"
