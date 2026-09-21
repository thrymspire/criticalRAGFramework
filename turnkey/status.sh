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

echo "======================================================================"
echo "          CRITICAL RAG CLUSTER TELEMETRY & STATUS (ISOLATED)          "
echo "======================================================================"

check_port() {
    local host="$1"
    local port="$2"
    local name="$3"
    if nc -z -w 1 "$host" "$port" 2>/dev/null || curl -s --max-time 1 "http://${host}:${port}/" >/dev/null 2>&1; then
        echo -e "  [ONLINE]  $name (http://${host}:${port})"
    else
        echo -e "  [OFFLINE] $name (http://${host}:${port})"
    fi
}

echo "[1] Cluster Node Connectivity:"
if curl -s --max-time 1 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    echo -e "  [ONLINE]  llama-server (Vulkan Host Engine) (http://127.0.0.1:8080)"
elif /mnt/c/Windows/System32/curl.exe -s --max-time 1 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    echo -e "  [ONLINE]  llama-server (Vulkan Host Engine) (http://127.0.0.1:8080 via Host Bridge)"
else
    echo -e "  [OFFLINE] llama-server (Vulkan Host Engine) (http://127.0.0.1:8080)"
fi
check_port "127.0.0.1" 8090 "Harness Streaming Server (harness-enclave)"
check_port "127.0.0.1" 8188 "ComfyUI Node (ROCm gfx1103)"
check_port "127.0.0.1" 2375 "Docker Engine (Auxiliary Container)"

echo ""
echo "[2] Active Harness Server Status:"
SERVER_PID=$(pgrep -f "core.server" || true)
if [ -n "$SERVER_PID" ]; then
    echo "  Process: Active (PID: $SERVER_PID)"
    echo "  Virtualenv: $VENV"
    echo "  UI Endpoint: http://localhost:8090"
else
    echo "  Process: Not running (use ./turnkey.sh start to launch)"
fi

echo ""
echo "[3] Active Sovereign Agent & Inventory:"
if curl -s --max-time 1 "http://127.0.0.1:8090/api/agents" >/dev/null 2>&1; then
    curl -s "http://127.0.0.1:8090/api/agents" | "$PYTHON_BIN" -c '
import sys, json
data = json.load(sys.stdin)
active = data.get("active", {})
act_name = active.get("name", "unknown").upper()
act_role = active.get("role", "")
act_path = active.get("path", "")
print("  Active Agent: [" + act_name + "] - " + act_role)
print("  Directive:    " + act_path)
print("  Available:")
for a in data.get("available", []):
    mark = "(*)" if a.get("name") == active.get("name") else "   "
    name = a.get("name", "")
    role = a.get("role", "")
    temp = str(a.get("temperature", 0.0))
    print(f"    {mark} {name:<10} | {role} (temp: {temp})")
'
else
    "$PYTHON_BIN" "$PROJECT_DIR/run.py" --list
fi

echo ""
echo "[4] Corpus Provenance Storage:"
if [ -f "$PROJECT_DIR/corpus_seed.json" ]; then
    DOC_COUNT=$("$PYTHON_BIN" -c '
import json
with open("'$PROJECT_DIR'/corpus_seed.json") as f:
    docs = json.load(f)
print(len(docs))
')
    echo "  Seed Corpus: $PROJECT_DIR/corpus_seed.json ($DOC_COUNT documents loaded)"
fi
if [ -d "/data/corpus" ]; then
    EXT_COUNT=$(find /data/corpus -type f 2>/dev/null | wc -l || echo 0)
    echo "  Storage Node: /data/corpus ($EXT_COUNT files indexed)"
fi

echo "======================================================================"
