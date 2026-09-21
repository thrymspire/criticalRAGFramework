# State Anchor Node Specification: `criticalpath-store-v1.0`
**Document Version:** 1.0.0-PROD  
**Node Role:** The State Anchor (Vector/Graph Persistence & Indexed Proximity Retrieval)  
**Distro RootFS:** Ubuntu 26.04.1 LTS Minimal  
**Bound Interfaces:** `127.0.0.1:5432` (PostgreSQL), `127.0.0.1:8000` (FastMCP Bridge)

---

## 1. Operational Boundary & Guarantees

- **STRICT BOUNDARY:** Zero LLM weights, zero agent toolings, zero document ingestion or text parsing logic.
- **SOLE RESPONSIBILITY:** Maintaining index persistence, executing cosine/L2 vector searches, filtering metadata, and managing write-ahead logging (WAL).
- **CRASH RESILIENCE:** If the upstream pipeline node (`criticalpath-pipeline-v1.0`) crashes during intensive text embedding or GPU batching, the state anchor remains completely isolated and unharmed.

---

## 2. Relational & Vector Schema DDL

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Table 1: Canonical Document Manifest
CREATE TABLE IF NOT EXISTS rag_documents (
    document_id TEXT PRIMARY KEY,
    title TEXT,
    source_uri TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: Hierarchical Vector Chunks
CREATE TABLE IF NOT EXISTS rag_chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT REFERENCES rag_documents(document_id) ON DELETE CASCADE,
    chunk_index INT,
    parent_chunk_id TEXT,
    content TEXT NOT NULL,
    token_count INT DEFAULT 0,
    embedding vector(768), -- Scalable to 1024 or 1536 depending on active model
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Production Indexes
CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc ON rag_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_parent ON rag_chunks(parent_chunk_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_meta ON rag_chunks USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding ON rag_chunks USING hnsw (embedding vector_cosine_ops);
```

---

## 3. Storage Allocation & WAL SSD Tuning

PostgreSQL configuration is tuned specifically for local NVMe SSD writes in `/etc/postgresql/18/main/conf.d/99-critical-rag-tuned.conf`:

```ini
shared_buffers = 1GB
work_mem = 64MB
maintenance_work_mem = 512MB
max_parallel_maintenance_workers = 4
wal_level = minimal
max_wal_senders = 0
synchronous_commit = off
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 512MB
listen_addresses = '127.0.0.1'
port = 5432
```

Dedicated cross-distro storage mount:
`/mnt/wsl/rag-store-data`

---

## 4. FastMCP Protocol Bridge Daemon

The daemon runs at `/opt/rag-store/mcp_server.py`, listening on `127.0.0.1:8000`:
- **GET `/health`**: Returns daemon health status.
- **POST `/mcp/query`**: Receives query embeddings, runs HNSW similarity search on Postgres, and returns top-k structured chunks and similarity scores.

```bash
# Verify Daemon Status
curl -s http://127.0.0.1:8000/health
```
