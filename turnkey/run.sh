#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(cd "$SCRIPT_DIR/.." && pwd)}"

if [ -d "/opt/venvs/critical-rag" ]; then
    VENV="/opt/venvs/critical-rag"
elif [ -d "$PROJECT_DIR/.venv" ]; then
    VENV="$PROJECT_DIR/.venv"
else
    VENV="$(dirname "$(dirname "$(command -v python3)")")"
fi

PYTHON_BIN="${VENV}/bin/python3"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="$(command -v python3)"
fi

cd "$PROJECT_DIR"
exec "$PYTHON_BIN" "$PROJECT_DIR/run.py" "$@"
