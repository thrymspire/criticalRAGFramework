#!/usr/bin/env python3
"""
CRITICAL RAG // WATERMARK DRIFT TRACKER & CONTEXT FIDELITY ENGINE (Interleaved from Ollama-Vanguard)
Extracts high-entropy CanaryAnchor tokens from prompt directives, tracks watermark retention
across streaming token steps, and computes real-time Context Drift and Fidelity.
"""

import re
from typing import Set, List, Dict, Any


STOP_WORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at", "by", "for",
    "with", "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "don", "should", "now", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "it", "its"
}


class WatermarkDriftTracker:
    def __init__(self, prompt: str, context_budget: int = 4096, turn_index: int = 1):
        self.prompt = prompt
        self.context_budget = context_budget
        self.turn_index = turn_index
        self.canary_anchors = self._extract_canary_anchors(prompt)
        self.accumulated_text = ""
        self.tokens_generated = 0

    def _extract_canary_anchors(self, text: str) -> Set[str]:
        """Extract high-entropy domain nouns, technical terms, and constraints as CanaryAnchors."""
        raw_words = re.findall(r'[a-zA-Z0-9_\-\.\:\/]+', text.lower())
        anchors = set()
        for w in raw_words:
            clean = re.sub(r'^[^\w]+|[^\w]+$', '', w)
            if len(clean) >= 3 and clean not in STOP_WORDS and not clean.isdigit():
                anchors.add(clean)
        return anchors

    def update(self, token: str) -> Dict[str, Any]:
        """Update tracker with newly streamed token and calculate drift telemetry."""
        self.accumulated_text += token
        self.tokens_generated += 1
        return self.get_telemetry()

    def get_telemetry(self) -> Dict[str, Any]:
        """Calculates current WatermarkRetention, ContextDrift, and ContextFidelity."""
        if not self.canary_anchors:
            return {
                "canary_count": 0,
                "anchors_recalled": 0,
                "watermark_retention": 1.0,
                "context_drift_pct": 0.0,
                "context_fidelity_pct": 100.0,
                "fidelity_status": "ANCHOR LOCKED",
                "tokens_generated": self.tokens_generated,
                "budget_saturation_pct": round((self.tokens_generated / max(1, self.context_budget)) * 100.0, 2)
            }

        text_lower = self.accumulated_text.lower()
        recalled = sum(1 for anchor in self.canary_anchors if anchor in text_lower)
        retention = recalled / len(self.canary_anchors)

        # Context saturation ratio S_ctx
        saturation = min(1.0, self.tokens_generated / max(1, self.context_budget))

        # Multi-turn entropy factor eta
        turn_entropy = min(1.0, self.turn_index / 10.0)

        # Vanguard Context Drift Equation:
        # Delta_drift = (1 - R_watermark) * 0.65 + S_ctx * 0.25 + eta * 0.10
        drift = ((1.0 - retention) * 0.65) + (saturation * 0.25) + (turn_entropy * 0.10)
        drift = max(0.0, min(1.0, drift))

        fidelity = max(0.0, min(100.0, (1.0 - drift) * 100.0))

        if fidelity >= 85.0:
            status = "ANCHOR LOCKED"
        elif fidelity >= 70.0:
            status = "NOMINAL STABLE"
        elif fidelity >= 48.0:
            status = "ATTENTION DILUTION"
        else:
            status = "CRITICAL DRIFT"

        return {
            "canary_count": len(self.canary_anchors),
            "anchors_recalled": recalled,
            "watermark_retention": round(retention, 3),
            "context_drift_pct": round(drift * 100.0, 2),
            "context_fidelity_pct": round(fidelity, 2),
            "fidelity_status": status,
            "tokens_generated": self.tokens_generated,
            "budget_saturation_pct": round(saturation * 100.0, 2)
        }


if __name__ == "__main__":
    prompt = "Explain the 4-tier Critical Path cluster and its storage guardrails."
    tracker = WatermarkDriftTracker(prompt)
    print("Canary Anchors:", tracker.canary_anchors)

    sample_output = "The Critical Path cluster utilizes a 4-tier architecture with strict storage guardrails."
    for word in sample_output.split():
        telemetry = tracker.update(word + " ")
    
    print("\n--- Final Telemetry ---")
    for k, v in tracker.get_telemetry().items():
        print(f"{k}: {v}")
