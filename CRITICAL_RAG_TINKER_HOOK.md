# Critical RAG Tinker Hook & Master Blueprint
**Workspace:** `./`  
**Mounted in Harness:** `criticalpath-harness-v1.0` at `/workspace/project/`  
**Primary Endpoint:** `http://127.0.0.1:8080/v1` (Native Vulkan or Docker fallback)

---

## 1. Quick-Start Tinker Loop

### Step 1: Launch the Local Inference Engine
* **Option A (Preferred: Native Vulkan on AMD 780M GPU):**
  Double-click [`launch_vulkan_server.bat`](file:///./launch_vulkan_server.bat) or run from PowerShell:
  ```powershell
  & "llama-server" `
    -m "models/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf" `
    --host 0.0.0.0 --port 8080 -ngl 99 -c 8192 --embedding --pooling mean
  ```
  *(Yields ~269 t/s prompt processing and native Vulkan acceleration).*
* **Option B (Docker CPU Fallback in WSL2):**
  If ComfyUI is rendering a heavy batch and you want zero VRAM contention:
  ```bash
  wsl -d docker-engine -u root docker compose -f /mnt/c/Users/Thrym/Desktop/Critical\ RAG/docker-compose.yml up -d
  ```

### Step 2: Run the ReAct Agent Loop
From Windows PowerShell:
```powershell
python "./react_loop.py" "What is the role of the Critical Path Store node?"
```
Or from inside the **Harness Enclave**:
```bash
wsl -d criticalpath-harness-v1.0
cd /workspace/project
python3 react_loop.py "What are the nodes in the Critical Path cluster?"
```

---

## 2. Core Architectural Hooks Implemented

1. **Auto-Discovery of [`AGENTS.md`](file:///./AGENTS.md):**
   * The `react_loop.py` script automatically inspects `/workspace/project/AGENTS.md` (or local directory) and injects the operational rules into the agent system prompt.
2. **Dual-Endpoint Verification (Chat + Embeddings):**
   * Calls `/v1/chat/completions` for reasoning synthesis.
   * Calls `/v1/embeddings` with `--pooling mean` to generate dense vectors for RAG document retrieval.
3. **Data Store Wiring (`criticalpath-store-v1.0`):**
   * The seed corpus lives at `/data/corpus/critical_path_corpus_seed.json` in `criticalpath-store-v1.0`.
   * Mirrored in [`corpus_seed.json`](file:///./corpus_seed.json) for cross-subsystem resilience.
4. **Hardware Guardrails Enforced:**
   * `--reserve-vram 2.0` in ComfyUI prevents 0x3B display driver bugchecks.
   * `PYTORCH_CUDA_ALLOC_CONF=garbage_collection_threshold:0.8,max_split_size_mb:512`.
   * **Vulkan Memory Ceiling:** Never load GGUF models larger than ~14 GB into Vulkan while ComfyUI is active. The 4B Nemotron is the designated agent model.

---

## 3. Next Tinker Steps (Your Roadmap)

1. **Expand Tool Suite:** Add new actions to `react_loop.py` (e.g. `read_file`, `write_patch`, `run_command`).
2. **Wire Pipeline Distro:** In `criticalpath-pipeline-v1.0`, build an ingest script that chunks documents, embeds them via `http://127.0.0.1:8080/v1/embeddings`, and writes vectors to `criticalpath-store-v1.0:/data/embeddings/`.
3. **Connect Multi-Agent Handshake:** Use the Harness secrets vault (`/etc/harness/secrets/`) to store API keys for external fallback models (e.g. Gemini / Anthropic) when local confidence is below threshold.
