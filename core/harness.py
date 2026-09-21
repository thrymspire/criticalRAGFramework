"""
Phase 4 — Autonomous ReAct Execution Harness Engine
Coordinates multi-stage retrieval, real-time token logprob streaming,
entropy-based hallucination detection, and grounded verification summaries.
"""

import os
import sys
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Generator

from .secrets import get_vault
from .retrieval import CorpusRetriever
from .stream_bridge import stream_tokens_from_llama, calculate_entropy
from .verification import verify_citations


@dataclass
class AgentAction:
    tool_name: str
    arguments: Dict[str, Any]


@dataclass
class AgentObservation:
    status: str
    output: Any


class HarnessOrchestrator:
    """The central execution harness coordinating ReAct agent cycles with logprob telemetry."""

    def __init__(
        self,
        server_url: str = "http://127.0.0.1:8080",
        workspace_dir: Optional[Path] = None,
        event_callback: Optional[Callable[[str, Any], None]] = None
    ):
        self.server_url = server_url.rstrip("/")
        self.workspace_dir = workspace_dir or Path(__file__).resolve().parent.parent
        self.event_callback = event_callback or (lambda evt, data: None)
        self.vault = get_vault()
        self.retriever = CorpusRetriever(server_url=self.server_url)
        self.directive = self.load_directive()

    def emit(self, event_type: str, data: Any) -> None:
        """Publishes telemetry to event listeners (UI, CLI, Logger)."""
        self.event_callback(event_type, data)

    def load_directive(self) -> str:
        """Loads agent instructions from AGENTS.md or workspace rules."""
        agents_file = self.workspace_dir / "AGENTS.md"
        if agents_file.exists():
            return agents_file.read_text(encoding="utf-8")
        return (
            "You are an autonomous sovereign AI assistant working within the Critical Path harness. "
            "Always ground your reasoning strictly in retrieved context."
        )

    def stream_agent_turn(
        self,
        user_prompt: str,
        max_tokens: int = 64
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Executes a complete, calibrated ReAct agent turn:
        1. Retrieves relevant corpus chunks.
        2. Injects retrieved context into prompt.
        3. Streams token logprobs & instantaneous Shannon entropy.
        4. Monitors rolling entropy for epistemological gaps / hallucination risks.
        5. Concludes with a standardized Verification Summary.
        """
        # Step 1: Retrieval probe
        retrieved = self.retriever.search(user_prompt, top_k=3)
        retrieved_summary = []
        rag_context_blocks = []

        for idx, item in enumerate(retrieved):
            doc = item.get("document") if item.get("document") else item
            score = item.get("score", 0.0)
            doc_id = doc.get("chunk_id") or doc.get("id") or item.get("chunk_id", f"CHK-{idx+1:04d}")
            title = doc.get("title") or item.get("title", "Corpus Document")
            content = doc.get("content") or item.get("content", "")
            parent_sec = doc.get("parent_section") or item.get("parent_section", content)

            retrieved_summary.append({"id": doc_id, "title": title, "score": round(score, 3)})
            # Parent-Document Retrieval: Precision chunk + surrounding section context
            rag_context_blocks.append(
                f"[{doc_id}] {title}\n"
                f"[CHUNK]: {content}\n"
                f"[PARENT SECTION CONTEXT]: {parent_sec}"
            )

        rag_context_str = "\n\n".join(rag_context_blocks)

        # Emit initial retrieval event
        yield {
            "type": "retrieval",
            "retrieved": retrieved_summary,
            "status": "grounded" if retrieved else "no_chunks"
        }

        # Step 2: Assemble grounded prompt
        grounded_system = (
            f"{self.directive}\n\n"
            f"[RETRIEVED CORPUS CONTEXT (HIERARCHICAL)]\n{rag_context_str}\n\n"
            f"[MANDATORY RULE] Ground every factual claim in the retrieved text above and cite chunk IDs as [CHK-...]. "
            f"If context is insufficient, explicitly declare [EPISTEMOLOGICAL GAP]."
        )

        full_prompt = f"System: {grounded_system}\nUser: {user_prompt}\nAssistant:"

        # Step 3: Stream tokens with logprob physics and watermark drift tracking
        from .watermark_drift import WatermarkDriftTracker
        drift_tracker = WatermarkDriftTracker(user_prompt)

        step_entropies: List[float] = []
        step_probs: List[float] = []
        full_text = ""

        for token_data in stream_tokens_from_llama(
            prompt=full_prompt,
            server_url=self.server_url,
            max_tokens=max_tokens,
            top_logprobs=5
        ):
            step_entropies.append(token_data["entropy"])
            step_probs.append(token_data["prob"])
            full_text = token_data.get("running_text", "")
            drift_telemetry = drift_tracker.update(token_data["chosen_token"])

            # Rolling entropy metrics
            rolling_entropy = sum(step_entropies[-5:]) / max(1, len(step_entropies[-5:]))
            avg_prob = sum(step_probs) / max(1, len(step_probs))

            # Yield token event with Phase 4 agent telemetry + Vanguard drift metrics
            yield {
                "type": "token",
                "step": token_data["step"],
                "chosen_token": token_data["chosen_token"],
                "prob": token_data["prob"],
                "entropy": token_data["entropy"],
                "rolling_entropy": round(rolling_entropy, 2),
                "avg_confidence": round(avg_prob, 3),
                "watermark_retention": drift_telemetry["watermark_retention"],
                "context_fidelity_pct": drift_telemetry["context_fidelity_pct"],
                "fidelity_status": drift_telemetry["fidelity_status"],
                "top": token_data["top"],
                "running_text": full_text,
                "status": token_data["status"]
            }

        # Step 4: Verification & Epistemological Gap Assessment
        import re
        citation_check = verify_citations(full_text, retrieved_summary)
        cited_in_text = citation_check["cited_ids"]

        mean_entropy = sum(step_entropies) / max(1, len(step_entropies)) if step_entropies else 0.0
        mean_confidence = sum(step_probs) / max(1, len(step_probs)) if step_probs else 0.0

        confidence_tier = "HIGH (>=0.85)" if mean_confidence >= 0.85 else ("MODERATE (0.72-0.84)" if mean_confidence >= 0.72 else "INSUFFICIENT (<0.72)")

        # Entropy & Citation Gate:
        # Force EPISTEMOLOGICAL GAP if mean entropy > 1.65 bits or zero chunk citations present
        entropy_breach = mean_entropy > 1.65
        citation_breach = not citation_check["citation_valid"]
        epistemological_gap = entropy_breach or citation_breach or mean_confidence < 0.60

        gap_reasons = []
        if entropy_breach:
            gap_reasons.append("Mean token entropy exceeded threshold (>1.65 bits)")
        if citation_breach:
            gap_reasons.extend(citation_check["reasons"])
        if mean_confidence < 0.60:
            gap_reasons.append("Confidence collapsed (<0.60)")

        final_drift = drift_tracker.get_telemetry()

        verification_summary = {
            "retrieval_confidence": confidence_tier,
            "mean_confidence": round(mean_confidence, 3),
            "mean_entropy_bits": round(mean_entropy, 2),
            "watermark_retention": final_drift["watermark_retention"],
            "context_fidelity_pct": final_drift["context_fidelity_pct"],
            "fidelity_status": final_drift["fidelity_status"],
            "canary_anchors_count": final_drift["canary_count"],
            "citation_valid": citation_check["citation_valid"],
            "unknown_citations": citation_check["unknown_citations"],
            "corpus_coverage": f"{len(cited_in_text)} retrieved chunks cited",
            "chunks_cited": cited_in_text,
            "epistemological_gap_declared": epistemological_gap,
            "gap_reasons": gap_reasons,
            "verification_status": "VERIFIED" if not epistemological_gap else "GAP_WARNING"
        }

        yield {
            "type": "verification",
            "verification": verification_summary,
            "status": "complete"
        }

    def stream_chat_turn(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        rag_enabled: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Executes a multi-turn conversational chat turn:
        1. Identifies latest user prompt and extracts CanaryAnchors.
        2. Retrieves grounding chunks from the 3-tier hierarchical retriever if enabled.
        3. Formats the full conversation history.
        4. Streams tokens with real-time logprob physics, Shannon entropy, and watermark retention.
        5. Concludes with a Verification Summary.
        """
        latest_user_prompt = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                latest_user_prompt = m.get("content", "")
                break

        retrieved_summary = []
        rag_context_str = ""

        if rag_enabled and latest_user_prompt:
            retrieved = self.retriever.search(latest_user_prompt, top_k=3)
            rag_context_blocks = []
            for idx, item in enumerate(retrieved):
                doc = item.get("document") if item.get("document") else item
                score = item.get("score", 0.0)
                doc_id = doc.get("chunk_id") or doc.get("id") or item.get("chunk_id", f"CHK-{idx+1:04d}")
                title = doc.get("title") or item.get("title", "Corpus Document")
                content = doc.get("content") or item.get("content", "")
                parent_sec = doc.get("parent_section") or item.get("parent_section", content)

                retrieved_summary.append({"id": doc_id, "title": title, "score": round(score, 3)})
                rag_context_blocks.append(
                    f"[{doc_id}] {title}\n"
                    f"[CHUNK]: {content}\n"
                    f"[PARENT SECTION CONTEXT]: {parent_sec}"
                )
            rag_context_str = "\n\n".join(rag_context_blocks)

            yield {
                "type": "retrieval",
                "retrieved": retrieved_summary,
                "status": "grounded" if retrieved else "no_chunks"
            }

        # Build system prompt with grounding
        system_content = self.directive
        if rag_context_str:
            system_content += f"\n\n[RETRIEVED CORPUS CONTEXT (HIERARCHICAL)]\n{rag_context_str}\n\n[MANDATORY RULE] Ground factual claims in the retrieved text above and cite chunk IDs as [CHK-...]."

        prompt_parts = [f"System: {system_content}"]
        for msg in messages:
            role = msg.get("role", "user")
            label = "User" if role == "user" else "Assistant"
            prompt_parts.append(f"{label}: {msg.get('content', '')}")

        prompt_parts.append("Assistant:")
        full_prompt = "\n\n".join(prompt_parts)

        # Drift tracking across conversation
        from .watermark_drift import WatermarkDriftTracker
        drift_tracker = WatermarkDriftTracker(latest_user_prompt or "conversation", turn_index=max(1, len(messages) // 2))

        step_entropies: List[float] = []
        step_probs: List[float] = []
        full_text = ""

        for token_data in stream_tokens_from_llama(
            prompt=full_prompt,
            server_url=self.server_url,
            max_tokens=max_tokens,
            top_logprobs=5
        ):
            step_entropies.append(token_data["entropy"])
            step_probs.append(token_data["prob"])
            full_text = token_data.get("running_text", "")
            drift_telemetry = drift_tracker.update(token_data["chosen_token"])

            rolling_entropy = sum(step_entropies[-5:]) / max(1, len(step_entropies[-5:]))
            avg_prob = sum(step_probs) / max(1, len(step_probs))

            yield {
                "type": "token",
                "step": token_data["step"],
                "chosen_token": token_data["chosen_token"],
                "prob": token_data["prob"],
                "entropy": token_data["entropy"],
                "rolling_entropy": round(rolling_entropy, 2),
                "avg_confidence": round(avg_prob, 3),
                "watermark_retention": drift_telemetry["watermark_retention"],
                "context_fidelity_pct": drift_telemetry["context_fidelity_pct"],
                "fidelity_status": drift_telemetry["fidelity_status"],
                "top": token_data["top"],
                "running_text": full_text,
                "status": token_data["status"]
            }

        import re
        citation_check = verify_citations(full_text, retrieved_summary)
        cited_in_text = citation_check["cited_ids"]
        mean_entropy = sum(step_entropies) / max(1, len(step_entropies)) if step_entropies else 0.0
        mean_confidence = sum(step_probs) / max(1, len(step_probs)) if step_probs else 0.0
        confidence_tier = "HIGH (>=0.85)" if mean_confidence >= 0.85 else ("MODERATE (0.72-0.84)" if mean_confidence >= 0.72 else "INSUFFICIENT (<0.72)")

        final_drift = drift_tracker.get_telemetry()

        verification_summary = {
            "retrieval_confidence": confidence_tier,
            "mean_confidence": round(mean_confidence, 3),
            "mean_entropy_bits": round(mean_entropy, 2),
            "watermark_retention": final_drift["watermark_retention"],
            "context_fidelity_pct": final_drift["context_fidelity_pct"],
            "fidelity_status": final_drift["fidelity_status"],
            "canary_anchors_count": final_drift["canary_count"],
            "citation_valid": citation_check["citation_valid"],
            "unknown_citations": citation_check["unknown_citations"],
            "corpus_coverage": f"{len(cited_in_text)} retrieved chunks cited",
            "chunks_cited": cited_in_text,
            "epistemological_gap_declared": mean_entropy > 1.70 or mean_confidence < 0.55 or not citation_check["citation_valid"],
            "verification_status": "VERIFIED" if mean_entropy <= 1.70 and citation_check["citation_valid"] else "GAP_WARNING",
            "gap_reasons": citation_check["reasons"]
        }

        yield {
            "type": "verification",
            "verification": verification_summary,
            "status": "complete"
        }
