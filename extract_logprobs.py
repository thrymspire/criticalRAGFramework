#!/usr/bin/env bash
"""": # Bash wrapper to run directly or via python
exec /opt/venvs/critical-rag/bin/python3 "$0" "$@"
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Ensure core is in python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from core.llm_client import stream_tokens_with_logprobs
from core.agent_loader import load_agent


def main():
    parser = argparse.ArgumentParser(description="Phase 1: Token Logprob & Shannon Entropy Extraction")
    parser.add_argument("--prompt", type=str, default="What is 2+2? Answer in one sentence.", help="Input prompt")
    parser.add_argument("--max-tokens", type=int, default=16, help="Maximum generated tokens")
    parser.add_argument("--top-logprobs", type=int, default=5, help="Number of candidate logprobs to request")
    parser.add_argument("--server", type=str, default="http://127.0.0.1:8080", help="llama-server URL")
    parser.add_argument("--agent", type=str, default="engineer", help="Agent persona to load directives from")
    parser.add_argument("--compact", action="store_true", help="Print compact one-line JSON per token")

    args = parser.parse_args()

    # Load agent directive
    system_prompt = None
    if args.agent:
        try:
            agent_data = load_agent(args.agent)
            system_prompt = agent_data.get("system_prompt")
        except Exception:
            pass

    token_count = 0
    full_text = []

    for step_obj in stream_tokens_with_logprobs(
        prompt=args.prompt,
        server_url=args.server,
        max_tokens=args.max_tokens,
        top_logprobs=args.top_logprobs,
        system_prompt=system_prompt
    ):
        full_text.append(step_obj["chosen_token"])
        token_count += 1

        if args.compact:
            print(json.dumps(step_obj))
        else:
            print(json.dumps(step_obj, indent=2))
        sys.stdout.flush()

    if not args.compact:
        print(f"\n--- Complete Generated Sequence ({token_count} tokens) ---", file=sys.stderr)
        print("".join(full_text).strip(), file=sys.stderr)


if __name__ == "__main__":
    main()
