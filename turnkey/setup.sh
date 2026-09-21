#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "======================================================================"
echo "      CRITICAL RAG SOVEREIGN HARNESS — SYSTEM REPLICATION SETUP      "
echo "======================================================================"

# 1. Detect or Create Python Virtual Environment
VENV=""
if [ -d "/opt/venvs/critical-rag" ]; then
    VENV="/opt/venvs/critical-rag"
elif [ -d "$PROJECT_DIR/.venv" ]; then
    VENV="$PROJECT_DIR/.venv"
else
    echo "[*] Creating fresh isolated Python virtual environment..."
    python3 -m venv "$PROJECT_DIR/.venv"
    VENV="$PROJECT_DIR/.venv"
fi
echo "[+] Using Python Virtualenv: $VENV"

# 2. Upgrade pip and install requirements
echo "[*] Installing cluster dependencies from requirements.txt..."
"$VENV/bin/pip" install --quiet --upgrade pip
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    "$VENV/bin/pip" install --quiet -r "$PROJECT_DIR/requirements.txt"
    echo "[+] Dependencies successfully verified."
fi

# 3. Ensure Directory Structure & Baseline Assets
echo "[*] Verifying directory structure..."
mkdir -p "$PROJECT_DIR/corpus" "$PROJECT_DIR/agents" "$PROJECT_DIR/core" "$PROJECT_DIR/ui" "$PROJECT_DIR/turnkey"

# Ensure ui/state.json exists
if [ ! -f "$PROJECT_DIR/ui/state.json" ]; then
    echo '{"active_agent": {"name": "engineer", "role": "Systems Architecture"}, "step": 0, "status": "idle"}' > "$PROJECT_DIR/ui/state.json"
fi

# Ensure executable permissions on all turnkey scripts
chmod +x "$PROJECT_DIR/turnkey.sh" "$PROJECT_DIR"/turnkey/*.sh "$PROJECT_DIR"/*.py 2>/dev/null || true

# 4. Probe Hardware & Cluster Connectivity
echo "[*] Probing cluster nodes..."
if curl -s --max-time 1 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    echo "  [ONLINE] llama-server (Port 8080)"
elif /mnt/c/Windows/System32/curl.exe -s --max-time 1 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    echo "  [ONLINE] llama-server (Port 8080 via Host Bridge)"
else
    echo "  [NOTICE] llama-server on Port 8080 not detected. Start llama-server on host to enable GPU inference."
fi

# 5. Ingest / Index Canonical Corpus
echo "[*] Initializing Hierarchical RAG index..."
"$VENV/bin/python3" -c '
import sys
sys.path.insert(0, "'"$PROJECT_DIR"'")
from core.hierarchical_retrieval import HierarchicalRetriever
hr = HierarchicalRetriever()
print(f"  [+] RAG Ready: {len(hr.documents)} Docs, {len(hr.sections)} Sections, {len(hr.chunks)} Chunks indexed.")
'

echo "======================================================================"
echo "          [REPLICATION SETUP COMPLETE: SYSTEM READY TO RUN]           "
echo "======================================================================"
echo "Next commands:"
echo "  ./turnkey.sh status       # Check cluster health"
echo "  ./turnkey.sh start        # Launch web server & cockpit on port 8090"
echo "  ./turnkey.sh run --prompt 'Diagnose rocket pressure.'"
echo "======================================================================"
