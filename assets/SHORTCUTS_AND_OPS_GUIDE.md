# Operations & Shortcuts Guide: Critical RAG
**Quick Reference Manual**  
**Location of Executable Shortcuts:** `./shortcuts\`

---

## 1. Primary Lifecycle Controls

| Control File | Action | When to Use |
| :--- | :--- | :--- |
| `start-rag-cluster.bat` | Starts store node (Postgres 18 + FastMCP) and pipeline node, verifies network readiness. | Run at the start of work or when beginning ingestion / querying. |
| `stop-rag-cluster.bat` | Gracefully shuts down Postgres, terminates all three WSL distros. | Run when finished working to release all CPU and RAM back to Windows. |
| `status-rag-cluster.bat` | Checks distro lifecycle states, tests TCP ports 5432 and 8000, checks `/mnt/wsl/rag-store-data`. | Run anytime to diagnose network connectivity or service status. |
| `run-eval-gate.bat` | Boots eval node, runs verification benchmarks, writes reports, and terminates eval node. | Run after ingesting new document sets or tuning chunking/prompt parameters. |

---

## 2. Interactive Shell Consoles

Direct bash shell launchers into each isolated container:

- `open-store-shell.bat` — Launches bash in `criticalpath-store-v1.0`.
  - Useful commands:
    ```bash
    su - postgres
    psql -d critical_rag
    # Inspect chunks table:
    SELECT count(*), avg(token_count) FROM rag_chunks;
    ```
- `open-pipeline-shell.bat` — Launches bash in `criticalpath-pipeline-v1.0`.
  - Useful commands:
    ```bash
    python3 /opt/rag-pipeline/pipeline_orchestrator.py
    ls -la /dev/dxg
    ```
- `open-eval-shell.bat` — Launches bash in `criticalpath-eval-v1.0`.
  - Useful commands:
    ```bash
    python3 /opt/rag-eval/run_eval.py --dry-run
    cat /opt/rag-eval/reports/latest.json | jq .
    ```

---

## 3. Host Memory & CPU Tuning (`~/.wslconfig`)

Applied settings:
```ini
[wsl2]
memory=16GB
processors=12
swap=4GB

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
```
- **Processors:** 12 of 16 logical threads assigned to WSL2, reserving 4 threads for Windows UI and background responsiveness.
- **Memory:** 16GB assigned to WSL2, leaving 8GB for Windows system host stability.
- **`autoMemoryReclaim=gradual`:** Automatically returns unused Linux page cache back to Windows.
