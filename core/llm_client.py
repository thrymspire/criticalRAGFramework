"""
LLM Client with Real-Time Token Logprobs & Shannon Entropy
Connects to llama-server (Port 8080) with logprobs enabled,
calculates normalized Shannon entropy, and streams token-by-token schemas.
"""

import sys
import os
import json
import math
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, List, Generator, Optional


def calculate_entropy(top_candidates: List[Dict[str, Any]]) -> float:
    """
    Calculates normalized Shannon entropy in bits over candidate probabilities.
    q_i = p_i / sum(p_i)
    H = - sum(q_i * log2(q_i))
    """
    if not top_candidates:
        return 0.0

    raw_probs = [float(c.get("prob", 0.0)) for c in top_candidates if float(c.get("prob", 0.0)) > 0.0]
    total_mass = sum(raw_probs)
    if total_mass <= 0.0:
        return 0.0

    normalized = [p / total_mass for p in raw_probs]
    entropy = -sum(q * math.log2(q) for q in normalized if q > 0.0)
    return max(0.0, float(entropy))


def _get_stream_lines(server_url: str, payload: dict) -> Generator[str, None, None]:
    """
    Attempts direct HTTP streaming.
    Falls back to Windows curl.exe bridge if connection is refused across WSL2 NAT boundary.
    """
    endpoint = f"{server_url.rstrip('/')}/v1/chat/completions"
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data_bytes,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            for line in resp:
                decoded = line.decode("utf-8", errors="replace").strip()
                if decoded:
                    yield decoded
        return
    except Exception:
        # Cross-boundary fallback: execute Windows curl.exe
        win_curl = "/mnt/c/Windows/System32/curl.exe"
        if not os.path.exists(win_curl):
            win_curl = "curl.exe"

        cmd = [
            win_curl, "-s", "-N", "-X", "POST",
            endpoint,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for line in proc.stdout:
                line_str = line.strip()
                if line_str:
                    yield line_str
        finally:
            proc.terminate()


def stream_tokens_with_logprobs(
    prompt: str,
    server_url: str = "http://127.0.0.1:8080",
    max_tokens: int = 64,
    top_logprobs: int = 5,
    system_prompt: Optional[str] = None
) -> Generator[Dict[str, Any], None, None]:
    """
    Streams tokens from llama-server, converting each token step into the clean schema:
    {
      "step": 0,
      "chosen_token": "The",
      "logprob": -0.5270,
      "prob": 0.590,
      "entropy": 1.42,
      "top": [{"token": "The", "prob": 0.590}, ...],
      "status": "generating"
    }
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "stream": True,
        "logprobs": True,
        "top_logprobs": top_logprobs
    }

    step_index = 0

    for line in _get_stream_lines(server_url, payload):
        if line == "data: [DONE]":
            break
        if not line.startswith("data: "):
            continue

        chunk_str = line[6:].strip()
        if not chunk_str:
            continue

        try:
            chunk = json.loads(chunk_str)
        except json.JSONDecodeError:
            continue

        choices = chunk.get("choices", [])
        if not choices:
            continue

        choice = choices[0]
        finish_reason = choice.get("finish_reason")
        status = "finished" if finish_reason else "generating"

        logprobs_data = choice.get("logprobs")
        if not logprobs_data:
            continue

        content_list = logprobs_data.get("content", [])
        if not content_list:
            continue

        for token_info in content_list:
            chosen_token = token_info.get("token", "")
            raw_logprob = float(token_info.get("logprob", 0.0))
            chosen_prob = math.exp(raw_logprob)

            candidates = []
            for cand in token_info.get("top_logprobs", []):
                cand_token = cand.get("token", "")
                cand_logprob = float(cand.get("logprob", 0.0))
                cand_prob = math.exp(cand_logprob)
                candidates.append({
                    "token": cand_token,
                    "prob": round(cand_prob, 3)
                })

            # Calculate Shannon entropy across candidate distribution
            entropy_bits = calculate_entropy(candidates)

            step_obj = {
                "step": step_index,
                "chosen_token": chosen_token,
                "logprob": round(raw_logprob, 4),
                "prob": round(chosen_prob, 3),
                "entropy": round(entropy_bits, 2),
                "top": candidates,
                "status": status
            }

            yield step_obj
            step_index += 1
