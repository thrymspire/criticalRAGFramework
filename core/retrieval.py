"""
Corpus Retrieval Engine for Critical Path RAG
Exports HierarchicalRetriever as the primary 3-tier retrieval engine
with backward-compatible CorpusRetriever alias.
"""

from .hierarchical_retrieval import HierarchicalRetriever

# Canonical class alias
CorpusRetriever = HierarchicalRetriever

__all__ = ["HierarchicalRetriever", "CorpusRetriever"]
