#!/usr/bin/env python3
"""
CRITICAL RAG // MODEL VAULT SCANNER & ARBITER (Interleaved from Ollama-Vanguard)
Discovers and classifies local GGUF models across local directories and Windows Host Model Vault.
Extracts family tags, quantization profiles, parameter counts, and recommended context budgets.
"""

import os
import sys
import glob
import re
from pathlib import Path
from typing import List, Dict, Any


def sanitize_model_tag(filepath: str) -> str:
    """Sanitize GGUF filename into canonical model identifier tag."""
    filename = os.path.basename(filepath)
    name = os.path.splitext(filename)[0].lower()
    parent_dir = os.path.basename(os.path.dirname(filepath)).lower()

    if "nemotron" in name or "nemotron" in parent_dir:
        m = re.search(r'(\d+b)', name)
        size = m.group(1) if m else "4b"
        return f"nemotron-3-nano-{size}"
    elif "qwen" in name or "qwen" in parent_dir:
        m = re.search(r'(\d+[\.\d]*b)', name)
        size = m.group(1) if m else "27b"
        return f"qwen-{size}"
    elif "phi" in name or "phi" in parent_dir:
        return "phi-3.5-mini"
    elif "gemma" in name or "gemma" in parent_dir:
        m = re.search(r'(\d+b)', name)
        size = m.group(1) if m else "12b"
        return f"gemma-4-{size}"
    elif "llama" in name or "llama" in parent_dir:
        m = re.search(r'(\d+[\.\d]*b)', name)
        size = m.group(1) if m else "3b"
        return f"llama-{size}"

    clean = re.sub(r'[\.\-_]?(q4_k_m|q4_0|q4_1|q5_k_m|q8_0|iq4_xs|iq\w+|gguf|instruct|chat|it|qat|i1)', '', name)
    clean = re.sub(r'[^a-z0-9_\-]+', '-', clean).strip('-')
    return clean or "custom-model"


def extract_quant_type(filename: str) -> str:
    """Extract quantization format string from filename."""
    m = re.search(r'(q\d+_[a-z0-9_]+|iq\d+_[a-z0-9_]+|q\d+_\d+)', filename.lower())
    return m.group(1).upper() if m else "UNKNOWN"


def scan_model_vault(search_paths: List[str] = None) -> List[Dict[str, Any]]:
    """Scans designated directory paths for GGUF model files."""
    if search_paths is None:
        search_paths = [
            "/opt/critical-rag/models",
            "/mnt/c/Users/Thrym/Desktop/LLM's",
            "/mnt/c/Users/Thrym/Desktop/Ollama-Vanguard/models"
        ]

    models = []
    seen_paths = set()

    for base in search_paths:
        if not os.path.exists(base):
            continue

        for root, _, files in os.walk(base):
            for file in files:
                if file.lower().endswith(".gguf"):
                    full_path = os.path.join(root, file)
                    if full_path in seen_paths:
                        continue
                    real = os.path.realpath(full_path)
                    if real in seen_paths:
                        continue
                    seen_paths.add(real)

                    size_bytes = os.path.getsize(full_path)
                    size_gb = round(size_bytes / (1024 ** 3), 2)
                    tag = sanitize_model_tag(full_path)
                    quant = extract_quant_type(file)

                    models.append({
                        "filename": file,
                        "path": full_path,
                        "tag": tag,
                        "quantization": quant,
                        "size_gb": size_gb,
                        "is_active_candidate": "nemotron" in tag.lower() or "qwen" in tag.lower()
                    })

    return models


def format_model_vault_report() -> str:
    """Formats an ASCII overview of available GGUF weights."""
    models = scan_model_vault()
    lines = [
        "======================================================================",
        "      CRITICAL RAG // MODEL VAULT REGISTRY (VANGUARD DISCOVERY)       ",
        "======================================================================",
        f"  Total Models Discovered: {len(models)} GGUF images",
        "----------------------------------------------------------------------"
    ]
    for m in models:
        active_mark = " [*]" if m["is_active_candidate"] else "    "
        lines.append(f"{active_mark} [{m['tag']:<22}] {m['quantization']:<10} {m['size_gb']:>5.2f} GB | {m['filename']}")
    lines.append("======================================================================")
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_model_vault_report())
