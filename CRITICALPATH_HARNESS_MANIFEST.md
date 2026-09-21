# Critical Path Harness Subsystem Manifest
- [x] Node Identifier: `criticalpath-harness-v1.0`
- [x] Naming Schema Alignment: Canonical Critical Path Micro-Distro Standard
- [x] Base Operating System: Ubuntu 26.04.1 LTS (Resolute Raccoon)
- [x] Subsystem Kernel: `6.18.40.1-microsoft-standard-WSL2`
- [x] Storage Partition: `C:\WSL\distros\criticalpath-harness-v1.0\ext4.vhdx`
- [x] Primary Architectural Role: Automated Test Execution, Benchmark Runner & Integration Harness
- [x] Project Mount Component: Dedicated mount boundary for attaching active project code inside
- [x] Secrets & Credential Vault: Secure enclave holding all project secrets, tokens, and API keys
- [x] Initialization Engine: Native Linux `systemd` enabled (`/etc/wsl.conf`)
- [x] Core Toolchains: Python 3.14.3, curl 8.18, ca-certificates, ext4 native I/O

## Core Functional Components

### 1. Project In-Mount Boundary
The harness distro acts as the dedicated execution boundary for project code:
- **Mount Point:** `/workspace/project/` (or dynamic bind mounts via `/mnt/c/` / `ext4`)
- **Purpose:** Attaches the active project codebase directly inside the harness environment so automated test suites, integration tests, and linters run in a pure, reproducible Linux userspace without modifying or polluting the host environment or other distros.

### 2. Secrets & API Key Isolation Vault
The harness distro serves as the centralized, protected enclave for holding all sensitive credentials:
- **Vault Location:** `/etc/harness/secrets/` and protected environment files (`/root/.secrets.env` with `chmod 600`)
- **Held Credentials:** AI provider API keys (Anthropic, OpenAI, Gemini, Hugging Face), database connection secrets, webhook signing keys, and automation tokens.
- **Security Boundary:** Isolates sensitive production/development keys away from `harness-enclave` and storage distros, preventing accidental exposure in git commits or unprivileged shell history.


## Canonical Critical Path Cluster Topology
The `criticalpath-harness-v1.0` node completes the four-tier architectural lifecycle for the Critical Path ecosystem:

| Cluster Node | Architecture | Role & Responsibility | Storage Path |
| :--- | :--- | :--- | :--- |
| **`criticalpath-store-v1.0`** | Ubuntu 26.04 Minimal | Canonical Gantt & Ontology Storage Core | `C:\WSL\distros\criticalpath-store-v1.0\ext4.vhdx` |
| **`criticalpath-pipeline-v1.0`**| Ubuntu 26.04 Minimal | Data Ingestion, Extraction & Pipeline Transform | `C:\WSL\distros\criticalpath-pipeline-v1.0\ext4.vhdx` |
| **`criticalpath-eval-v1.0`** | Ubuntu 26.04 Minimal | Metric Verification & Output Evaluation | `C:\WSL\distros\criticalpath-eval-v1.0\ext4.vhdx` |
| **`criticalpath-harness-v1.0`** | **Ubuntu 26.04.1 LTS** | **Automated Execution Harness & Integration Test Bed** | `C:\WSL\distros\criticalpath-harness-v1.0\ext4.vhdx` |

## Subsystem Hardware & Network Allocation
| Metric | Configuration | Operational Notes |
| :--- | :--- | :--- |
| **Global Memory Boundary** | 16.0 GB (via `.wslconfig`) | Shared dynamically with 8.0 GB Windows reserve |
| **Processors** | 12 Virtual Processors | Bound to AMD Ryzen Z1 Extreme Zen 4 cores |
| **Disk Format** | Dynamic Virtual Hard Disk (`ext4.vhdx`)| Direct native ext4 execution with zero NTFS overhead |
| **Default User** | `root` (passwordless sudo available) | Automated CI/CD script execution without prompts |

## 5. Active Sovereign Agent Roster

The harness environment supports on-the-fly hot-switching between 5 specialized agents defined in `agents/<name>.md`:
1. **`engineer`** (Rocket & Systems Engineer, temp 0.65, top-5 logprobs, 1024 tokens)
2. **`framework`** (Meta-Auditor & Self-Critique Engineer, temp 0.40, top-5 logprobs, 1536 tokens)
3. **`mechanic`** (Hardware, VRAM & Driver Specialist, temp 0.10, top-5 logprobs, 1024 tokens)
4. **`analyst`** (Corpus Synthesis & Epistemological Audit, temp 0.30, top-5 logprobs, 1024 tokens)
5. **`debug`** (Token Logprob & Shannon Entropy Debugger, temp 0.05, top-5 logprobs, 1024 tokens)

## 6. Isolated Environment Turnkey Control Plane

Execution is 100% contained within Linux ext4 via `~/Critical-RAG/turnkey.sh`:
- `./turnkey.sh start`: Launches streaming server (Port 8090)
- `./turnkey.sh stop`: Halts server & releases port 8090
- `./turnkey.sh status`: Full node telemetry, port verification & active agent
- `./turnkey.sh agent [name]`: Agent inventory & mid-session hot-switcher
- `./turnkey.sh run [args]`: Direct CLI ReAct agent executor
- `./turnkey.sh eval`: Automated benchmark & hardware verification gate

## 7. Operational & Execution Commands
```bash
# Launch interactive shell inside the harness node
wsl -d criticalpath-harness-v1.0

# Execute turnkey status check directly
wsl -d harness-enclave -u rag-admin -- bash -c "cd ~/Critical-RAG && ./turnkey.sh status"

# Run the verification gate suite
wsl -d harness-enclave -u rag-admin -- bash -c "cd ~/Critical-RAG && ./turnkey.sh eval"

# Inspect harness node resource usage
wsl -d criticalpath-harness-v1.0 -u root systemctl status --no-pager
```

## 8. Vanguard Foundry Interleaved Capabilities
- [x] **Universal Hardware Resource Arbiter (`core/hardware_arbiter.py`)**: Real-time topology detection (AVX-512, 12 cores, 11.68 GB RAM, Host Vulkan Port 8080) and 4-tier model/context arbitration (Tier 2 Zen4 APU).
- [x] **Watermark Drift & Context Fidelity Engine (`core/watermark_drift.py`)**: Formal CanaryAnchor extraction $\mathcal{A}_k$ with real-time drift telemetry $\Delta_{\text{drift}}$ and four-tier fidelity status (`ANCHOR LOCKED`, `NOMINAL STABLE`, `ATTENTION DILUTION`, `CRITICAL DRIFT`).
- [x] **Model Vault Discovery Scanner (`core/model_scanner.py`)**: Automated GGUF discovery, tag sanitization, quantization parsing (Q4_K_M, IQ4_XS, Q4_0), and memory footprint profiling.
- [x] **Visual Insignia Asset (`assets/logo.svg`)**: Vanguard Formline Insignia integrated into the Sovereign Cockpit.

## 9. Multi-Turn Dialogue & General Chat Subsystem
- [x] **Multi-Turn Chat Streaming Engine (`core/harness.py`, `core/server.py`)**: `POST /api/chat/stream` supporting full conversational array `messages: [{role, content}]`, per-turn CanaryAnchor tracking, 3-tier hierarchical RAG grounding toggle, and real-time SSE token emission.
- [x] **Direct Mode Toggle (No Agent Persona) (`agents/direct.md`)**: Allows raw queries to the LLM and RAG without agent persona roleplay framing, with synchronized toggles in ReAct and Chat decks.
- [x] **General Framework & User Agent (`agents/general.md`)**: Dedicated general-purpose agent for direct questions, explanations, synthesis, and structured outputs for instant Alien Artifact generation.
- [x] **Unified Single-Page Cockpit (`ui/index.html`)**: Chat mode with speech bubble transcript, live typing cursor, and inline `[ 🧬 Compile Turn to Alien Artifact ]` button connected to the Live Alien Artifact Vessel deck and desktop target folder `./artifacts/`.
- [x] **Formal Dialogue Schema (`ui/chat_schema.json`)**: Machine-readable JSON Schema for conversational history payloads and SSE stream physics events.


