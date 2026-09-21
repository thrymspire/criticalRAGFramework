# Critical Path Harness Subsystem Specification
**Node Identifier:** `criticalpath-harness-v1.0`  
**Distribution:** Ubuntu 26.04.1 LTS (WSL2 Kernel 6.18.40.1-microsoft-standard-WSL2)  
**Storage VHDX:** `C:\WSL\distros\criticalpath-harness-v1.0\ext4.vhdx`  

---

## 1. Node Responsibilities
- **Isolated Execution Boundary:** Houses `/workspace/project` mounting points and isolates production and development secrets (`/etc/harness/secrets/` chmod 700).
- **Automated Test & Benchmark Runner:** Executes non-destructive regression benchmarks, token probability physics assertions, and hardware arbitration tests.
- **Inter-Node Coordination:** Dispatches jobs across `criticalpath-store-v1.0` (data), `criticalpath-pipeline-v1.0` (ingest), and `criticalpath-eval-v1.0` (scoring).

## 2. Secrets & Credential Isolation
- Storage location: `/etc/harness/secrets/` and `/root/.secrets.env` (chmod 600).
- Prevents accidental leakage into git commits, unprivileged shell history, or host environment.

## 3. Linkage to harness-enclave Core
- Core runtime logic originates in `harness-enclave:/opt/critical-rag/` and binds dynamically into `/workspace/project`.
