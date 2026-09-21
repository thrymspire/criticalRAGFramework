# Verification Gate Specification: `criticalpath-eval-v1.0`
**Document Version:** 1.0.0-PROD  
**Node Role:** The Verification Gate (Quality Evaluation, Faithfulness Benchmarking, Hallucination Auditing)  
**Distro RootFS:** Ubuntu 26.04.1 LTS Minimal  
**Execution Model:** Ephemeral / On-Demand (Auto-terminated post-evaluation)  
**Evaluation Suite:** Ragas, TruLens, Deterministic Test Split Regression Benches

---

## 1. Operational Boundary & Guarantees

- **EPHEMERAL EXECUTION:** Kept stopped (`wsl --terminate criticalpath-eval-v1.0`) during normal operations. Only booted on-demand when a dataset batch run or pipeline re-indexing trigger executes.
- **ZERO PRODUCTION CONTAMINATION:** Evaluation logs, synthetic golden sets, and intermediate metric score matrices are strictly confined to this node or exported as pure JSON/CSV logs into `./`.
- **ZERO MEMORY CONTENTION:** By terminating the node after batch runs, the host machine reclaims all evaluation RAM immediately.

---

## 2. Benchmark Metrics Matrix

| Metric Name | Threshold Goal | Methodology |
| :--- | :--- | :--- |
| **Faithfulness** | `>= 0.88` | Ratio of claims in generated answer that can be directly inferred from retrieved context chunks. |
| **Answer Relevance** | `>= 0.85` | Semantic alignment between the user query and the final synthesized response. |
| **Context Recall** | `>= 0.90` | Percentage of relevant ground-truth sentences captured in the retrieved chunks. |
| **Context Precision** | `>= 0.82` | Signal-to-noise ratio: rank-weighted position of relevant chunks in top-k retrieval. |
| **Latency Budget** | `<= 800ms` | End-to-end retrieval + inference round-trip time across localhost loopback. |

---

## 3. Automation Protocol: `run-eval-gate.bat`

To execute an end-to-end verification gate run:
1. Double click `./shortcuts\run-eval-gate.bat` (or execute via CLI).
2. The script:
   - Starts `criticalpath-eval-v1.0`.
   - Executes `/opt/rag-eval/run_eval.py`.
   - Sends test queries to pipeline / store nodes.
   - Compares responses against `/opt/rag-eval/golden_dataset.json`.
   - Exports `eval_report_<timestamp>.json` and `.csv`.
   - Issues `wsl --terminate criticalpath-eval-v1.0`.
