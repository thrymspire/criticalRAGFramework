# Transform & Inference Node Specification: `criticalpath-pipeline-v1.0`
**Document Version:** 1.0.0-PROD  
**Node Role:** The Transform & Inference Engine (DAG Scheduling, Embedding Extraction, Local Inference)  
**Distro RootFS:** Ubuntu 26.04.1 LTS  
**Compute Acceleration:** Direct Silicon Access (`/dev/dxg` via DirectX / WSLg)  
**Bound Interfaces:** `127.0.0.1:11434` (Ollama/vLLM), Inter-distro Loopback Client

---

## 1. Operational Boundary & Guarantees

- **STATELESS PROCESSING:** Does not retain permanent document or vector state. It reads raw sources from `/mnt/wsl/rag-store-data`, splits documents into hierarchical chunk trees, computes embeddings, and streams vector records down to `criticalpath-store-v1.0`.
- **SYSTEM STABILITY:** High token processing and embedding batching spikes are contained inside this node. When processing finishes, memory is reclaimed via WSL2 `autoMemoryReclaim=gradual` to prevent host Windows lockups.

---

## 2. Hierarchical Chunking DAG (Snakemake)

The ingestion pipeline is executed as a directed acyclic graph (DAG) via Snakemake:

```
[ Raw Documents ] (/mnt/wsl/rag-store-data/raw_documents/)
       |
       v
[ Rule: extract_text ] --> Normalizes PDFs, Markdown, HTML, JSON
       |
       v
[ Rule: parent_chunking ] --> Generates wide context windows (~1024 tokens)
       |
       v
[ Rule: child_chunking ]  --> Splits into granular search units (~256 tokens) with 32-token overlap
       |
       v
[ Rule: compute_embeddings ] --> Direct silicon inference (/dev/dxg) generating vectors
       |
       v
[ Rule: sync_to_store ] --> Pushes vectors to PostgreSQL 18 on 127.0.0.1:5432
```

---

## 3. Direct Silicon Access (`/dev/dxg`)

The pipeline leverages paravirtualized GPU access without needing bare-metal Nvidia drivers inside WSL:
- Verified via: `ls -la /dev/dxg`
- Vulkan / DirectML userspace drivers map compute jobs directly onto host GPUs (NVIDIA, AMD, or Intel).
- Supports local inference engines:
  - **Ollama:** `ollama serve` binding to `127.0.0.1:11434`
  - **llama-cpp-python / vLLM:** High throughput tensor parallel inference.

---

## 4. LangGraph / LangChain Runtime Node

The orchestration pipeline runs at `/opt/rag-pipeline/`:
- Coordinates query intake, reformulates questions with conversational context, issues vector similarity queries to `criticalpath-store-v1.0` (FastMCP / 8000 or Postgres / 5432), reranks results, and synthesizes answers using local LLM runtimes.
