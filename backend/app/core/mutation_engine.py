"""
Mutation Engine – Applies structural transformation strategies to content.
Each strategy produces a meaningfully different variant, not just a paraphrase.
Uses Amazon Bedrock (Claude 3) when available, with rule-based fallback.
"""

from __future__ import annotations
import re
import random
import logging
from .models import MutationStrategy

logger = logging.getLogger(__name__)


class MutationEngine:
    """
    Generates content mutations using six distinct strategies.
    Uses Claude 3 via Amazon Bedrock for AI-powered mutations.
    Falls back to rule-based templates when Bedrock is unavailable.
    """

    def __init__(self):
        self._bedrock = None
        try:
            from ..aws.bedrock_client import BedrockClient
            self._bedrock = BedrockClient()
            if self._bedrock.available:
                logger.info("MutationEngine: Bedrock (Claude 3) available — AI mutations enabled")
            else:
                logger.info("MutationEngine: Bedrock unavailable — using rule-based fallback")
                self._bedrock = None
        except Exception as e:
            logger.warning(f"MutationEngine: Could not init Bedrock: {e}")
            self._bedrock = None

    def mutate(self, content: str, strategy: MutationStrategy, platform: str = "general") -> str:
        """Apply a mutation strategy. Tries Bedrock first, falls back to templates."""
        # Try AI-powered mutation via Bedrock
        if self._bedrock and self._bedrock.available:
            ai_result = self._bedrock.generate_mutation(
                content=content,
                strategy=strategy.value,
                platform=platform,
            )
            if ai_result and len(ai_result.strip()) > 20:
                logger.info(f"Bedrock mutation succeeded for strategy={strategy.value}")
                return ai_result.strip()
            logger.warning(f"Bedrock returned empty/short result for {strategy.value}, using fallback")

        # Fallback: rule-based mutation
        return self._mutate_rule_based(content, strategy)

    def _mutate_rule_based(self, content: str, strategy: MutationStrategy) -> str:
        """Rule-based fallback mutation."""
        handlers = {
            MutationStrategy.HOOK_AMPLIFICATION: self._hook_amplification,
            MutationStrategy.ANGLE_SHIFT: self._angle_shift,
            MutationStrategy.STORY_REFRAME: self._story_reframe,
            MutationStrategy.COUNTERPOINT_INJECTION: self._counterpoint_injection,
            MutationStrategy.SUMMARY_DISTILLATION: self._summary_distillation,
            MutationStrategy.PLATFORM_FORMATTING: self._platform_formatting,
        }
        handler = handlers.get(strategy)
        if handler is None:
            raise ValueError(f"Unknown strategy: {strategy}")
        return handler(content)

    # ── Strategy Implementations ──────────────────────────────────────────────

    def _hook_amplification(self, content: str) -> str:
        """
        Amplify the opening hook — restructure the first sentence
        into a bold, attention-grabbing lead.
        """
        sentences = self._split_sentences(content)
        if not sentences:
            return content

        first = sentences[0].strip()
        rest = " ".join(sentences[1:])

        hook_templates = [
            f"🔥 Here's what nobody tells you: {first}",
            f"Stop scrolling. {first} — and here's why it matters.",
            f"What if I told you this changes everything? {first}",
            f"⚡ The truth is brutal: {first}",
            f"Most people get this wrong. {first}",
            f"Read this twice: {first}",
        ]
        new_hook = random.choice(hook_templates)
        return f"{new_hook}\n\n{rest}".strip()

    def _angle_shift(self, content: str) -> str:
        """
        Shift the perspective angle — reframe from a different
        stakeholder viewpoint or contrarian lens.
        """
        shifts = [
            (
                "Let's flip this around. From a completely different angle:\n\n",
                "\n\nThis perspective changes the entire conversation.",
            ),
            (
                "Here's the insider view most people never see:\n\n",
                "\n\nWhen you see it from this angle, the implications are massive.",
            ),
            (
                "What if we looked at this through the eyes of a skeptic?\n\n",
                "\n\nSkepticism reveals what optimism hides.",
            ),
            (
                "Consider the opposite take:\n\n",
                "\n\nSometimes the contrarian view holds the real insight.",
            ),
        ]
        prefix, suffix = random.choice(shifts)

        # Restructure: move the conclusion to the beginning for angle shift
        sentences = self._split_sentences(content)
        if len(sentences) > 3:
            # Put the last third first
            pivot = len(sentences) // 3
            reordered = sentences[-pivot:] + sentences[:-pivot]
            body = " ".join(reordered)
        else:
            body = content

        return f"{prefix}{body}{suffix}"

    def _story_reframe(self, content: str) -> str:
        """
        Reframe the content as a narrative or story structure
        with setup → conflict → resolution arc.
        """
        sentences = self._split_sentences(content)
        if len(sentences) < 3:
            return f"📖 Let me tell you a story.\n\n{content}\n\nAnd that changed everything."

        third = max(len(sentences) // 3, 1)
        setup = " ".join(sentences[:third])
        conflict = " ".join(sentences[third : 2 * third])
        resolution = " ".join(sentences[2 * third :])

        return (
            f"📖 THE SETUP:\n{setup}\n\n"
            f"⚡ THE CONFLICT:\n{conflict}\n\n"
            f"✅ THE RESOLUTION:\n{resolution}"
        )

    def _counterpoint_injection(self, content: str) -> str:
        """
        Inject a counterpoint or devil's advocate position
        into the content to create tension and depth.
        """
        counterpoints = [
            "But here's the counterargument nobody wants to address:",
            "Devil's advocate: what if the opposite is true?",
            "Critics would say this misses the bigger picture:",
            "The uncomfortable truth that challenges this view:",
            "However, there's a side to this that deserves scrutiny:",
        ]
        responses = [
            "And yet — the original point still stands because the evidence is overwhelming.",
            "Despite this tension, the data points in one clear direction.",
            "This counterpoint actually strengthens the original argument when examined closely.",
            "Acknowledging this challenge makes the core thesis even more robust.",
        ]

        sentences = self._split_sentences(content)
        if len(sentences) < 2:
            return f"{content}\n\n{random.choice(counterpoints)}\n\n{random.choice(responses)}"

        mid = len(sentences) // 2
        first_half = " ".join(sentences[:mid])
        second_half = " ".join(sentences[mid:])

        return (
            f"{first_half}\n\n"
            f"🔄 {random.choice(counterpoints)}\n\n"
            f"{second_half}\n\n"
            f"💡 {random.choice(responses)}"
        )

    def _summary_distillation(self, content: str) -> str:
        """
        Distill the content into its essential points —
        strip fluff, extract core insight, compress.
        """
        sentences = self._split_sentences(content)
        if len(sentences) <= 2:
            return f"💎 Core insight: {content}"

        # Take the most information-dense sentences (heuristic: longer = denser)
        scored = [(s, len(s.split())) for s in sentences]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Take top 40% of sentences
        top_count = max(2, int(len(scored) * 0.4))
        top_sentences = [s for s, _ in scored[:top_count]]

        # Restore original order
        ordered = [s for s in sentences if s in top_sentences]

        key_points = "\n".join(f"→ {s.strip()}" for s in ordered)
        return f"💎 DISTILLED INSIGHT:\n\n{key_points}\n\n⚡ That's the signal. Everything else is noise."

    def _platform_formatting(self, content: str) -> str:
        """
        Reformat content for maximum platform impact —
        short paragraphs, line breaks, emoji anchors, scanability.
        """
        sentences = self._split_sentences(content)
        if not sentences:
            return content

        emojis = ["💡", "🔑", "📌", "⚡", "🎯", "✅", "🚀", "💪", "🔥", "📊"]
        formatted_parts = []

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            emoji = emojis[i % len(emojis)]
            formatted_parts.append(f"{emoji} {sentence}")

        return "\n\n".join(formatted_parts) + "\n\n👉 Save this. Share this. Apply this."

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s for s in sentences if s.strip()]

    @staticmethod
    def available_strategies() -> list[MutationStrategy]:
        """Return all available mutation strategies."""
        return list(MutationStrategy)
