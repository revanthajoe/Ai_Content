"""
Similarity Guard – Anti-repetition enforcement layer.
Uses SequenceMatcher for text similarity and tracks used content
to prevent degenerative evolution.
"""

from __future__ import annotations
import re
from difflib import SequenceMatcher
from .models import MutationStrategy


class SimilarityGuard:
    """
    Prevents repetitive mutations by:
    - Measuring text similarity against parent and siblings
    - Tracking used text fragments across generations
    - Preventing strategy reuse within the same evolution
    - Cleaning content to prevent superficial variation gaming
    """

    DEFAULT_THRESHOLD = 0.65  # Reject if similarity > this

    def __init__(self, threshold: float = DEFAULT_THRESHOLD):
        self.threshold = threshold
        self._used_texts: list[str] = []
        self._used_strategies: list[MutationStrategy] = []
        self._used_hooks: set[str] = set()
        self._used_ctas: set[str] = set()

    # ── Public API ────────────────────────────────────────────────────────────

    def check(self, new_content: str, parent_content: str) -> tuple[bool, float, str]:
        """
        Check if a mutation passes the similarity guard.

        Returns:
            (accepted, similarity_score, rejection_reason)
        """
        cleaned_new = self._clean(new_content)
        cleaned_parent = self._clean(parent_content)

        # 1. Check similarity to parent
        parent_sim = self._compute_similarity(cleaned_new, cleaned_parent)
        if parent_sim > self.threshold:
            return False, parent_sim, f"Too similar to parent ({parent_sim:.2%} > {self.threshold:.0%} threshold)"

        # 2. Check similarity to all previously used texts
        for i, used in enumerate(self._used_texts):
            sibling_sim = self._compute_similarity(cleaned_new, self._clean(used))
            if sibling_sim > self.threshold:
                return (
                    False,
                    sibling_sim,
                    f"Too similar to generation {i} sibling ({sibling_sim:.2%} > {self.threshold:.0%} threshold)",
                )

        # 3. Check for repeated hooks
        hook = self._extract_hook(new_content)
        if hook and hook in self._used_hooks:
            return False, 1.0, "Duplicate hook detected"

        # 4. Check for repeated CTAs
        cta = self._extract_cta(new_content)
        if cta and cta in self._used_ctas:
            return False, 1.0, "Duplicate CTA detected"

        return True, parent_sim, ""

    def check_strategy(self, strategy: MutationStrategy) -> bool:
        """Check if a strategy has already been used."""
        return strategy not in self._used_strategies

    def register(self, content: str, strategy: MutationStrategy):
        """Register content and strategy as used."""
        self._used_texts.append(content)
        self._used_strategies.append(strategy)
        hook = self._extract_hook(content)
        if hook:
            self._used_hooks.add(hook)
        cta = self._extract_cta(content)
        if cta:
            self._used_ctas.add(cta)

    def get_used_strategies(self) -> list[MutationStrategy]:
        """Return list of strategies already used."""
        return list(self._used_strategies)

    def get_available_strategies(self) -> list[MutationStrategy]:
        """Return strategies not yet used."""
        all_strategies = set(MutationStrategy)
        used = set(self._used_strategies)
        return list(all_strategies - used)

    def reset(self):
        """Reset all tracking state."""
        self._used_texts.clear()
        self._used_strategies.clear()
        self._used_hooks.clear()
        self._used_ctas.clear()

    # ── Similarity Computation ────────────────────────────────────────────────

    @staticmethod
    def _compute_similarity(text_a: str, text_b: str) -> float:
        """Compute similarity ratio using SequenceMatcher."""
        if not text_a or not text_b:
            return 0.0
        return SequenceMatcher(None, text_a, text_b).ratio()

    # ── Content Cleaning ──────────────────────────────────────────────────────

    @staticmethod
    def _clean(text: str) -> str:
        """
        Normalize text for fair comparison:
        - Lowercase
        - Remove emojis and special chars
        - Collapse whitespace
        """
        text = text.lower()
        # Remove emoji-like characters
        text = re.sub(
            r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]|[\uFE00-\uFE0F]|[\u2700-\u27BF]",
            "",
            text,
        )
        # Remove special formatting chars
        text = re.sub(r"[→•📖⚡✅💡🔥🔑📌🎯🚀💪📊🔄💎👉🧵]", "", text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # ── Fragment Extraction ───────────────────────────────────────────────────

    @staticmethod
    def _extract_hook(content: str) -> str:
        """Extract the opening hook (first line/sentence)."""
        lines = content.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            return first_line[:100].lower() if first_line else ""
        return ""

    @staticmethod
    def _extract_cta(content: str) -> str:
        """Extract call-to-action (last meaningful line)."""
        lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
        if lines:
            last_line = lines[-1]
            return last_line[:100].lower()
        return ""
