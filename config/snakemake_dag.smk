# Snakemake Hierarchical Chunking & Embedding DAG
# Pipeline Node: criticalpath-pipeline-v1.0

import json
from pathlib import Path

DATA_DIR = Path("/mnt/wsl/rag-store-data")
RAW_DIR = DATA_DIR / "raw_documents"
CHUNK_DIR = DATA_DIR / "hierarchical_chunks"
EMBED_DIR = DATA_DIR / "embeddings"

rule all:
    input:
        f"{EMBED_DIR}/status.done"

rule normalize_raw_documents:
    input:
        raw_files = glob_wildcards(str(RAW_DIR) + "/{filename}.txt").filename
    output:
        normalized = f"{CHUNK_DIR}/manifest.json"
    shell:
        """
        mkdir -p {CHUNK_DIR}
        python3 -c "
import json, glob, os
files = glob.glob('/mnt/wsl/rag-store-data/raw_documents/*')
manifest = [{'file': f, 'size': os.path.getsize(f)} for f in files]
with open('{output.normalized}', 'w') as out:
    json.dump(manifest, out, indent=2)
"
        """

rule hierarchical_chunking:
    input:
        manifest = f"{CHUNK_DIR}/manifest.json"
    output:
        chunks = f"{CHUNK_DIR}/chunks_tree.json"
    params:
        parent_tokens = 1024,
        child_tokens = 256,
        overlap = 32
    shell:
        """
        python3 /opt/rag-pipeline/chunker.py --input {input.manifest} --output {output.chunks} --parent-size {params.parent_tokens} --child-size {params.child_tokens} --overlap {params.overlap}
        """

rule compute_embeddings_and_sync:
    input:
        chunks = f"{CHUNK_DIR}/chunks_tree.json"
    output:
        done = f"{EMBED_DIR}/status.done"
    shell:
        """
        mkdir -p {EMBED_DIR}
        python3 /opt/rag-pipeline/sync_store.py --chunks {input.chunks}
        touch {output.done}
        """
