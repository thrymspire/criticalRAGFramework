#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMAND="${1:-status}"
shift || true

case "$COMMAND" in
    start)
        exec "$SCRIPT_DIR/turnkey/start.sh" "$@"
        ;;
    stop)
        exec "$SCRIPT_DIR/turnkey/stop.sh" "$@"
        ;;
    status)
        exec "$SCRIPT_DIR/turnkey/status.sh" "$@"
        ;;
    agent)
        exec "$SCRIPT_DIR/turnkey/agent.sh" "$@"
        ;;
    run)
        exec "$SCRIPT_DIR/turnkey/run.sh" "$@"
        ;;
    eval|gate)
        exec "$SCRIPT_DIR/turnkey/eval.sh" "$@"
        ;;
    setup)
        exec "$SCRIPT_DIR/turnkey/setup.sh" "$@"
        ;;
    replicate|package)
        exec "$SCRIPT_DIR/turnkey/replicate.sh" "$@"
        ;;
    help|--help|-h)
        echo "=================================================================="
        echo "       CRITICAL RAG SOVEREIGN HARNESS — ISOLATED TURNKEY          "
        echo "=================================================================="
        echo "Usage: ./turnkey.sh <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  setup           Bootstrap environment, install deps, index corpus"
        echo "  start           Launch the background streaming harness server (port 8090)"
        echo "  stop            Terminate the streaming server and free port 8090"
        echo "  status          Display comprehensive node health and agent telemetry"
        echo "  agent [name]    Inspect active agent or hot-switch to a new persona"
        echo "  run [args]      Execute an agent turn via CLI (e.g. --agent analyst --prompt '...')"
        echo "  eval            Run the verification test suite and hardware audit gate"
        echo "  replicate       Package system into a portable replication tarball (.tar.gz)"
        echo "  help            Show this help dialog"
        echo "=================================================================="
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo "Run './turnkey.sh help' for usage instructions."
        exit 1
        ;;
esac
