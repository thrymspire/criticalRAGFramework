"""Citation validation utilities.

These checks validate only evidence the service can prove: citations must be
present and must refer to retrieved chunks. Token likelihood remains telemetry,
not a factual-correctness score.
"""

import re
from typing import Iterable, Mapping, Any

_CITATION = re.compile(r"\[(CHK-[A-Za-z0-9_-]+)\]")


def cited_chunk_ids(text: str) -> list[str]:
    return list(dict.fromkeys(_CITATION.findall(text)))


def verify_citations(text: str, retrieved: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    cited = cited_chunk_ids(text)
    retrieved_ids = {str(item.get("id") or item.get("chunk_id") or "") for item in retrieved}
    unknown = [citation for citation in cited if citation not in retrieved_ids]
    missing = bool(retrieved_ids) and not cited
    reasons = []
    if missing:
        reasons.append("Response cited none of the retrieved chunks")
    if unknown:
        reasons.append("Response cited chunk IDs that were not retrieved")
    return {"cited_ids": cited, "retrieved_ids": sorted(retrieved_ids), "unknown_citations": unknown,
            "citation_valid": not missing and not unknown, "reasons": reasons}
