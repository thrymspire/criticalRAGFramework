#!/usr/bin/env python3
"""
Critical RAG Runtime Entry Point
Supports on-the-fly agent switching via CLI flag (--agent), prompt execution,
artifact generation, or launches the live telemetry server.
"""

import sys
import argparse
import subprocess
import tempfile
import re
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.agent_loader import load_agent, set_active_agent, list_available_agents
from core.harness import HarnessOrchestrator
from core.server import start_harness_server


def export_alien_artifact(agent_name: str, prompt: str, output_text: str, citations: list, verification: dict) -> str:
    """Generate an Alien Artifact HTML dashboard for the turn execution."""
    clean_topic = re.sub(r'[^a-zA-Z0-9_]+', '_', f"{agent_name}_{prompt[:30]}").strip('_')
    
    content = f"""# Critical RAG Execution: {agent_name.upper()}

- **Agent Persona**: `{agent_name}`
- **Verification Status**: `{verification.get('verification_status', 'UNKNOWN')}`
- **Confidence**: `{verification.get('retrieval_confidence', 'N/A')}`
- **Mean Entropy**: `{verification.get('mean_entropy_bits', 'N/A')} bits`
- **Citations**: `{', '.join(citations) if citations else 'None'}`

---

## 1. Directive / Prompt
> {prompt}

---

## 2. Grounded Agent Output
{output_text}

---

## 3. Retrieval Grounding Telemetry
"""
    if citations:
        content += "### Verified Source Chunks\n"
        for c in citations:
            content += f"- `{c}`\n"
    else:
        content += "_No direct chunk citations triggered._\n"

    content += f"""
---

## 4. Token Physics & Entropy Profile
- **Retrieval Confidence**: {verification.get('retrieval_confidence', 'N/A')}
- **Mean Token Entropy**: {verification.get('mean_entropy_bits', 'N/A')} bits
- **Audit Gate**: {verification.get('verification_status', 'N/A')}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        wslpath_res = subprocess.run(["wslpath", "-w", tmp_path], capture_output=True, text=True)
        win_tmp = wslpath_res.stdout.strip()
        res = subprocess.run([
            "cmd.exe", "/c", "python",
            "./scripts/generate_alien_artifact.py",
            "--topic", clean_topic,
            "--file", win_tmp
        ], capture_output=True, text=True)

        out = res.stdout.strip()
        if "Artifact generated successfully:" in out:
            artifact_path = out.split("Artifact generated successfully:")[1].strip()
            return artifact_path
        return out
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Critical RAG Sovereign Runtime & Agent Harness")
    parser.add_argument("--agent", default="engineer", help="Agent to activate (engineer, framework, mechanic, analyst, debug)")
    parser.add_argument("--prompt", help="Direct prompt to execute against the active agent")
    parser.add_argument("--artifact", action="store_true", help="Generate an Alien Artifact HTML dashboard for this execution")
    parser.add_argument("--server", action="store_true", help="Start the live UI streaming server (default if no prompt)")
    parser.add_argument("--list", action="store_true", help="List all available agents")
    parser.add_argument("--port", type=int, default=8090, help="Server port (default: 8090)")
    args = parser.parse_args()

    if args.list:
        print("\n=== Available Critical RAG Agents ===")
        for a in list_available_agents():
            print(f"• [{a['name']:<10}] {a['role']:<35} (temp: {a['temperature']})")
            print(f"  {a['description']}")
        print()
        return

    # Activate requested agent
    active_agent = set_active_agent(args.agent)
    print(f"[*] Activated Agent: [{active_agent['name'].upper()}] - {active_agent['role']}")
    print(f"[*] Directives loaded from {active_agent['path']}")

    if args.prompt:
        print(f"\n[USER PROMPT] {args.prompt}")
        orchestrator = HarnessOrchestrator()
        orchestrator.directive = active_agent["system_prompt"]
        print("\n--- Executing ReAct Turn ---")
        
        output_tokens = []
        retrieved_chunks = []
        last_verification = {}

        for event in orchestrator.stream_agent_turn(args.prompt):
            if event["type"] == "retrieval":
                retrieved_chunks = [c["id"] for c in event.get("retrieved", [])]
                print(f"[RAG PROBE] Grounded with {len(retrieved_chunks)} chunks: {retrieved_chunks}")
            elif event["type"] == "token":
                tok = event["chosen_token"]
                output_tokens.append(tok)
                sys.stdout.write(tok)
                sys.stdout.flush()
            elif event["type"] == "verification":
                last_verification = event["verification"]
                v = last_verification
                print(f"\n\n--- Verification Summary ({v.get('verification_status')}) ---")
                print(f"• Confidence: {v.get('retrieval_confidence')} | Mean Entropy: {v.get('mean_entropy_bits')}b")
                print(f"• Chunks Cited: {v.get('chunks_cited')}")
        print()

        if args.artifact:
            print("\n[*] Packaging output into Alien Artifact...")
            full_text = "".join(output_tokens)
            artifact_file = export_alien_artifact(
                args.agent,
                args.prompt,
                full_text,
                last_verification.get("chunks_cited", retrieved_chunks),
                last_verification
            )
            print(f"[+] Artifact Created: {artifact_file}")
    else:
        # Launch server with this agent active
        start_harness_server(port=args.port)


if __name__ == "__main__":
    main()
