"""
Hierarchical RAG Retrieval Engine for Critical Path RAG
Implements 3-tier hierarchy:
  Level 1: Document Summaries (Coarse Filter)
  Level 2: Section Summaries (Topic Routing)
  Level 3: Precision Chunks (512 tokens / ~1600 chars, 64-token overlap)
With Parent-Document Context Expansion & Hybrid (Dense + BM25 + RRF) Fusion.
"""

import os
import re
import json
import math
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
SEED_FILE = ROOT_DIR / "corpus_seed.json"
STORAGE_NODE_DIR = Path("/data/corpus")


def clean_tokens(text: str) -> List[str]:
    """Tokenizes and normalizes text for BM25 keyword matching."""
    return [t.lower() for t in re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text)]


def compute_bm25(query_tokens: List[str], doc_tokens: List[str], avg_len: float, k1: float = 1.5, b: float = 0.75) -> float:
    """Lightweight BM25 term frequency scoring."""
    doc_len = len(doc_tokens)
    if doc_len == 0 or avg_len == 0:
        return 0.0
    score = 0.0
    tf_map: Dict[str, int] = {}
    for t in doc_tokens:
        tf_map[t] = tf_map.get(t, 0) + 1

    for q in query_tokens:
        tf = tf_map.get(q, 0)
        if tf > 0:
            num = tf * (k1 + 1)
            den = tf + k1 * (1 - b + b * (doc_len / avg_len))
            score += num / den
    return score


class HierarchicalRetriever:
    """
    3-Tier Hierarchical RAG with Parent-Document Context Expansion:
    Level 1 -> Document summaries
    Level 2 -> Section summaries
    Level 3 -> Chunks (512 tokens / ~1600 chars, 64 token overlap)
    """

    def __init__(self, server_url: str = "http://127.0.0.1:8080"):
        self.server_url = server_url.rstrip("/")
        self.documents: List[Dict[str, Any]] = []      # Level 1
        self.sections: List[Dict[str, Any]] = []       # Level 2
        self.chunks: List[Dict[str, Any]] = []         # Level 3
        self.embedding_cache: Dict[str, List[float]] = {}
        self._direct_http = self._check_direct_http()
        self.load_all()

    def _check_direct_http(self) -> bool:
        """Probes whether 127.0.0.1:8080 is directly reachable via HTTP within 200ms."""
        try:
            with urllib.request.urlopen(f"{self.server_url}/health", timeout=0.2) as r:
                return r.status == 200
        except Exception:
            return False

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Queries llama-server /v1/embeddings with zero-hang host fallback."""
        if not text.strip():
            return None

        cache_key = text.strip()[:200]
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        url = f"{self.server_url}/v1/embeddings"
        payload = json.dumps({"input": text})

        if self._direct_http:
            try:
                req = urllib.request.Request(
                    url,
                    data=payload.encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": "CriticalRAG-Hierarchical"}
                )
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    vec = data["data"][0]["embedding"]
                    self.embedding_cache[cache_key] = vec
                    return vec
            except Exception:
                self._direct_http = False

        # Host bridge fallback via Windows curl.exe (executes instantly on Windows host)
        try:
            win_curl = "/mnt/c/Windows/System32/curl.exe" if os.path.exists("/mnt/c/Windows/System32/curl.exe") else "curl.exe"
            cmd = [win_curl, "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", payload]
            res = subprocess.check_output(cmd, timeout=3)
            data = json.loads(res.decode("utf-8"))
            vec = data["data"][0]["embedding"]
            self.embedding_cache[cache_key] = vec
            return vec
        except Exception:
            return None

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculates cosine similarity."""
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def load_all(self) -> None:
        """Loads and indexes the 3-tier hierarchy strictly from native ext4 paths."""
        self.documents = []
        self.sections = []
        self.chunks = []

        # 1. Baseline Seed Corpus (Immutable)
        if SEED_FILE.exists():
            try:
                seed_data = json.loads(SEED_FILE.read_text(encoding="utf-8"))
                items = seed_data if isinstance(seed_data, list) else seed_data.get("documents", [seed_data])
                for s in items:
                    self._ingest_raw_entry(s)
            except Exception as e:
                print(f"[HIERARCHICAL] Error loading seed: {e}")

        # 2. Ingest real project documents on native ext4
        doc_files = [
            ROOT_DIR / "AGENTS.md",
            ROOT_DIR / ".antigravity" / "rules.md"
        ]
        # Also check agents directory
        agents_dir = ROOT_DIR / "agents"
        if agents_dir.exists():
            doc_files.extend(list(agents_dir.glob("*.md")))

        for df in doc_files:
            if df.exists() and df.is_file():
                try:
                    self.ingest_markdown_file(df)
                except Exception as ex:
                    print(f"[HIERARCHICAL] Error ingesting {df.name}: {ex}")

        # 3. Check /data/corpus
        if STORAGE_NODE_DIR.exists():
            for mf in STORAGE_NODE_DIR.glob("*.md"):
                try:
                    self.ingest_markdown_file(mf)
                except Exception:
                    pass

        # Compute pre-tokenized representations for instant BM25
        for s in self.sections:
            s["_tokens"] = clean_tokens(f"{s['title']} {s['summary']}")
        for c in self.chunks:
            c["_tokens"] = clean_tokens(f"{c['title']} {c['content']}")

        print(f"[HIERARCHICAL] Loaded {len(self.documents)} docs (L1), {len(self.sections)} sections (L2), {len(self.chunks)} chunks (L3).")

    def _ingest_raw_entry(self, entry: Dict[str, Any]) -> None:
        """Ingests a raw dictionary entry."""
        doc_id = entry.get("id", f"DOC-{len(self.documents)+1:03d}")
        title = entry.get("title", "Corpus Document")
        content = entry.get("content", "")
        summary = content[:200] + "..." if len(content) > 200 else content

        self.documents.append({"doc_id": doc_id, "title": title, "summary": summary, "content": content})

        sec_id = f"SEC-{doc_id}-01"
        self.sections.append({"sec_id": sec_id, "doc_id": doc_id, "title": title, "summary": summary, "content": content})

        chunk_id = f"CHK-{len(self.chunks)+1:04d}"
        self.chunks.append({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "sec_id": sec_id,
            "title": title,
            "content": content,
            "parent_section": content
        })

    def ingest_markdown_file(self, file_path: Path) -> None:
        """Parses a markdown document into Document -> Sections -> Chunks."""
        text = file_path.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            return

        doc_name = file_path.stem.replace("_", " ").title()
        doc_id = f"DOC-{file_path.stem.upper()[:8]}"

        # Level 1: Document Summary
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        doc_summary = paragraphs[0] if paragraphs else doc_name
        if len(doc_summary) > 250:
            doc_summary = doc_summary[:250] + "..."

        self.documents.append({
            "doc_id": doc_id,
            "title": doc_name,
            "summary": doc_summary,
            "path": str(file_path)
        })

        # Level 2: Section Breakdown
        section_splits = re.split(r"\n(?=##?\s)", text)
        for s_idx, sec_text in enumerate(section_splits):
            sec_text = sec_text.strip()
            if not sec_text:
                continue

            lines = sec_text.split("\n")
            header_line = lines[0].lstrip("#").strip() if lines[0].startswith("#") else f"Section {s_idx+1}"
            sec_id = f"SEC-{doc_id}-{s_idx+1:02d}"
            sec_body = "\n".join(lines[1:]).strip() if len(lines) > 1 else sec_text
            sec_summary = sec_body[:200] + "..." if len(sec_body) > 200 else sec_body

            self.sections.append({
                "sec_id": sec_id,
                "doc_id": doc_id,
                "title": f"{doc_name} > {header_line}",
                "summary": sec_summary,
                "content": sec_body
            })

            # Level 3: Precision Chunking (nominal ~1400 chars, 200 chars overlap)
            chunk_size_chars = 1400
            overlap_chars = 200
            start = 0

            while start < len(sec_body):
                end = start + chunk_size_chars
                chunk_str = sec_body[start:end].strip()
                if chunk_str:
                    chunk_id = f"CHK-{doc_id[:4]}-{len(self.chunks)+1:04d}"
                    self.chunks.append({
                        "chunk_id": chunk_id,
                        "doc_id": doc_id,
                        "sec_id": sec_id,
                        "title": f"{doc_name} > {header_line}",
                        "content": chunk_str,
                        "parent_section": sec_body[:1800]  # Expanded parent context
                    })
                if end >= len(sec_body):
                    break
                start = end - overlap_chars

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Hierarchical Query Execution:
        1. Level 1 & 2 Coarse Routing: Finds top matching sections via BM25 + Document summaries.
        2. Queries embedding for query once.
        3. Scans precision chunks (Level 3) restricted to / boosted by candidate sections.
        4. Expands parent section context for LLM grounding.
        """
        if not self.chunks:
            return []

        q_tokens = clean_tokens(query)
        if not q_tokens:
            q_tokens = [query.lower()]

        # Step 1: Coarse Topic Routing (Instant BM25 on Level 2 Sections)
        avg_sec_len = sum(len(s.get("_tokens", [])) for s in self.sections) / max(1, len(self.sections))
        sec_scores = []
        for sec in self.sections:
            bm25_s = compute_bm25(q_tokens, sec.get("_tokens", []), avg_sec_len)
            sec_scores.append((sec["sec_id"], bm25_s))

        sec_scores.sort(key=lambda x: x[1], reverse=True)
        # Select top candidate sections (top matching or fallback to first)
        candidate_sec_ids = {s[0] for s in sec_scores[:max(2, top_k)] if s[1] > 0}
        if not candidate_sec_ids and sec_scores:
            candidate_sec_ids = {sec_scores[0][0]}

        # Step 2: RESTRICT chunk search to ONLY candidate sections!
        candidate_chunks = [c for c in self.chunks if c.get("sec_id") in candidate_sec_ids]
        if not candidate_chunks:
            candidate_chunks = self.chunks[:top_k * 2]

        # Step 3: Fetch single embedding for the query
        query_vec = self.get_embedding(query)

        # Step 4: Level 3 Precision Chunk Search with Dense + BM25 Fusion
        avg_chunk_len = sum(len(c.get("_tokens", [])) for c in candidate_chunks) / max(1, len(candidate_chunks))
        scored_chunks = []

        for chunk in candidate_chunks:
            bm25_score = compute_bm25(q_tokens, chunk.get("_tokens", []), avg_chunk_len)
            dense_score = 0.0
            if query_vec:
                chunk_vec = self.get_embedding(f"{chunk['title']}: {chunk['content'][:200]}")
                if chunk_vec:
                    dense_score = self.cosine_similarity(query_vec, chunk_vec)

            final_score = (dense_score * 0.70) + (min(1.0, bm25_score * 0.30))

            scored_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "title": chunk["title"],
                "content": chunk["content"],
                "parent_section": chunk.get("parent_section", chunk["content"]),
                "sec_id": chunk.get("sec_id", ""),
                "doc_id": chunk.get("doc_id", ""),
                "score": round(final_score, 3)
            })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)

        results = []
        for c in scored_chunks[:top_k]:
            results.append({
                "document": {
                    "id": c["chunk_id"],
                    "title": c["title"],
                    "content": c["content"],
                    "parent_section": c["parent_section"],
                    "sec_id": c["sec_id"],
                    "doc_id": c["doc_id"]
                },
                "score": c["score"]
            })

        return results
