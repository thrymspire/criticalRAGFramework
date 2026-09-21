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
AGENT_NAME="$1"

if [ -z "$AGENT_NAME" ]; then
    echo "[*] Querying current agent status and available agents..."
    if curl -s --max-time 1 "http://127.0.0.1:8090/api/agents" >/dev/null 2>&1; then
        curl -s "http://127.0.0.1:8090/api/agents" | "$PYTHON_BIN" -c '
import sys, json
data = json.load(sys.stdin)
active = data.get("active", {})
act_name = active.get("name", "unknown").upper()
act_role = active.get("role", "")
print("\nACTIVE AGENT: [" + act_name + "] - " + act_role)
print("Model: " + str(active.get("model")) + " | Temp: " + str(active.get("temperature")) + " | Top-Logprobs: " + str(active.get("top_logprobs")))
print("\nAVAILABLE AGENTS:")
for a in data.get("available", []):
    mark = "(*)" if a.get("name") == active.get("name") else "   "
    name = a.get("name", "")
    role = a.get("role", "")
    temp = str(a.get("temperature", 0.0))
    print(f"  {mark} {name:<10} | {role} (temp: {temp})")
print("\nUsage to switch: ./turnkey.sh agent <agent_name>")
'
    else
        "$PYTHON_BIN" "$PROJECT_DIR/run.py" --list
        echo "Usage to switch: ./turnkey.sh agent <agent_name>"
    fi
    exit 0
fi

echo "[*] Switching active runtime agent to: $AGENT_NAME..."

# Try switching via API first if server is running
if curl -s --max-time 1 "http://127.0.0.1:8090/api/agents" >/dev/null 2>&1; then
    curl -s -X POST "http://127.0.0.1:8090/api/agents/switch" \
        -H "Content-Type: application/json" \
        -d "{\"agent\":\"$AGENT_NAME\"}" | "$PYTHON_BIN" -c '
import sys, json
res = json.load(sys.stdin)
if res.get("status") == "ok":
    act = res.get("active", {})
    name = act.get("name", "").upper()
    role = act.get("role", "")
    path = act.get("path", "")
    print("[+] Hot-switch SUCCESSFUL: [" + name + "] is now ACTIVE.")
    print("    Role: " + role)
    print("    System prompt: " + path)
else:
    err = res.get("error", "Unknown error")
    print("[-] Switch failed: " + err)
'
else
    # Fallback to direct Python loader
    "$PYTHON_BIN" -c '
import sys
sys.path.insert(0, "'"$PROJECT_DIR"'")
from core.agent_loader import set_active_agent
act = set_active_agent("'"$AGENT_NAME"'")
name = act.get("name", "").upper()
role = act.get("role", "")
print("[+] Switch SUCCESSFUL (offline): [" + name + "] is now default.")
print("    Role: " + role)
'
fi
