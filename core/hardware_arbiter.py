#!/usr/bin/env python3
"""
CRITICAL RAG // HARDWARE RESOURCE ARBITER (Interleaved from Ollama-Vanguard)
Diagnoses host compute topology (RAM, CPU, SIMD, AVX-512, GPU/Vulkan node, WSL2),
dynamically calculates optimal inference tiers, thread allocations, and context budgets.
Zero external pip dependencies (Standard Library only).
"""

import os
import sys
import platform
import subprocess
import re
import json
import urllib.request
from pathlib import Path


def get_system_memory_gb():
    """Detect total and available physical RAM."""
    total_gb = 8.0
    avail_gb = 6.0

    if os.path.exists("/proc/meminfo"):
        try:
            mem = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        mem[parts[0].strip()] = parts[1].strip()
            if "MemTotal" in mem:
                kb = int(re.sub(r"[^\d]", "", mem["MemTotal"]))
                total_gb = round(kb / (1024 * 1024), 2)
            if "MemAvailable" in mem:
                kb = int(re.sub(r"[^\d]", "", mem["MemAvailable"]))
                avail_gb = round(kb / (1024 * 1024), 2)
            else:
                avail_gb = round(total_gb * 0.75, 2)
            return total_gb, avail_gb
        except Exception:
            pass

    return total_gb, avail_gb


def get_compute_topology():
    """Detect CPU architecture, core counts, SIMD extensions, and GPU availability."""
    arch = platform.machine().lower()
    threads = os.cpu_count() or 4
    features = []
    gpu_desc = "None (CPU Inference)"
    has_gpu = False

    if os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                content = f.read().lower()
                if "avx512" in content:
                    features.append("AVX-512")
                elif "avx2" in content:
                    features.append("AVX2")
                if "avx" in content and "AVX" not in features and "AVX2" not in features and "AVX-512" not in features:
                    features.append("AVX")
                if "asimd" in content or "neon" in content:
                    features.append("ARM-NEON")
                if "dotprod" in content:
                    features.append("DotProd")
                if "i8mm" in content:
                    features.append("I8MM")
                if "sve" in content:
                    features.append("SVE")
        except Exception:
            pass

    # Check for Host Vulkan Bridge (Port 8080)
    vulkan_active = False
    try:
        req = urllib.request.Request("http://127.0.0.1:8080/health")
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            if resp.status < 400:
                vulkan_active = True
                gpu_desc = "Native Vulkan llama-server (Port 8080)"
                has_gpu = True
    except Exception:
        # Check via host bridge curl
        try:
            res = subprocess.run(["/mnt/c/Windows/System32/curl.exe", "-s", "--max-time", "1", "http://127.0.0.1:8080/health"], capture_output=True, text=True)
            if res.returncode == 0:
                vulkan_active = True
                gpu_desc = "Native Vulkan llama-server (Port 8080 via Host Bridge)"
                has_gpu = True
        except Exception:
            pass

    # Check for ROCm APU via lspci
    if not has_gpu:
        try:
            res = subprocess.run(["lspci"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if any(k in line.lower() for k in ["vga", "3d", "display"]) and "amd" in line.lower():
                        gpu_desc = "AMD Radeon 780M / APU (Integrated)"
                        has_gpu = True
                        break
        except Exception:
            pass

    return {
        "arch": arch,
        "threads": threads,
        "features": features,
        "gpu_desc": gpu_desc,
        "has_gpu": has_gpu,
        "vulkan_active": vulkan_active
    }


def evaluate_tier(total_ram_gb, arch, has_gpu, vulkan_active):
    """
    Evaluates optimal hardware tier based on Vanguard Foundry specifications:
    - Tier 1: Mobile Edge / VM (< 8 GB RAM)
    - Tier 2: Compact & Handheld APU (8 - 18 GB RAM / Zen 4)
    - Tier 3: Workstation (18 - 36 GB RAM)
    - Tier 4: Enterprise Compute (> 36 GB RAM)
    """
    if total_ram_gb < 8.0 or arch in ("aarch64", "arm64"):
        tier = {
            "tier": 1,
            "tier_name": "Tier 1 // Mobile Edge & VM Enclave",
            "recommended_model": "llama-3.2-3b",
            "fallback_model": "phi-3.5-mini-3.8b",
            "context_window": 2048 if total_ram_gb < 6.0 else 4096,
            "est_throughput": "35-50 tok/s"
        }
    elif total_ram_gb <= 18.0:
        tier = {
            "tier": 2,
            "tier_name": "Tier 2 // Compact & Handheld APU (Zen 4 / RDNA3)",
            "recommended_model": "NVIDIA-Nemotron3-Nano-4B (or Qwen2.5-7B)",
            "fallback_model": "phi-3.5-mini-instruct-3.8b",
            "context_window": 8192 if total_ram_gb >= 11.0 else 4096,
            "est_throughput": "25-45 tok/s on Vulkan / AVX-512"
        }
    elif total_ram_gb <= 36.0:
        tier = {
            "tier": 3,
            "tier_name": "Tier 3 // High-Throughput Workstation",
            "recommended_model": "qwen2.5-14b",
            "fallback_model": "gemma-2-9b",
            "context_window": 8192,
            "est_throughput": "15-25 tok/s"
        }
    else:
        tier = {
            "tier": 4,
            "tier_name": "Tier 4 // Deep Compute Foundry",
            "recommended_model": "qwen2.5-32b",
            "fallback_model": "qwen2.5-14b",
            "context_window": 16384,
            "est_throughput": "8-14 tok/s"
        }

    tier["recommended_threads"] = min(os.cpu_count() or 4, 8)
    return tier


def probe_hardware():
    """Returns complete hardware arbitration dictionary."""
    total_ram, avail_ram = get_system_memory_gb()
    compute = get_compute_topology()
    tier = evaluate_tier(total_ram, compute["arch"], compute["has_gpu"], compute["vulkan_active"])

    return {
        "system_memory": {
            "total_gb": total_ram,
            "available_gb": avail_ram
        },
        "compute": compute,
        "arbitrated_tier": tier
    }


def format_hardware_report():
    """Generates ASCII telemetry report for CLI and agents."""
    data = probe_hardware()
    mem = data["system_memory"]
    comp = data["compute"]
    tier = data["arbitrated_tier"]

    lines = [
        "======================================================================",
        "     CRITICAL RAG // HARDWARE RESOURCE ARBITER (VANGUARD INTERLEAVED)  ",
        "======================================================================",
        f"  * Architecture:      {comp['arch']} ({comp['threads']} logical cores)",
        f"  * SIMD Extensions:   {', '.join(comp['features']) if comp['features'] else 'Standard SSE'}",
        f"  * System Memory:     {mem['total_gb']} GB Total ({mem['available_gb']} GB Available)",
        f"  * Graphics Engine:   {comp['gpu_desc']}",
        f"  * Host Vulkan Node:  {'ONLINE (Port 8080)' if comp['vulkan_active'] else 'OFFLINE / STANDBY'}",
        "----------------------------------------------------------------------",
        f"  * Matched Tier:      {tier['tier_name']}",
        f"  * Target Model:      {tier['recommended_model']}",
        f"  * Context Budget:    {tier['context_window']} tokens",
        f"  * Target Threads:    {tier['recommended_threads']} threads",
        f"  * Expected Latency:  {tier['est_throughput']}",
        "======================================================================"
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_hardware_report())
