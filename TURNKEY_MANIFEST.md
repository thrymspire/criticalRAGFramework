# Sovereign Isolated Environment Turnkey Manifest
<!-- Target: ./docs/TURNKEY_MANIFEST.md -->
<!-- Scope: Isolated Linux ext4 Turnkey Architecture (harness-enclave / criticalpath-harness) -->

- [x] Architecture Paradigm: **100% Isolated Environment Turnkey**
- [x] Host OS (Windows) Footprint: **Zero compute services, zero turnkey scripts, zero batch files, zero shortcuts**
- [x] Exclusive Host Exception: Native Vulkan `llama-server.exe` (Port 8080) for direct GPU memory access
- [x] Isolated Execution Boundary: `harness-enclave:/opt/critical-rag/` on native Linux `ext4`
- [x] Secondary Enclave Boundary: `criticalpath-harness-v1.0:/workspace/project/`
- [x] Turnkey Entry Point: `~/Critical-RAG/turnkey.sh`
- [x] Subsystem CLI Suite: `~/Critical-RAG/turnkey/*.sh` (POSIX compliant, executable)
- [x] System Replication Engine: `turnkey/replicate.sh` & `turnkey/setup.sh`

---

## 1. Architectural Philosophy: Absolute Isolation & Reproducibility

All previous Windows `.bat` launchers, `.lnk` shell shortcuts, and Desktop-based orchestration scripts have been completely eliminated. The Windows host acts strictly as a hardware bridge (hosting Vulkan GPU inference on Port 8080 and NVMe GGUF model files) and a passive visual mirror.

All orchestration, testing, streaming, hierarchical retrieval, agent hot-switching, evaluation, and system replication occur strictly within the isolated Linux userspace (`harness-enclave`), protected by native ext4 file permissions and virtualenv sandboxing.

---

## 2. Directory Layout & Isolated Turnkey Suite

```
harness-enclave:~/Critical-RAG/
├── turnkey.sh                 # Master CLI dispatcher (setup | start | stop | status | agent | run | eval | replicate)
├── turnkey/
│   ├── setup.sh              # One-command automated bootstrap (venv, deps, index, cluster health)
│   ├── replicate.sh          # System bundler creating portable deployment archive (.tar.gz)
│   ├── start.sh              # Launches core.server (Port 8090), probes health & logs
│   ├── stop.sh               # Gracefully terminates server, frees port 8090
│   ├── status.sh             # Live cluster telemetry, port checks, active agent inspection
│   ├── agent.sh              # CLI agent inventory and mid-session hot-switcher
│   ├── run.sh                # Direct one-shot ReAct agent CLI executor
│   └── eval.sh               # Verification test suite & hardware audit gate
├── agents/                   # Switchable markdown agent directives
│   ├── engineer.md           # Systems Architecture & Structural Engineering
│   ├── framework.md          # Sovereign Agent & Framework Self-Auditing
│   ├── mechanic.md           # Hardware, VRAM & Driver Diagnostics
│   ├── analyst.md            # Corpus Synthesis & Epistemological Audit
│   └── debug.md              # Logprob Telemetry & Perplexity Debugger
├── core/                     # Shared orchestration engine
│   ├── server.py             # HTTP & SSE bridge (Port 8090)
│   ├── harness.py            # ReAct agent loop & token physics
│   ├── stream_bridge.py      # Real-time token streaming & Shannon entropy
│   ├── hierarchical_retrieval.py # 3-tier Hierarchical RAG (Doc -> Section -> Chunk)
│   ├── retrieval.py          # Unified retriever bridge
│   ├── llm_client.py         # Streaming client with logprobs & entropy extraction
│   └── agent_loader.py       # Frontmatter parser & state keeper
├── corpus/                   # Canonical data store
│   └── canonical_chunks.json # 406 absorbed chunks with strict UUID provenance
├── ui/                       # Cockpit frontend
│   ├── index.html            # Alien UI with agent selector & mode pill switcher
│   ├── circle.js             # Canvas entropy orbit & probability spokes
│   └── state.json            # Active agent & token physics state
├── requirements.txt          # Frozen cluster dependencies
├── critical_rag_replication_bundle.tar.gz # Latest self-contained deployment bundle
└── corpus_seed.json          # Immutable baseline provenance documents
```

---

## 3. Operational Commands (Inside Isolated Environment)

All commands are executed inside `harness-enclave`:

```bash
# Enter the isolated environment
wsl -d harness-enclave

# Navigate to project
cd ~/Critical-RAG

# Automated setup & verification (first-time or post-clone)
./turnkey.sh setup

# Inspect complete cluster telemetry & agent state
./turnkey.sh status

# Inspect or hot-switch the active agent
./turnkey.sh agent              # Lists available agents
./turnkey.sh agent framework    # Hot-switches to Framework Self-Auditor
./turnkey.sh agent engineer     # Hot-switches to Systems Engineer
./turnkey.sh agent mechanic     # Hot-switches to Hardware/VRAM Mechanic
./turnkey.sh agent analyst      # Hot-switches to Corpus Research Analyst
./turnkey.sh agent debug        # Hot-switches to Logprob Debugger

# Launch the streaming server in the background
./turnkey.sh start

# Stop the streaming server and free port 8090
./turnkey.sh stop

# Execute a one-shot agent reasoning turn
./turnkey.sh run --agent framework --prompt "Verify the canonical chunk schema compliance."

# Run the complete hardware verification & entropy gate
./turnkey.sh eval

# Package the entire deployment into a portable replication tarball
./turnkey.sh replicate
```

---

## 4. Hardware & Storage Topology Matrix

| Layer | Environment | Role | Storage Path | Protocol / Port |
| :--- | :--- | :--- | :--- | :--- |
| **GPU Inference** | Windows Host | Native Vulkan `llama-server.exe` | `C:\Workspace\Desktop\llama-vulkan\` | HTTP `127.0.0.1:8080` |
| **Model Vault** | Windows Host (NVMe) | Direct mmap weight storage | `models\` | Physical NVMe (>5 GB/s) |
| **Turnkey & Harness** | **`harness-enclave` (WSL2)** | **Complete runtime, API & Turnkey** | **`/opt/critical-rag/`** | **HTTP `127.0.0.1:8090`** |
| **Python Virtualenv** | **`harness-enclave` (WSL2)** | **Python 3.14.4 execution** | **`/opt/venvs/critical-rag`** | Isolated ext4 |
| **Corpus Primary Store**| `criticalpath-store-v1.0` | Production documents & ontology | `/data/corpus/` | ext4 Virtual Disk |
| **Auxiliary Containers**| `docker-engine` | Microservices & database sandboxes | TCP Socket | TCP `2375` |
| **Display Protection** | `comfyui` | ROCm compute with VRAM safety | User space | Port `8188` (`--reserve-vram 2.0`) |

---

## 5. Security & Isolation Invariants

1. **Zero Windows Compute Invariant:** No Python workers, scripts, or orchestrators run in the Windows host OS.
2. **Zero Windows Turnkey Invariant:** No `.bat`, `.lnk`, or Windows shortcut files exist in the project or desktop.
3. **Cloud Storage Protection:** Absolute prohibition against accessing `OneDrive*` or `Google Drive*`.
4. **Hardware Stability Guardrail:** ComfyUI enforces `--reserve-vram 2.0` on Port 8188 to prevent AMD display driver bugchecks (`0x3B`).
5. **State Preservation:** State writes (`ui/state.json`) execute at native ext4 speed with zero 9P/DrvFs write delays.

---

## 6. System Replication & Redeployment Playbook (Zero-Friction Bootstrap)

To redeploy or replicate the entire Critical RAG system onto a fresh host, WSL2 instance, or isolated container:

### Step 1: Package the System (Source Environment)
From inside `harness-enclave:~/Critical-RAG/`:
```bash
./turnkey.sh replicate
```
This generates `critical_rag_replication_bundle.tar.gz` containing all code, agents, UI assets, canonical corpus (`canonical_chunks.json`), configurations, and turnkey management tools (excluding virtual environments, caches, and raw weights).

### Step 2: Unpack onto Destination Environment
On the target machine:
```bash
# Create project destination
mkdir -p ~/Critical-RAG
cd ~/Critical-RAG

# Extract replication bundle
tar -xzf /path/to/critical_rag_replication_bundle.tar.gz -C ~/Critical-RAG
```

### Step 3: Run One-Command Automated Setup
```bash
./turnkey.sh setup
```
The automated setup script:
1. Detects existing Python virtual environment or bootstraps a clean one (`.venv`).
2. Installs and pins all required dependencies from `requirements.txt`.
3. Verifies POSIX execution permissions on all scripts in `turnkey/*.sh`.
4. Probes cluster connectivity (native port 8080 and host-bridge fallback).
5. Pre-indexes the Hierarchical RAG corpus across 3 tiers (Docs, Sections, Chunks).

### Step 4: Validate Cluster & Launch Cockpit
```bash
# Verify health
./turnkey.sh status

# Launch streaming server on Port 8090
./turnkey.sh start

# Open Cockpit UI in browser
# http://localhost:8090
```

---

## 7. Vanguard Foundry Interleaved Capabilities & Live Test Accreditation

The Critical RAG Sovereign Harness has officially absorbed and interleaved all unique capabilities from the **Vanguard Foundry** project:

1. **Hardware Resource Arbiter (`core/hardware_arbiter.py`)**:
   - Dynamic AVX-512 vector detection, 12-core Zen 4 profiling, 11.68 GB physical memory verification, and host Vulkan Port 8080 arbitration.
   - Dynamic tier mapping to **Tier 2 (Compact & Handheld APU)** with 8192 token context budget.
2. **Context Drift & Watermark Telemetry (`core/watermark_drift.py`)**:
   - CanaryAnchor extraction $\mathcal{A}_k$ from user directives.
   - Real-time watermark retention ($R_{\text{watermark}}$) and context drift equation ($\Delta_{\text{drift}}$).
   - Four-tier classification: `ANCHOR LOCKED`, `NOMINAL STABLE`, `ATTENTION DILUTION`, `CRITICAL DRIFT`.
3. **Model Vault Scanner (`core/model_scanner.py`)**:
   - Multi-path GGUF discovery across WSL ext4 and Windows Host NVMe Model Vault.
   - Auto-extracts quantization types (`Q4_K_M`, `IQ4_XS`, `Q4_0`) and parameter sizes.
4. **Vanguard Domain Specification Corpus Ingestion**:
   - Absorbed 8 canonical chunks into `corpus/canonical_chunks.json`.
5. **Live Verification & Accreditation (`./turnkey.sh eval`)**:
   - Passed 7 automated benchmark gates: Vulkan health, embedding generation, Shannon entropy math, hardware arbiter, model scanner, canary drift math, and grounded hierarchical retrieval.

---

## 8. Sovereign Multi-Turn Dialogue & General Chat Subsystem

The unified web cockpit (`http://localhost:8090`) features an integrated **General Chat** conversational interface directly on the single-page dashboard alongside the Spokewheel and Alien Artifact Vessel deck:

1. **Conversational Multi-Turn Engine (`core/harness.py` & `core/server.py`)**:
   - Endpoint: `POST /api/chat/stream`
   - Accepts full conversation history: `messages: [{role, content}]`
   - Dynamic CanaryAnchor extraction from the latest turn for real-time watermark retention and drift tracking.
   - Configurable RAG Grounding toggle: grounds turns against the 3-tier hierarchical index or falls back to pure parametric reasoning.
   - Emits Server-Sent Events (SSE):
     - `retrieval`: Grounded provenance chunks (`CHK-...`)
     - `token`: Chosen token, Top-1 probability, Shannon entropy (bits), rolling entropy, CanaryAnchor retention, context fidelity percentage, and top-5 candidate logprobs.
     - `verification`: Epistemological gap declaration, retrieval confidence, chunks cited, and fidelity status.
2. **Unified Single-Page UI Integration (`ui/index.html`)**:
   - `💬 General Chat` mode button on top header.
   - Conversation transcript with distinct operator and agent bubbles, live typing cursor, and real-time fidelity badges.
   - Live synchronization with Spokewheel Canvas (`circle.js`) and Top-5 Logprob pool.
   - **Inline Alien Artifact Compilation**: Every assistant response features an inline `[ 🧬 Compile Turn to Alien Artifact ]` button that loads the response into the cut-corner panel vessel and permits one-click saving to `./artifacts/`.
3. **Formal Schema Specification**:
   - `ui/chat_schema.json`: Complete JSON Schema for multi-turn chat directives and SSE streaming events.
4. **Direct Mode (Bypass Agent Persona) & General Framework Agent**:
   - **Direct Mode (`agents/direct.md`)**: Toggle switch `[x] ⚡ Direct Mode (No Persona)` allows operators to query the LLM and RAG index directly with zero agent persona, preamble, or roleplay framing—operating like standard AI harnesses.
   - **General User Agent (`agents/general.md`)**: Dedicated general-purpose framework agent engineered specifically for user inquiries, technical explanations, and structured markdown synthesis ready for instant Alien Artifact generation.
   - **Seamless Hot-Switching**: Fully integrated into the web cockpit dropdown, ReAct tray toggle, and Chat deck toggle with state preservation.


