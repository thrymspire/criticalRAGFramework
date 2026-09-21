# Critical RAG Framework — Master Structural Architecture & Review Guide
<!-- Document ID: ARCH-CRITICAL-RAG-STRUCTURE-REVIEW-20260921-v1.0 -->
<!-- Target Root: .\ -->
<!-- Primary Authoritative Distro: harness-enclave:~/Critical-RAG/ on native ext4 -->

---

## 1. Executive Summary & Framework Scope

The **Critical RAG Framework** is an autonomous, sovereign local AI and retrieval infrastructure designed specifically for high-efficiency, zero-overhead reasoning on mobile AMD Zen 4 / RDNA 3 hardware (ASUS ROG Ally X, Ryzen Z1 Extreme, 24.0 GB LPDDR5X).

This archive represents the consolidated, formal master structure of the framework, drawn together from across the hypervisor micro-distributions and unified into a single coherent structural reference.

### Core Architectural Mandates
1. **Single Host Compute Exception:** Native Windows Vulkan `llama-server.exe` (Port 8080) for direct, zero-overhead GPU memory access and 269+ t/s prompt evaluation.
2. **100% Linux Userspace Execution:** All orchestration, hierarchical RAG retrieval, token physics calculations, agent hot-switching, and HTTP/SSE serving run inside WSL2 (`harness-enclave`) on native `ext4`.
3. **No Windows Compute Scripts:** Zero batch files, zero desktop turnkey scripts, zero background Python workers on the Windows host.
4. **Cloud Storage Exemption:** Absolute isolation from `OneDrive*` and `Google Drive*` to prevent hydration thrashing and reparse corruption.

---

## 2. Directory Layout & Component Inventory

```
criticalRAGFramework/
├── FRAMEWORK_STRUCTURE_REVIEW.md  # [This Document] Master Architectural Review & Scoping Guide
├── AGENTS.md                      # Complete 7-Agent Master Roster & Directive Specification
├── CRITICAL_RAG_TINKER_HOOK.md    # IDE & Autonomous Subagent Interleaving Hook
├── turnkey.sh                     # Master POSIX CLI Dispatcher (setup | start | stop | status | agent | run | eval | replicate)
├── requirements.txt               # Pinned Python Dependencies
├── docker-compose.yml             # Auxiliary Service Definitions (Store, Redis, Vector Nodes)
├── absorb_corpus.py               # Document & Section ETL Extraction & Canonical Chunk Ingestion
├── extract_logprobs.py            # Standalone Logprob & Normalized Shannon Entropy CLI Engine
├── react_loop.py                  # Core ReAct Grounded Reasoning Loop
├── run.py                         # Standalone Direct Agent CLI Entry Point
├── critical_rag_replication_bundle.tar.gz # Self-Contained Deployment Archive (329 KB)
│
├── core/                          # Shared Python Orchestration Subsystem
│   ├── __init__.py                # Package Exports
│   ├── agent_loader.py            # Frontmatter Markdown Parser & Mid-Session Hot-Switcher
│   ├── hardware_arbiter.py        # CPU Vector, Memory & Vulkan Tier Arbiter (Tier 2 Zen4 APU)
│   ├── harness.py                 # Multi-Turn Dialogue & ReAct Execution Engine
│   ├── hierarchical_retrieval.py  # 3-Tier Hierarchical RAG (Doc -> Section -> Chunk)
│   ├── llm_client.py              # SSE Token Streamer with Logprobs & Shannon Math
│   ├── model_scanner.py           # Multi-Path GGUF Model Vault Scanner & Quantization Profiler
│   ├── retrieval.py               # Unified Dense + BM25 + Reciprocal Rank Fusion Bridge
│   ├── secrets.py                 # Enclave Secrets Manager with Chmod-700 Memory Caching
│   ├── server.py                  # Sovereign HTTP & SSE Server on Port 8090
│   ├── stream_bridge.py           # Live Token Probability Bridge for Spokewheel Canvas
│   └── watermark_drift.py         # Vanguard CanaryAnchor Retention & Context Drift Engine
│
├── agents/                        # Autonomous Agent Directives (Markdown + Frontmatter)
│   ├── direct.md                  # Direct Mode: Clean LLM & RAG queries (No Agent Persona)
│   ├── general.md                 # General Framework Assistant: Inquiries, synthesis & Alien Artifacts
│   ├── engineer.md                # Primary Rocket Systems Engineer: Empirical diagnostics
│   ├── framework.md               # Meta-Engineer: Harness, Agent & Self-Audit protocol
│   ├── mechanic.md                # Hardware, VRAM & ROCm Specialist: gfx1103 diagnostics
│   ├── analyst.md                 # Deep RAG Research Analyst: Epistemological gap auditor
│   └── debug.md                   # Logprob Telemetry & Perplexity Uncertainty Debugger
│
├── ui/                            # Unified Single-Page Sovereign Web Cockpit
│   ├── index.html                 # Unified HTML5 Cockpit: Spokewheel, Drift Meter, Chat & Artifact Vessel
│   ├── circle.js                  # HTML5 Canvas Token Entropy Orbit & Probability Spokes
│   ├── chat_schema.json           # Formal JSON Schema for Multi-Turn Chat & SSE Stream Physics
│   ├── state.json                 # Active Agent & Instantaneous Token Physics State
│   ├── styles.css                 # Alien Void Design System Stylesheet
│   ├── logo.svg                   # Vanguard Formline Insignia
│   └── vanguard.html              # Dedicated Vanguard Telemetry Dashboard
│
├── turnkey/                       # Modular POSIX Control Plane Suite
│   ├── setup.sh                   # Automated First-Time / Post-Clone Bootstrap
│   ├── start.sh                   # Starts core.server on Port 8090 with Port & API Verification
│   ├── stop.sh                    # Gracefully Terminates Server & Frees Socket
│   ├── status.sh                  # Comprehensive Cluster Telemetry & Active Agent Inventory
│   ├── agent.sh                   # CLI Agent Inventory & Mid-Session Switcher
│   ├── run.sh                     # Direct One-Shot ReAct CLI Execution
│   ├── eval.sh                    # 7-Gate Hardware & Regression Verification Gate
│   └── replicate.sh               # System Bundler Creating Self-Contained Deployment Tarball
│
├── corpus/                        # Grounded Knowledgebase & Canonical Provenance Chunks
│   ├── canonical_chunks.json      # 348 Absorbed Chunks with Strict UUID & Parent Hierarchy
│   ├── corpus_seed.json           # Baseline System Documents & Architectural Specs
│   ├── critical_path_corpus_seed.json # Master Critical Path 4-Tier Topology Seed
│   └── vanguard_domain_specification.md # Vanguard Foundry Interleaved Ontology
│
├── assets/                        # Multi-Distro Node Specifications & Architecture Blueprints
│   ├── ARCHITECTURE_OVERVIEW.md   # Full Cross-Distro Hypervisor Topology Diagram
│   ├── ASSET_MANIFEST.md          # File & Asset Catalog
│   ├── STORE_NODE_SCHEMA.md       # Canonical Database & Schema Rules for Store Node
│   ├── PIPELINE_NODE_SPEC.md      # Data Extraction & Normalization Pipeline Spec
│   ├── EVAL_NODE_SPEC.md          # Scoring, Slack Calculation & Benchmark Spec
│   ├── SCHEMA_AND_UPDATE_LIFECYCLE.md # Chunk Evolution & Update Lifecycle
│   ├── SHORTCUTS_AND_OPS_GUIDE.md # Operator Keybindings & Quick Actions
│   └── logo.svg                   # Vector Brand Asset
│
├── distro_nodes/                  # Consolidated Cross-Distro Subsystem Enclaves
│   ├── criticalpath-store-v1.0/   # Store Node: Graph & Entity Persistence Core
│   │   ├── STORE_NODE_SCHEMA.md   # Detailed Store Node Architecture
│   │   └── corpus/critical_path_corpus_seed.json # Master 4-Phase Node Definitions
│   ├── criticalpath-harness-v1.0/ # Harness Node: Automated Benchmark & Secrets Enclave
│   │   └── HARNESS_NODE_SPEC.md   # Dedicated Enclave Execution Boundaries
│   ├── criticalpath-pipeline-v1.0/# Pipeline Node: Ingestion & DAG Normalization
│   │   └── PIPELINE_NODE_SPEC.md  # Transformation & Pipeline Specs
│   ├── criticalpath-eval-v1.0/    # Eval Node: Metric Verification & Scoring
│   │   └── EVAL_NODE_SPEC.md      # Evaluation Runner Architecture
│   └── comfyui/                   # Acceleration Node: ROCm 7.1 gfx1103 Daemon
│       └── COMFYUI_ACCELERATION_SPEC.md # Hardware Guardrails & Memory Allocation Spec
│
├── templates/                     # Standardized JSON Ingestion & Chunk Templates
│   ├── chunk_template.json        # Canonical Chunk Schema Template
│   ├── document_template.json     # Document Ingestion Template
│   └── query_template.json        # Unified Retrieval Query Payload Template
│
└── config/                        # Cluster Configuration Templates & Auxiliary Runners
    ├── eval_runner.py             # Evaluation Test Harness
    ├── fastmcp-server.py          # Model Context Protocol Endpoint
    ├── postgresql-tuned.conf      # Low-Memory Tuned Postgres Configuration
    ├── snakemake_dag.smk          # Pipeline Workflow Execution DAG
    └── wslconfig.sample           # Verified 16GB / 8GB Host WSL Configuration
```

---

## 3. Multi-Distro Hypervisor Architecture

The Critical Path cluster distributes workloads across 7 isolated WSL2 distributions:

```
+--------------------------------------------------------------------------------------------------+
|                                  WINDOWS 11 HOST (THRYMSTATION)                                  |
|                                                                                                  |
|  +------------------------------------+        +----------------------------------------------+  |
|  |   llama-server.exe (Port 8080)     |        |          Centralized Model Vault             |  |
|  |   AMD Vulkan (Radeon 780M iGPU)    | <====> |          models\       |  |
|  |   269.23 t/s PP512 | Context 8192  | (mmap) |          (25.5 GB GGUF NVMe Vault)           |  |
|  +------------------------------------+        +----------------------------------------------+  |
|                   ^                                                                              |
|                   | Internal Hypervisor Virtual Network Bridge                                   |
|                   v                                                                              |
|  +--------------------------------------------------------------------------------------------+  |
|  |                                  WSL2 HYPERVISOR BOUNDARY                                  |  |
|  |                                                                                            |  |
|  |  +-----------------------------------+        +-----------------------------------------+  |  |
|  |  |      harness-enclave (Ubuntu 26.04)      |        |        comfyui (Ubuntu Minimal)         |  |  |
|  |  |  * Authoritative Code Source      |        |  * ROCm 7.1 + TheRock PyTorch Nightly   |  |  |
|  |  |  * Port 8090 (Web Cockpit & SSE)  |        |  * Port 8188 (Image & Latent Diffusion) |  |  |
|  |  |  * Python 3.14 (.venvs/critical)  |        |  * --reserve-vram 2.0 Memory Guardrail  |  |  |
|  |  +-----------------------------------+        +-----------------------------------------+  |  |
|  |                   |                                                |                       |  |
|  |                   v                                                v                       |  |
|  |  +-----------------------------------+        +-----------------------------------------+  |  |
|  |  |   criticalpath-harness-v1.0       |        |        criticalpath-store-v1.0          |  |  |
|  |  |  * /workspace/project mount       |        |  * /data/corpus/ (Permanent Store)      |  |  |
|  |  |  * /etc/harness/secrets (700)     |        |  * /data/embeddings/ & /data/graphs/    |  |  |
|  |  +-----------------------------------+        +-----------------------------------------+  |  |
|  |                   |                                                |                       |  |
|  |                   v                                                v                       |  |
|  |  +-----------------------------------+        +-----------------------------------------+  |  |
|  |  |   criticalpath-pipeline-v1.0      |        |        criticalpath-eval-v1.0           |  |  |
|  |  |  * Data Ingestion & ETL           |        |  * Metric Verification & Scoring        |  |  |
|  |  |  * Topological DAG Normalization  |        |  * Regression Assertion Suite           |  |  |
|  |  +-----------------------------------+        +-----------------------------------------+  |  |
|  +--------------------------------------------------------------------------------------------+  |
+--------------------------------------------------------------------------------------------------+
```

---

## 4. 3-Tier Hierarchical RAG Architecture

Rather than performing expensive, brute-force chunk scans across the entire corpus, the retrieval pipeline utilizes a 3-tier hierarchy optimized for the 24 GB hardware envelope:

```
[User Query]
     │
     ▼
[Tier 1: Collection / Document Summaries] ──► Coarse semantic filtering (Identifies candidate documents)
     │
     ▼
[Tier 2: Section / Chapter Summaries]     ──► Mid-level routing (Isolates relevant contextual sections)
     │
     ▼
[Tier 3: Canonical Chunks (512 tokens)]  ──► Dense Vector (Cosine) + BM25 Sparse + Reciprocal Rank Fusion (RRF)
     │
     ▼
[Parent-Document Context Injection]       ──► Chunk text + surrounding section context injected into prompt
```

- **Canonical Chunk Identifier:** `CHK-<doc_id>-<uuid4>`
- **Parent Context Assembly:** Preserves paragraph flow and prevents context amputation.
- **Epistemological Gap Protocol:** If mean similarity is below threshold ($< 0.72$), the system explicitly declares `[EPISTEMOLOGICAL GAP]` rather than hallucinating answers.

---

## 5. Token Physics & Vanguard Telemetry Mathematics

Each streamed token is evaluated for uncertainty and drift in real time:

1. **Normalized Shannon Entropy ($H$ in bits):**
   $$q_i = \frac{p_i}{\sum_j p_j}, \quad H = - \sum_{i=1}^{k} q_i \log_2(q_i)$$
   - $H < 0.65\text{ b}$: High certainty / collapsed probability distribution (Cyan spoke).
   - $0.65 \le H \le 1.45\text{ b}$: Balanced reasoning / standard vocabulary branching (Purple spoke).
   - $H > 1.45\text{ b}$: High epistemic risk / ambiguous distribution (Red spoke).

2. **CanaryAnchor Watermark Retention ($R_{\text{watermark}}$):**
   $$R_{\text{watermark}} = \frac{|\mathcal{A}_k \cap \mathcal{G}_{\text{accumulated}}|}{|\mathcal{A}_k|}$$
   Measures whether salient semantic anchor tokens $\mathcal{A}_k$ from the prompt remain grounded in generated output.

3. **Context Drift Equation ($\Delta_{\text{drift}}$):**
   $$\Delta_{\text{drift}} = \max\left(0, \, (1 - R_{\text{watermark}}) \times 100 - \frac{|\mathcal{G}_{\text{accumulated}}|}{C_{\text{budget}}} \times 10\right)$$
   Classified across four operational tiers:
   - `ANCHOR LOCKED (100% Fidelity)`
   - `NOMINAL STABLE (72–88% Fidelity)`
   - `ATTENTION DILUTION (50–71% Fidelity)`
   - `CRITICAL DRIFT (<50% Fidelity)`

---

## 6. Unified Single-Page Sovereign Web Cockpit (`http://localhost:8090`)

All operator interactions are consolidated onto **one single live dashboard**:

- **Spokewheel Orbit Canvas (`circle.js`):** Visualizes the probability distribution of the top-5 candidate tokens as glowing radial spokes rotating along an entropy orbit.
- **CanaryAnchor Drift Meter:** Animated progress capsule tracking watermark preservation and context saturation against the 8192 token context budget.
- **Top Header Mode Switcher:**
  - `⚡ ReAct RAG`: One-shot directive execution with structured grounded chunk inspection.
  - `💬 General Chat`: Interactive multi-turn conversational dialogue.
  - `📊 Token Physics`: Direct token probability probe with top-5 candidate distribution table.
  - `📝 Direct Wrap`: Immediate Markdown-to-Alien Artifact compilation.
- **General Chat Deck (`#chatDeck`):**
  - Continuous dialogue transcript with operator bubbles and active agent bubbles.
  - `[x] 3-Tier RAG Grounding`: Toggles grounding against canonical chunks or parametric LLM.
  - `[x] ⚡ Direct Mode (No Persona)`: Toggles clean, persona-free Q&A.
  - `[ 🛑 Clear Thinking / Abort ]`: **Emergency stream abort toggle** that instantly cancels hanging SSE streams, removes stalled typing cursors, unlocks the input bar, and refreshes state without reloading the page.
  - `[ 🧬 Compile Turn to Alien Artifact ]`: One-click button on each assistant turn to load the conversation into the vessel deck below.
- **Live Alien Artifact Vessel Deck:** Full preview featuring cut-corner glassmorphic panels (`clip-path`), interactive circular checkpods, dark code blocks with copy buttons, and instant export to `./artifacts/`.

---

## 7. Active Sovereign Agent Roster

| Agent | File | Temp | Top-Logprobs | Max Tokens | Role & Operational Focus |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`direct`** | `agents/direct.md` | `0.30` | `5` | `1024` | **Direct Query (No Persona):** Clean, raw LLM & RAG query mode without agent persona or roleplay framing. |
| **`general`** | `agents/general.md` | `0.50` | `5` | `1024` | **General Framework Assistant:** User inquiry companion, multi-document synthesis, and Alien Artifact generation. |
| **`engineer`** | `agents/engineer.md` | `0.65` | `5` | `1024` | **Chief Rocket & Systems Engineer:** Mechanical/compute failure diagnostics and empirical evidence validation. |
| **`framework`** | `agents/framework.md` | `0.40` | `5` | `1536` | **Meta-Engineer & Auditor:** Tri-part auditor (Harness Audit, Agent Audit, Self-Audit) reporting findings by severity. |
| **`mechanic`** | `agents/mechanic.md` | `0.10` | `5` | `1024` | **Hardware & ROCm Specialist:** Low-level `/dev/dxg` bridges, Radeon 780M `gfx1103`, and `--reserve-vram 2.0` guardrails. |
| **`analyst`** | `agents/analyst.md` | `0.30` | `5` | `1024` | **Corpus Synthesis & Ontology Analyst:** Multi-document research, epistemological gap audits, and strict citations. |
| **`debug`** | `agents/debug.md` | `0.05` | `5` | `1024` | **Logprob Telemetry & Perplexity Debugger:** Traces token probability mass, entropy spikes, and epistemic uncertainty. |

---

## 8. Operational Verification & Turnkey Control Commands

All framework operations are managed inside `harness-enclave` on Linux ext4:

```bash
# 1. Connect to authoritative development distro
wsl -d harness-enclave

# 2. Navigate to project root
cd ~/Critical-RAG

# 3. Automated cluster setup & dependency bootstrap
./turnkey.sh setup

# 4. Comprehensive cluster health inspection
./turnkey.sh status

# 5. Hot-switch active runtime agent
./turnkey.sh agent              # Lists available agents
./turnkey.sh agent direct       # Switches to Direct Query Mode (No Persona)
./turnkey.sh agent general      # Switches to General Framework Assistant
./turnkey.sh agent framework    # Switches to Meta-Auditor Engineer
./turnkey.sh agent engineer     # Switches to Rocket Systems Engineer

# 6. Manage background streaming server (Port 8090)
./turnkey.sh start              # Launches server & probes health
./turnkey.sh stop               # Gracefully terminates server & frees port 8090

# 7. Execute automated 7-gate regression & hardware verification
./turnkey.sh eval

# 8. Package portable standalone replication bundle
./turnkey.sh replicate
```

---

*Formally Consolidated & Accredited by Antigravity Autonomous Systems Agent.*
