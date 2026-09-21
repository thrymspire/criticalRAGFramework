#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="${1:-$PROJECT_DIR}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="critical_rag_replication_bundle_${TIMESTAMP}.tar.gz"
LATEST_NAME="critical_rag_replication_bundle.tar.gz"
TARGET_FILE="$OUTPUT_DIR/$ARCHIVE_NAME"
LATEST_LINK="$OUTPUT_DIR/$LATEST_NAME"

echo "======================================================================"
echo "    CRITICAL RAG SOVEREIGN HARNESS — PACKAGING REPLICATION BUNDLE    "
echo "======================================================================"
echo "[*] Source Directory: $PROJECT_DIR"
echo "[*] Destination:      $TARGET_FILE"

# Collect items to package that exist
ITEMS=()
for item in core agents ui corpus turnkey config requirements.txt run.py turnkey.sh \
            absorb_corpus.py extract_logprobs.py index.html circle.js styles.css corpus_seed.json; do
    if [ -e "$PROJECT_DIR/$item" ]; then
        ITEMS+=("$item")
    fi
done

# Create archive packaging essential components
tar -czf "$TARGET_FILE" \
    -C "$PROJECT_DIR" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.pyo" \
    --exclude=".git" \
    --exclude="logs/*.log" \
    --exclude="models" \
    --exclude="*.tar.gz" \
    "${ITEMS[@]}"

# Create latest copy
cp -f "$TARGET_FILE" "$LATEST_LINK"

BUNDLE_SIZE=$(du -h "$TARGET_FILE" | cut -f1)

echo "[+] Replication bundle created successfully!"
echo "    Archive: $TARGET_FILE ($BUNDLE_SIZE)"
echo "    Latest:  $LATEST_LINK"
echo ""
echo "======================================================================"
echo "               REPLICATION & REDEPLOYMENT INSTRUCTIONS                "
echo "======================================================================"
echo "To redeploy onto a fresh machine or isolated container:"
echo ""
echo "1. Extract bundle:"
echo "   mkdir -p ~/Critical-RAG && tar -xzf $LATEST_NAME -C ~/Critical-RAG"
echo ""
echo "2. Run one-command automated setup:"
echo "   cd ~/Critical-RAG"
echo "   ./turnkey.sh setup"
echo ""
echo "3. Verify cluster health:"
echo "   ./turnkey.sh status"
echo ""
echo "4. Launch system:"
echo "   ./turnkey.sh start"
echo "======================================================================"
