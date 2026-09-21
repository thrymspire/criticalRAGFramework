# Critical RAG Operational Directives & Retrieval Contract
<!-- Target: .antigravity/rules.md -->
<!-- Scope: Base Universal Project Scope (Persists across all slash handlers, agent workflows, and subagents) -->

## Executive Principle
This workspace operates under the **Critical RAG Sovereign Protocol**. All generative output, analytical conclusions, code implementations, and planning workflows must be strictly grounded in verified retrieval context. Hallucination, ungrounded extrapolation, and undocumented assumptions are treated as catastrophic system failures.

---

## 1. Verification & Grounding Contract

### 1.1 Strict Retrieval Provenance
- **Zero-Unattributed-Assertions Policy:** Every factual claim, schema definition, metric, code configuration, or architectural constraint presented by an agent must cite one or more retrieved chunks from the corpus.
- **Direct Synthesizing Constraint:** If a statement combines insights from multiple chunks, each contributing chunk must be explicitly referenced at the sentence or clause level.
- **World Knowledge Boundary:** Pretrained parametric knowledge may only be used to facilitate language syntax, code formatting, and grammatical parsing. It must never override or supply factual data absent from retrieved corpus chunks.

### 1.2 Epistemological Gap Protocol
- **Retrieval Failure Handling:** If a retrieval query yields zero results above the similarity threshold, or if retrieved chunks do not contain sufficient evidence to answer the user request, the agent **MUST NOT** speculate, interpolate, or fabricate an answer.
- **Explicit Gap Declaration:** When context is insufficient, conflicting, or missing, the agent must output a structured `[EPISTEMOLOGICAL GAP]` declaration:
  ```markdown
  > [!WARNING] Epistemological Gap Declared
  > **Query Domain:** <topic / query description>
  > **Deficiency:** <why retrieved context is inadequate or contradictory>
  > **Missing Evidence:** <exact facts or documents needed to ground this inquiry>
  > **Action Taken:** Halting ungrounded synthesis; requesting corpus ingestion or clarification.
  ```
- **Conflicting Evidence Resolution:** If retrieved chunks present contradictory facts, the agent must present the conflict transparently with chunk attributions and refuse to unilaterally resolve the conflict without human corroboration.

---

## 2. Chunking, Ingestion & Embedding Architecture

### 2.1 Deterministic Ingestion Parameters
- **Target Chunk Size:** 512 tokens (or 1,800 characters) nominal size for narrative/prose documents; 256 tokens for dense technical specs.
- **Boundary Overlap:** Exactly 64 tokens (12.5% overlap) to prevent context fragmentation across chunk splits.
- **Deterministic Tokenizer:** Ingestion pipelines must utilize the exact tokenizer matching the active embedding model (`NVIDIA-Nemotron3-Nano` / `nomic-bert` tokenizer).

### 2.2 Canonical Metadata Schema
Every chunk ingested into the `criticalpath-store-v1.0` or local corpus must adhere to this mandatory JSON schema:
```json
{
  "chunk_id": "CHK-<DOC_ID>-<CHUNK_INDEX:04d>",
  "document_id": "DOC-<SOURCE_NAME_HASH>",
  "source_uri": "file:///path/to/source.ext",
  "ingested_at": "YYYY-MM-DDTHH:MM:SSZ",
  "chunk_index": 0,
  "total_chunks": 1,
  "hierarchy": {
    "h1": "Document Title",
    "h2": "Section Heading",
    "h3": "Subsection Heading"
  },
  "token_count": 512,
  "char_count": 1800,
  "content": "Raw chunk text content..."
}
```

### 2.3 Semantic Boundary Preservation
- **Header & Section Boundary Rule:** Chunk splits must align with structural Markdown headers (`#`, `##`, `###`), horizontal rules (`---`), or section dividers. Splitting mid-section across a header is strictly prohibited.
- **Logical Code Block Integrity:** Fenced code blocks (```lang ... ```), JSON records, XML schemas, and Python classes/functions must never be split across chunk boundaries. If a code block exceeds 512 tokens, it must be stored as an atomic entity with windowed sub-indexing or semantic class/function level chunking.
- **Table Integrity:** Markdown tables must be ingested intact. If a table exceeds max chunk size, header rows must be repeated at the start of each split table chunk.

---

## 3. Retrieval Strategy & Scoring Protocol

### 3.1 Hybrid Retrieval Architecture
All retrieval passes against the Critical RAG store must execute a dual-stage hybrid retrieval strategy:
1. **Dense Vector Retrieval (Weight: 0.70):**
   - Computed using `llama-server` `/v1/embeddings` with mean pooling.
   - Measures semantic alignment and latent conceptual similarity.
2. **Sparse Lexical Retrieval (Weight: 0.30):**
   - Computed via BM25 (or exact token inverted index).
   - Guarantees exact matches for symbol names, function signatures, identifiers, and hardware register codes.

### 3.2 Reciprocal Rank Fusion (RRF) & Reranking
- Results from Dense and Sparse passes must be fused using Reciprocal Rank Fusion (RRF) with constant $k = 60$:
  $$RRF\_Score(d) = \frac{0.70}{60 + r_{dense}(d)} + \frac{0.30}{60 + r_{sparse}(d)}$$
- Where available, candidate top-$N$ chunks ($N=15$) are passed to a cross-encoder reranker to yield final top-$K$ chunks ($K=3\text{ to }5$).

### 3.3 Strict Similarity Thresholds & Noise Elimination
- **Cosine Floor:** Chunks with raw cosine similarity $< 0.72$ must be dropped unconditionally before context assembly.
- **Noise Budget:** Never pack more than 5 chunks into the context window unless the user explicitly requests an exhaustive multi-document synthesis.
- **Deduplication:** Chunks with cosine overlap $> 0.95$ against an already-selected chunk must be suppressed to maximize context diversity.

---

## 4. Output Formatting & Citation Protocol

### 4.1 In-Text Citation Syntax
- Every factual proposition, technical parameter, or quoted claim must end with a bracketed chunk anchor referencing the canonical `chunk_id`:
  ```markdown
  The Radeon 780M utilizes 12 RDNA 3 compute units operating with Vulkan wave matrix acceleration [CHK-HW-0012].
  ```
- If multiple chunks support a claim, group citations in ascending index: `[CHK-HW-0012, CHK-HW-0015]`.
- Free-floating, uncited technical statements are rejected.

### 4.2 Mandatory Verification Summary Block
Every response generated by an agent or handler in this workspace **MUST conclude** with a standardized verification block:

```markdown
---

### Verification Summary
- **Retrieval Confidence:** [ HIGH (>=0.85) | MODERATE (0.72-0.84) | INSUFFICIENT (<0.72) ]
- **Corpus Coverage:** <Percentage of response points directly attributed to chunks, e.g., 100%>
- **Chunks Cited:**
  - `[CHK-ID-1]` - *<Document Title / Section Header>* (Score: 0.89)
  - `[CHK-ID-2]` - *<Document Title / Section Header>* (Score: 0.81)
- **Epistemological Disclosures:** <None, or description of any ungrounded query aspects omitted>
```

---

## 5. Incoming Dataset Intake & Staging Protocol (Ready for New Datasets)

When you import new datasets into the Critical RAG system:

### 5.1 Dropzone Locations
1. **Primary Production Storage Node:**
   - WSL2 Distro: `criticalpath-store-v1.0`
   - Path: `/data/corpus/`
   - Purpose: Permanent, isolated ext4 repository for production corpus files.
2. **Local Working Staging Directory:**
   - Linux Source of Truth: `harness-enclave:/opt/critical-rag/corpus/`
   - Windows Host Mirror: `./corpus\`
   - Baseline Seed Document: `corpus_seed.json` (must be preserved, never overwritten).

### 5.2 Accepted Formats & Intake Standards
- **Structured:** `.json`, `.jsonl` (with `id`, `title`, `content`, `metadata` fields).
- **Unstructured:** `.md`, `.txt`, `.csv`, PDF text extracts.
- **Non-Destructive Ingestion:** New datasets must be appended or ingested into dedicated subfolders or separate JSON files; never clobber existing baseline seed data.
- **Automatic Vectorization:** Upon arrival, files placed into `/data/corpus/` or `Critical-RAG/corpus/` are parsed by `core.retrieval.CorpusRetriever`, generating vector embeddings via `http://127.0.0.1:8080/v1/embeddings` (`--pooling mean`).

---

## 6. Hardware, Topology & Runtime Invariants

1. **Strict Windows Execution Boundary (Absolute User Mandate):**
   - **EXCLUSION:** The **ONLY** process permitted to execute on the Windows host is `llama-server.exe` (native Vulkan, port 8080) for direct GPU/VRAM hardware access.
   - **MANDATE:** **EVERYTHING ELSE MUST RUN EXCLUSIVELY INSIDE `harness-enclave` (ext4)**:
     - Python runtime (`/opt/venvs/critical-rag/bin/python3`)
     - Streaming HTTP/SSE server on port 8090 (`core.server`)
     - Harness orchestrator (`core.harness`)
     - Agent scripts and CLI entry points (`run.py`)
     - Corpus retrievers, embeddings, and vectorizers
     - Node/frontend tooling
   - **Zero Toleration:** Zero Python processes, workers, or servers may execute directly on the Windows host.
2. **Code Source of Truth:** `harness-enclave:/opt/critical-rag/` on native Linux `ext4`. All virtual environments (`~/.venvs/critical-rag`), Python runtime writes, and git operations execute here to guarantee zero 9P/DrvFs write bottlenecks.
3. **Cross-Distro Shared Enclave:** `/mnt/wsl/Critical-RAG/` is shared across all WSL2 distros (`criticalpath-harness-v1.0`, etc.) at native ext4 speeds.
4. **Windows Mirroring:** `./` mirrors `harness-enclave` via `sync-mirror.bat` for visual host inspection only.
5. **Model Vault Invariant:** `models\` remains physically on the Windows NVMe SSD to allow direct `mmap` at >5,000 MB/s for host Vulkan `llama-server.exe`. It is symlinked into `harness-enclave:~/models`.
6. **Inference Engine:** Native Windows Host Vulkan `llama-server.exe` on port `8080` (with `--embedding --pooling mean`). Zero Docker container overhead.
7. **ComfyUI Compute Guardrail:** Enforces `--reserve-vram 2.0` on port `8188` to protect the Windows display compositor from `0x3B` driver bugchecks.
8. **Secrets Vault Enclave:** Sandboxed in `criticalpath-harness-v1.0:/etc/harness/secrets/` with permissions `700`.

---

## 7. Real-Time Token Physics & Entropy Calibrations (Phases 1–4)

1. **Streaming Bridge Endpoint:** `http://localhost:8090` serves the Alien UI and real-time SSE stream (`/api/agent/stream` and `/api/tokens/stream`).
2. **Live Telemetry Schema:**
   - Emits `step`, `chosen_token`, `prob`, `entropy` (bits), and `top` candidate distributions.
   - Continuously writes current state to `ui/state.json`.
3. **Calibrated Shannon Entropy ($H$) Action Thresholds:**
   - **$H < 0.60$ bits:** Grounded Certainty. Ring displays tight bioluminescent cyan (`#5ffbf1`).
   - **$0.60 \le H \le 1.40$ bits:** Balanced Synthesis. Ring displays transitional purple (`#c084fc`).
   - **$H > 1.65$ bits:** Ambiguity Alert. Ring expands and pulses coral warning (`#ff6b81`); automatically triggers the **Epistemological Gap Protocol** if sustained over factual assertions.

---

## 8. Strict Cloud Storage Protection (Hydration Guard)

NEVER traverse, scan, read, index, or search into cloud storage folders, specifically:
- `[Cloud Drives]*` (including personal OneDrive and university accounts)
- `[Cloud Drives]*` or virtual drive `G:\`
- Any directory containing cloud placeholder reparse points.

All corpus searches, greps, and ingestion scripts MUST strictly stay within `Critical RAG`, `/data/corpus/`, `Desktop`, or specific local project directories.
