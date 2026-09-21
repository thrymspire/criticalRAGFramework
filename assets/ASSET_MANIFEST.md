# Critical RAG Asset Manifest & Infrastructure Inventory
**Version:** 1.0.0-PROD  
**Last Updated:** 2026-09-19  
**Security & Access Tier:** Local Isolated Architecture (WSL2 Multi-Distro Topology)  
**Host Substrate:** Windows 11 Enterprise (DirectX DXCore / WSLg enabled)

---

## 1. Executive Summary

This manifest registers and documents all architectural assets, running services, network bindings, storage mounts, and operational files comprising the **Critical Path RAG Architecture**. The infrastructure is segregated into three specialized, single-responsibility Ubuntu 26.04 LTS WSL2 distros interconnected strictly across host loopback (`127.0.0.1`):

1. **`criticalpath-store-v1.0`** — The State Anchor (Vector DB, WAL, FastMCP Bridge)
2. **`criticalpath-pipeline-v1.0`** — The Transform & Inference Node (Hierarchical Chunking DAG, LangGraph, Local Model Runtime, Direct Silicon GPU access)
3. **`criticalpath-eval-v1.0`** — The Verification Gate (Ephemeral Ragas / TruLens benchmark node)

---

## 2. Distro Asset Registry

| Distro Name | Role & Responsibility | RootFS Base | State Model | Default Ports / Sockets | Storage Allocations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`criticalpath-store-v1.0`** | State Anchor & Vector Proximity | Ubuntu 26.04 LTS Minimal | Persistent | `127.0.0.1:5432` (PostgreSQL)<br>`127.0.0.1:8000` (FastMCP) | Dedicated `/mnt/wsl/rag-store-data`<br>VHDX: `C:\WSL\distros\criticalpath-store-v1.0\ext4.vhdx` |
| **`criticalpath-pipeline-v1.0`** | Transform, Chunking DAG & Inference | Ubuntu 26.04 LTS Minimal | Stateless Compute | `127.0.0.1:11434` (Ollama/vLLM)<br>`/dev/dxg` (D3D12 GPU Silicon) | Working cache `/mnt/wsl/rag-store-data/pipeline_cache`<br>VHDX: `C:\WSL\distros\criticalpath-pipeline-v1.0\ext4.vhdx` |
| **`criticalpath-eval-v1.0`** | Verification & Metric Gate | Ubuntu 26.04 LTS Minimal | Ephemeral (On-Demand) | Client-only (Asynchronous queries into Pipeline/Store) | Benchmark output: `/opt/rag-eval/reports`<br>VHDX: `C:\WSL\distros\criticalpath-eval-v1.0\ext4.vhdx` |

---

## 3. Desktop Shortcuts & Operation Scripts Inventory

Located at `./shortcuts\`:

| Script / Shortcut | Type | Target Distro / Action | Description |
| :--- | :--- | :--- | :--- |
| **`start-rag-cluster.bat`** | Orchestration Batch | Store + Pipeline | Mounts `/mnt/wsl/rag-store-data`, boots Postgres 18 & FastMCP daemon, initializes pipeline node. |
| **`stop-rag-cluster.bat`** | Orchestration Batch | All Distros | Gracefully halts Postgres, shuts down eval gate, and issues `wsl --terminate` to flush memory. |
| **`status-rag-cluster.bat`** | Diagnostic Batch | System-wide | Verifies distro lifecycle status, tests TCP ports 5432 & 8000, inspects shared VHD mount. |
| **`run-eval-gate.bat`** | Execution Batch | Eval Distro | Boots `criticalpath-eval-v1.0`, runs RAG benchmark matrix, writes output JSON/CSV, auto-terminates. |
| **`open-store-shell.bat`** | Interactive Shell | `criticalpath-store-v1.0` | Direct bash console for database administration, WAL tuning, and pgvector index maintenance. |
| **`open-pipeline-shell.bat`**| Interactive Shell | `criticalpath-pipeline-v1.0`| Direct bash console for Snakemake pipeline triggers, LangGraph development, and Ollama tests. |
| **`open-eval-shell.bat`** | Interactive Shell | `criticalpath-eval-v1.0` | Direct bash console for metric calibration, synthetic query test adjustments, and report review. |

---

## 4. Configuration & Runtime Assets Inventory

Located at `./config\`:

- **`wslconfig.sample`**: Production host tuning file applied to `~/.wslconfig` (16GB RAM limit, 12 cores, `autoMemoryReclaim=gradual`, `sparseVhd=true`).
- **`postgresql-tuned.conf`**: High-performance vector search configuration for Postgres 18 (SSD WAL tuning, `shared_buffers`, `maintenance_work_mem` for HNSW/IVFFlat indexing).
- **`fastmcp-server.py`**: Lightweight asynchronous Python FastMCP protocol bridge exposing similarity search tools to LLM orchestrators over port 8000.
- **`snakemake_dag.smk`**: Declarative DAG defining hierarchical chunking rules (parent-child document hierarchy, token window overlaps, embedding generation).
- **`eval_runner.py`**: Standalone deterministic verification runner evaluating context recall, precision, and hallucination rates.

---

## 5. Schema & Governance Notice

Any addition, modification, or retirement of components in the Critical RAG ecosystem must comply with the update lifecycle documented in:  
`./assets\SCHEMA_AND_UPDATE_LIFECYCLE.md`.
