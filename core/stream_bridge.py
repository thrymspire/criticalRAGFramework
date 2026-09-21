"""
Phase 2 — Real-Time Logprob Streaming Bridge
Receives streaming tokens from llama-server, calculates instantaneous Shannon entropy,
writes live telemetry to ui/state.json, and provides an SSE / Generator interface.
"""

import sys
import os
import json
import math
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Generator, Optional, Callable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_STATE_FILE = PROJECT_ROOT / "ui" / "state.json"


def calculate_entropy(top_candidates: List[Dict[str, Any]]) -> float:
    """Calculates normalized Shannon entropy in bits."""
    if not top_candidates:
        return 0.0
    raw_probs = [c["prob"] for c in top_candidates if c["prob"] > 0]
    total = sum(raw_probs)
    if total <= 0:
        return 0.0
    norm = [p / total for p in raw_probs]
    return max(0.0, -sum(p * math.log2(p) for p in norm if p > 0))


def _probe_direct_http(server_url: str) -> bool:
    """Fast probe whether server_url is directly reachable via HTTP within 150ms."""
    try:
        with urllib.request.urlopen(f"{server_url.rstrip('/')}/health", timeout=0.15) as r:
            return r.status == 200
    except Exception:
        return False


def stream_tokens_from_llama(
    prompt: str,
    server_url: str = "http://127.0.0.1:8080",
    max_tokens: int = 64,
    top_logprobs: int = 5,
    on_token: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Generator[Dict[str, Any], None, None]:
    """
    Connects to llama-server with stream=True and yields Phase 2 token schema objects.
    Also continuously updates ui/state.json with the latest token state.
    """
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "stream": True,
        "logprobs": True,
        "top_logprobs": top_logprobs
    }
    payload_json = json.dumps(payload)

    # Prepare stream request
    req = urllib.request.Request(
        f"{server_url}/v1/chat/completions",
        data=payload_json.encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "CriticalRAG-StreamingBridge"}
    )

    resp = None
    proc = None

    # Probe direct HTTP first to avoid hanging 30 seconds on WSL2 NAT boundary
    if _probe_direct_http(server_url):
        try:
            resp = urllib.request.urlopen(req, timeout=10)
        except Exception:
            resp = None

    if resp is None:
        # Cross-boundary fallback to Windows curl.exe bridge
        win_curl = "/mnt/c/Windows/System32/curl.exe"
        if not os.path.exists(win_curl):
            win_curl = "curl.exe" if os.name == "nt" else "curl"
        try:
            proc = subprocess.Popen(
                [win_curl, "-sN", "-X", "POST", f"{server_url.rstrip('/')}/v1/chat/completions",
                 "-H", "Content-Type: application/json", "-d", payload_json],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            resp = proc.stdout
        except Exception:
            resp = []

    step_idx = 0
    full_text = ""

    # Ensure ui directory exists
    UI_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    for line in resp:
        line_str = line.decode("utf-8") if isinstance(line, bytes) else line
        line_str = line_str.strip()

        if not line_str.startswith("data:"):
            continue

        data_body = line_str[5:].strip()
        if data_body == "[DONE]":
            break

        try:
            chunk = json.loads(data_body)
        except Exception:
            continue

        choices = chunk.get("choices", [])
        if not choices:
            continue

        choice = choices[0]
        delta = choice.get("delta", {})
        tok_text = delta.get("content") or delta.get("reasoning_content") or ""
        logprobs_block = choice.get("logprobs", {})
        content_items = logprobs_block.get("content", [])

        if not content_items:
            continue

        item = content_items[0]
        chosen_tok = item.get("token", tok_text)
        chosen_lp = item.get("logprob", 0.0)
        chosen_prob = math.exp(chosen_lp)

        # Build candidate top list
        raw_top = item.get("top_logprobs", [])
        top_list = []
        for c in raw_top:
            c_tok = c.get("token", "")
            c_lp = c.get("logprob", 0.0)
            top_list.append({"token": c_tok, "prob": math.exp(c_lp)})

        if not any(c["token"] == chosen_tok for c in top_list):
            top_list.append({"token": chosen_tok, "prob": chosen_prob})

        top_list.sort(key=lambda x: x["prob"], reverse=True)
        entropy = calculate_entropy(top_list)
        full_text += chosen_tok

        finish_reason = choice.get("finish_reason")
        status = "finished" if finish_reason else "generating"

        schema_obj = {
            "step": step_idx,
            "chosen_token": chosen_tok,
            "logprob": round(chosen_lp, 4),
            "prob": round(chosen_prob, 3),
            "entropy": round(entropy, 2),
            "top": [
                {"token": c["token"], "prob": round(c["prob"], 3)}
                for c in top_list[:top_logprobs]
            ],
            "running_text": full_text,
            "status": status
        }

        # Persist latest state to ui/state.json
        try:
            UI_STATE_FILE.write_text(json.dumps(schema_obj, indent=2), encoding="utf-8")
        except Exception:
            pass

        if on_token:
            on_token(schema_obj)

        yield schema_obj
        step_idx += 1

    if proc is not None:
        try:
            proc.terminate()
        except Exception:
            pass

    if step_idx == 0:
        err_msg = "[NOTICE: Inference engine at port 8080 did not return tokens. Verify that llama-server.exe is running on host.]"
        diagnostic_event = {
            "step": 1,
            "chosen_token": err_msg,
            "logprob": 0.0,
            "prob": 1.0,
            "entropy": 0.0,
            "top": [{"token": "[NOTICE]", "prob": 1.0}],
            "status": "complete",
            "running_text": err_msg
        }
        if on_token:
            on_token(diagnostic_event)
        yield diagnostic_event


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "What is the capital of France?"
    print(f"[*] Streaming logprobs for: {prompt}")
    for item in stream_tokens_from_llama(prompt, max_tokens=16):
        print(f"Step {item['step']:02d} | Token: {repr(item['chosen_token']):<12} | Prob: {item['prob']:.3f} | Entropy: {item['entropy']:.2f}")
