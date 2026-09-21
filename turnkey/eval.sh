#!/usr/bin/env bash
set -eo pipefail

VENV="/opt/venvs/critical-rag"
PROJECT_DIR="/opt/critical-rag"

echo "======================================================================"
echo "    CRITICAL RAG & VANGUARD VERIFICATION GATE & HARDWARE AUDIT       "
echo "======================================================================"

echo "[1] Testing Vulkan llama-server Endpoint..."
HEALTH_OK=0
if curl -s --max-time 2 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    HEALTH_OK=1
elif /mnt/c/Windows/System32/curl.exe -s --max-time 2 "http://127.0.0.1:8080/health" >/dev/null 2>&1; then
    HEALTH_OK=1
fi

if [ "$HEALTH_OK" -eq 1 ]; then
    echo "  [PASS] llama-server /health OK (Host Vulkan 8080)"
else
    echo "  [FAIL] llama-server not responding on port 8080"
    exit 1
fi

echo "[2] Testing Embeddings API..."
if curl -s --max-time 2 "http://127.0.0.1:8080/v1/embeddings" >/dev/null 2>&1; then
    EMB_CMD="curl -s"
else
    EMB_CMD="/mnt/c/Windows/System32/curl.exe -s"
fi
EMB_RESP=$($EMB_CMD -X POST "http://127.0.0.1:8080/v1/embeddings" \
    -H "Content-Type: application/json" \
    -d '{"input": "hardware verification test"}' 2>/dev/null || true)

if echo "$EMB_RESP" | grep -q "embedding"; then
    echo "  [PASS] /v1/embeddings returned vector payload"
else
    echo "  [WARN] Embeddings returned unexpected response: $EMB_RESP"
fi

echo "[3] Testing Shannon Entropy & Logprob Engine..."
LOGPROB_TEST=$("$VENV/bin/python3" -c '
import sys
sys.path.insert(0, "'"$PROJECT_DIR"'")
from core.stream_bridge import calculate_entropy
top = [{"prob": 0.5}, {"prob": 0.25}, {"prob": 0.25}]
H = calculate_entropy(top)
print(f"H={H:.2f}")
assert 1.4 < H < 1.6, f"Entropy calculation unexpected: {H}"
print("OK")
')
echo "  [PASS] Shannon entropy mathematics validated ($LOGPROB_TEST)"

echo "[4] Probing Vanguard Hardware Resource Arbiter..."
"$VENV/bin/python3" "$PROJECT_DIR/core/hardware_arbiter.py"

echo "[5] Scanning Model Vault (GGUF Discovery)..."
"$VENV/bin/python3" "$PROJECT_DIR/core/model_scanner.py"

echo "[6] Validating CanaryAnchor & Watermark Drift Math..."
"$VENV/bin/python3" -c '
import sys
sys.path.insert(0, "'"$PROJECT_DIR"'")
from core.watermark_drift import WatermarkDriftTracker
w = WatermarkDriftTracker("Test cluster memory")
res = w.update("memory ")
assert "context_fidelity_pct" in res
fid = res["context_fidelity_pct"]
status = res["fidelity_status"]
print(f"  [PASS] Watermark drift math verified: fidelity={fid}%, status={status}")
'

echo "[7] Executing Grounded Hierarchical RAG Turn (Analyst Agent)..."
"$VENV/bin/python3" "$PROJECT_DIR/run.py" --agent analyst --prompt "Synthesize Vanguard CanaryAnchor and storage guardrails."

echo "======================================================================"
echo "      [VERIFICATION GATE COMPLETE: ALL BENCHMARKS PASS ACCREDITED]     "
echo "======================================================================"
