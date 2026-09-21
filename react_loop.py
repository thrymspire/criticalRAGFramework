#!/usr/bin/env python3
"""
Minimal Sovereign ReAct Agent Loop for Critical Path Harness
- Discovers and auto-injects AGENTS.md
- Communicates directly with llama-server at http://127.0.0.1:8080 (or WSL host loopback)
- Queries /v1/chat/completions and /v1/embeddings
- Interfaces with criticalpath-store-v1.0 corpus data
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Ensure UTF-8 output across Windows and Linux terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_SERVER_URLS = [
    "http://127.0.0.1:8080",       # Native Windows Host Vulkan
    "http://localhost:8080",       # Localhost
    "http://172.28.41.31:8080"     # Docker Engine in WSL2 fallback
]


def resolve_server_url() -> str:
    """Finds an active llama-server endpoint."""
    for url in DEFAULT_SERVER_URLS:
        try:
            req = urllib.request.Request(f"{url}/health", headers={"User-Agent": "CriticalRAG-Harness"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status in (200, 503):
                    return url
        except urllib.error.HTTPError as e:
            if e.code in (200, 503):
                return url
        except Exception:
            pass
    return DEFAULT_SERVER_URLS[0]


def load_agents_directive(search_dir: Path) -> str:
    """Auto-discovers and loads AGENTS.md from project root."""
    candidate = search_dir / "AGENTS.md"
    if candidate.exists():
        print(f"[HARNESS] Auto-loaded directive: {candidate}")
        return candidate.read_text(encoding="utf-8")
    
    # Check parent
    parent_candidate = search_dir.parent / "AGENTS.md"
    if parent_candidate.exists():
        print(f"[HARNESS] Auto-loaded directive: {parent_candidate}")
        return parent_candidate.read_text(encoding="utf-8")
    
    return "You are an autonomous Critical Path RAG agent."


def get_embedding(server_url: str, text: str) -> list:
    """Generates dense embedding vector using llama-server /v1/embeddings."""
    payload = json.dumps({"input": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{server_url}/v1/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["data"][0]["embedding"]


def query_chat(server_url: str, messages: list, max_tokens: int = 256) -> str:
    """Calls /v1/chat/completions."""
    payload = json.dumps({
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{server_url}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        msg = data["choices"][0]["message"]
        # In Nemotron / thinking models, content or reasoning_content may be populated
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        if content:
            return content
        return reasoning


def load_store_corpus() -> list:
    """Loads corpus nodes from criticalpath-store-v1.0 if accessible, or local fallback."""
    paths = [
        Path("/data/corpus/critical_path_corpus_seed.json"),
        Path("/mnt/c/Users/Thrym/Desktop/Critical RAG/corpus_seed.json"),
        Path(__file__).parent / "corpus_seed.json"
    ]
    for p in paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return data.get("nodes", [])
            except Exception:
                pass
    return [
        {"id": "CP-NODE-001", "name": "Ingestion", "description": "Extracts and normalizes raw project data into DAG nodes."},
        {"id": "CP-NODE-002", "name": "Storage", "description": "Stores graph structures, relational edges, and embeddings in criticalpath-store-v1.0."},
        {"id": "CP-NODE-003", "name": "Evaluation", "description": "Evaluates float, slack, and model metrics in criticalpath-eval-v1.0."},
        {"id": "CP-NODE-004", "name": "Harness", "description": "Executes ReAct loops, mounts project code, and secures credentials."}
    ]


def run_react_agent(prompt: str):
    """Executes a single ReAct reasoning cycle."""
    server = resolve_server_url()
    project_root = Path(__file__).resolve().parent
    directive = load_agents_directive(project_root)
    corpus = load_store_corpus()

    print(f"\n[REAC_LOOP] Active Server: {server}")
    print(f"[REAC_LOOP] User Query: {prompt}")

    # Inject corpus summary as context
    corpus_summary = "\n".join([f"- [{n['id']}] {n['name']}: {n['description']}" for n in corpus])
    system_prompt = f"{directive}\n\n### Available Store Knowledge Base:\n{corpus_summary}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Answer this question using the Store Knowledge Base:\n{prompt}"}
    ]

    print("[REAC_LOOP] Dispatching prompt to llama-server...")
    answer = query_chat(server, messages)
    print("\n=== AGENT RESPONSE ===")
    print(answer)
    print("======================\n")

    # Verify embeddings vector pipeline
    print("[EMBEDDINGS_VERIFY] Generating sample test vector from query...")
    vec = get_embedding(server, prompt)
    print(f"[EMBEDDINGS_VERIFY] Successfully generated vector of dimension: {len(vec)} (First 5 values: {vec[:5]})")


if __name__ == "__main__":
    test_query = sys.argv[1] if len(sys.argv) > 1 else "What is the function of the Critical Path Harness node and where are secrets kept?"
    run_react_agent(test_query)
