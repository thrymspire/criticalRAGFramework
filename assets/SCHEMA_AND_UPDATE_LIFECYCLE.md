# Schema Instructions & Asset Update Lifecycle Guide
**Classification:** Standard Operating Procedure (SOP)  
**Applies To:** All files in `./`  
**Target Audience:** Any engineer, researcher, or automated agent onboarding or updating this RAG system.

---

## 1. Governance & Single Source of Truth

To ensure that any team member or agent can pick up this system at any moment and immediately understand its structure, every modification must follow this lifecycle protocol.

Whenever you:
1. Introduce a new asset (model, dataset, script, vector index, pipeline stage),
2. Modify an existing architecture boundary or network port,
3. Adapt the RAG pipeline to a new use case (e.g. Legal reasoning, Medical QA, Code intelligence),

You **MUST** update the asset documentation according to the schemas specified below.

---

## 2. Manifest Update Schema (For `ASSET_MANIFEST.md`)

When registering a new component, insert an entry into the appropriate table using this schema:

```markdown
| Asset Identifier | Asset Type | Owning Node | Host / Container Path | Port / Binding | Lifecycle Trigger |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `<name>-vX.Y` | `[VHDX | Script | Model | Service | Table]` | `[Store | Pipeline | Eval]` | `<absolute path>` | `<IP:Port or N/A>` | `[Persistent | On-Demand | Scheduled]` |
```

### Required Fields Definition:
- **Asset Identifier:** Semantic name ending with version suffix (e.g. `bge-m3-quant-v1.0`, `chunking-dag-v2.1`).
- **Asset Type:** Exactly one of: `Distro VHDX`, `Config File`, `Python Script`, `Batch Automation`, `Database Index`, `Inference Model`.
- **Owning Node:** Must declare strict boundary ownership (`criticalpath-store-v1.0`, `criticalpath-pipeline-v1.0`, or `criticalpath-eval-v1.0`). Never assign cross-boundary dual ownership.
- **Host / Container Path:** Both Windows host path and Linux in-distro path if applicable.
- **Port / Binding:** TCP/IP port or socket path (e.g., `127.0.0.1:5432`).
- **Lifecycle Trigger:** `Persistent` (runs constantly), `On-Demand` (spawned via script), or `Ephemeral` (auto-terminates).

---

## 3. Use-Case Adaptation Schema (Step-by-Step Procedure)

When changing the RAG workload from generic text retrieval to a specific domain (e.g. Finance, Healthcare, Engineering):

### Phase 1: Store Node Updates (`criticalpath-store-v1.0`)
1. **Embedding Dimension Modification:**  
   If switching embedding models (e.g. 768-dim `nomic-embed-text` to 1024-dim `bge-m3` or 1536-dim `text-embedding-3-small`):
   - Open store shell: `shortcuts\open-store-shell.bat`
   - Run database migration:
     ```sql
     ALTER TABLE rag_chunks ADD COLUMN embedding_1024 vector(1024);
     CREATE INDEX ON rag_chunks USING hnsw (embedding_1024 vector_cosine_ops);
     ```
   - Update `STORE_NODE_SCHEMA.md` with the new column definition and HNSW index parameters (`m=16, ef_construction=64`).

### Phase 2: Pipeline Node Updates (`criticalpath-pipeline-v1.0`)
1. **Chunking Strategy Tuning:**  
   - Edit `/opt/rag-pipeline/chunking_rules.yaml` in the pipeline distro.
   - Adjust `parent_chunk_tokens` (default 1024) and `child_chunk_tokens` (default 256) with `overlap_tokens` (default 32).
   - Re-validate the Snakemake DAG: `snakemake -s /opt/rag-pipeline/Snakefile --dry-run`.
   - Update `PIPELINE_NODE_SPEC.md` documenting the rationale and benchmark impact.

### Phase 3: Verification Gate Updates (`criticalpath-eval-v1.0`)
1. **Synthetic Bench Calibration:**  
   - Update `/opt/rag-eval/test_splits.json` with domain-specific ground truth pairs (Question, Expected Context, Ideal Answer).
   - Configure target metric thresholds in `EVAL_NODE_SPEC.md`:
     - Minimum Faithfulness: `>= 0.88`
     - Minimum Context Recall: `>= 0.85`
     - Latency budget: `<= 650ms`

---

## 4. Disaster Recovery & Snapshot Protocol

Before executing major package upgrades or altering PostgreSQL data directories:
1. Terminate all distros:
   ```cmd
   ./shortcuts\stop-rag-cluster.bat
   ```
2. Create an instant differential copy of the virtual disks:
   ```powershell
   Copy-Item "C:\WSL\distros\criticalpath-store-v1.0\ext4.vhdx" "C:\WSL\distros\criticalpath-store-v1.0\ext4.vhdx.bak"
   ```
3. To restore: Terminate WSL, overwrite `ext4.vhdx` with `.bak`, and execute `start-rag-cluster.bat`.
