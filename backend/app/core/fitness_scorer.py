"""
Fitness Scorer – Multi-dimensional fitness evaluation for content mutations.
Rewards novelty, clarity, and structural diversity; penalizes repetition.
"""

from __future__ import annotations
import re
import math
from .models import (
    FitnessScore,
    FitnessDelta,
    DNAProfile,
    MutationStrategy,
)


class FitnessScorer:
    """Evaluates content fitness across multiple dimensions."""

    # ── Configuration ─────────────────────────────────────────────────────────

    IDEAL_LENGTH_MIN = 80   # words
    IDEAL_LENGTH_MAX = 500  # words

    WEIGHTS = {
        "length": 0.15,
        "structural_clarity": 0.20,
        "intent_alignment": 0.15,
        "strategy_diversity": 0.15,
        "repetition_penalty": 0.15,
        "similarity_penalty": 0.10,
        "novelty_bonus": 0.10,
    }

    # ── Public API ────────────────────────────────────────────────────────────

    def score(
        self,
        content: str,
        dna: DNAProfile,
        strategy: MutationStrategy | None = None,
        parent_content: str = "",
        used_strategies: list[MutationStrategy] | None = None,
        similarity: float = 0.0,
    ) -> FitnessScore:
        """Compute a full fitness score for a content mutation."""

        length_score = self._score_length(content)
        structural_clarity = self._score_structural_clarity(content)
        intent_alignment = self._score_intent_alignment(content, dna)
        strategy_diversity = self._score_strategy_diversity(strategy, used_strategies or [])
        repetition_penalty = self._score_repetition_penalty(content)
        similarity_penalty = self._score_similarity_penalty(similarity)
        novelty_bonus = self._score_novelty(content, parent_content)

        total = (
            self.WEIGHTS["length"] * length_score
            + self.WEIGHTS["structural_clarity"] * structural_clarity
            + self.WEIGHTS["intent_alignment"] * intent_alignment
            + self.WEIGHTS["strategy_diversity"] * strategy_diversity
            - self.WEIGHTS["repetition_penalty"] * repetition_penalty
            - self.WEIGHTS["similarity_penalty"] * similarity_penalty
            + self.WEIGHTS["novelty_bonus"] * novelty_bonus
        )

        # Clamp to [0, 1]
        total = max(0.0, min(1.0, total))

        return FitnessScore(
            total=round(total, 4),
            length_score=round(length_score, 4),
            structural_clarity=round(structural_clarity, 4),
            intent_alignment=round(intent_alignment, 4),
            strategy_diversity=round(strategy_diversity, 4),
            repetition_penalty=round(repetition_penalty, 4),
            similarity_penalty=round(similarity_penalty, 4),
            novelty_bonus=round(novelty_bonus, 4),
        )

    def compute_delta(self, parent_fitness: float, child_fitness: float) -> FitnessDelta:
        """Compute the fitness delta between parent and child."""
        delta = child_fitness - parent_fitness
        return FitnessDelta(
            parent_fitness=round(parent_fitness, 4),
            child_fitness=round(child_fitness, 4),
            delta=round(delta, 4),
            improved=delta > 0,
        )

    # ── Dimension Scorers ─────────────────────────────────────────────────────

    def _score_length(self, content: str) -> float:
        """Score based on ideal content length range."""
        word_count = len(content.split())
        if self.IDEAL_LENGTH_MIN <= word_count <= self.IDEAL_LENGTH_MAX:
            return 1.0
        if word_count < self.IDEAL_LENGTH_MIN:
            return word_count / self.IDEAL_LENGTH_MIN
        # Gradually decay for overly long content
        overflow = word_count - self.IDEAL_LENGTH_MAX
        return max(0.0, 1.0 - (overflow / self.IDEAL_LENGTH_MAX))

    def _score_structural_clarity(self, content: str) -> float:
        """Score structural clarity based on formatting signals."""
        score = 0.0
        lines = content.strip().split("\n")

        # Paragraph breaks improve readability
        paragraph_count = len([l for l in lines if l.strip() == ""])
        score += min(0.3, paragraph_count * 0.05)

        # Headers / section markers
        headers = sum(1 for l in lines if l.strip().startswith(("#", "📖", "⚡", "✅", "💡", "🔥", "→")))
        score += min(0.3, headers * 0.1)

        # Sentence length variance (mix of short and long = good)
        sentences = re.split(r"[.!?]+", content)
        if len(sentences) > 1:
            lengths = [len(s.split()) for s in sentences if s.strip()]
            if lengths:
                avg_len = sum(lengths) / len(lengths)
                variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
                # Moderate variance is ideal
                score += min(0.4, math.sqrt(variance) / 20)

        return min(1.0, score)

    def _score_intent_alignment(self, content: str, dna: DNAProfile) -> float:
        """Score how well the content aligns with its detected intent."""
        # Simple heuristic: check for intent-appropriate signals
        intent_keywords = {
            "inform": ["here's", "according", "data", "shows"],
            "persuade": ["you should", "must", "imagine"],
            "educate": ["step", "how", "guide", "learn"],
            "inspire": ["dream", "believe", "never give up"],
            "sell": ["buy", "offer", "deal", "get"],
            "engage": ["think", "comment", "share", "agree"],
            "entertain": ["funny", "imagine", "plot twist"],
        }
        keywords = intent_keywords.get(dna.intent.value, [])
        if not keywords:
            return 0.5
        matches = sum(1 for kw in keywords if kw in content.lower())
        return min(1.0, matches / max(1, len(keywords)))

    def _score_strategy_diversity(
        self, strategy: MutationStrategy | None, used: list[MutationStrategy]
    ) -> float:
        """Reward using a strategy that hasn't been used before."""
        if strategy is None:
            return 0.5
        if strategy not in used:
            return 1.0
        # Penalize reuse proportional to how many times it's been used
        count = used.count(strategy)
        return max(0.0, 1.0 - (count * 0.3))

    def _score_repetition_penalty(self, content: str) -> float:
        """Detect and penalize internal repetition."""
        words = content.lower().split()
        if len(words) < 10:
            return 0.0

        # Check for repeated phrases (trigrams)
        trigrams = [" ".join(words[i : i + 3]) for i in range(len(words) - 2)]
        unique_trigrams = set(trigrams)
        if not trigrams:
            return 0.0
        repetition_ratio = 1 - (len(unique_trigrams) / len(trigrams))
        return min(1.0, repetition_ratio * 3)  # Scale up for sensitivity

    def _score_similarity_penalty(self, similarity: float) -> float:
        """Penalize based on similarity to parent content."""
        # Higher similarity → higher penalty
        return max(0.0, similarity)

    def _score_novelty(self, content: str, parent_content: str) -> float:
        """Reward novel vocabulary and structures compared to parent."""
        if not parent_content:
            return 0.5

        parent_words = set(parent_content.lower().split())
        child_words = set(content.lower().split())

        if not child_words:
            return 0.0

        new_words = child_words - parent_words
        novelty_ratio = len(new_words) / len(child_words)
        return min(1.0, novelty_ratio * 2)  # Boost novelty signal
