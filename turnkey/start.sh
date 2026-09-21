#!/usr/bin/env bash
set -eo pipefail

VENV="/opt/venvs/critical-rag"
PROJECT_DIR="/opt/critical-rag"
LOG_FILE="/tmp/critical_rag_server.log"

echo "[*] Initializing Critical RAG Sovereign Harness in isolated environment..."

# Check if port 8090 is already in use
if lsof -Pi :8090 -sTCP:LISTEN -t >/dev/null 2>&1 || nc -z -w 1 127.0.0.1 8090 2>/dev/null; then
    echo "[!] Port 8090 is already active."
    SERVER_PID=$(pgrep -f "core.server" || true)
    if [ -n "$SERVER_PID" ]; then
        echo "[+] Existing server running under PID $SERVER_PID."
    fi
else
    echo "[*] Launching core.server on port 8090..."
    cd "$PROJECT_DIR"
    nohup "$VENV/bin/python3" -m core.server > "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    sleep 1.5

    if kill -0 "$NEW_PID" 2>/dev/null; then
        echo "[+] Sovereign Harness Server successfully started (PID: $NEW_PID)."
        echo "    Logs: $LOG_FILE"
    else
        echo "[-] Failed to start server. Output from log:"
        tail -n 20 "$LOG_FILE"
        exit 1
    fi
fi

# Verify health
echo "[*] Probing Harness API..."
if curl -s --max-time 3 "http://127.0.0.1:8090/api/status" >/dev/null 2>&1; then
    echo "[+] Harness API is healthy and answering on http://localhost:8090"
    echo "[+] Web Cockpit: http://localhost:8090"
else
    echo "[!] Server started, but API probe timed out. Check logs: $LOG_FILE"
fi
