#!/usr/bin/env bash
set -eo pipefail

echo "[*] Halting Critical RAG Harness Server..."

SERVER_PID=$(pgrep -f "core.server" || true)

if [ -n "$SERVER_PID" ]; then
    echo "[*] Killing process $SERVER_PID..."
    kill "$SERVER_PID" || true
    sleep 1
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "[!] Force terminating PID $SERVER_PID..."
        kill -9 "$SERVER_PID" || true
    fi
    echo "[+] Harness Server stopped."
else
    echo "[!] No active core.server process found."
fi

# Ensure port 8090 is completely released
if lsof -Pi :8090 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "[*] Freeing lingering socket on port 8090..."
    fuser -k 8090/tcp 2>/dev/null || true
fi

echo "[+] Port 8090 released."
