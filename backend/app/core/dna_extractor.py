"""
DNA Extractor – Extracts the genetic blueprint of content.
Analyzes intent, tone, emotion, keywords, platform alignment, and structure.
"""

import re
from collections import Counter
from .models import (
    DNAProfile,
    IntentType,
    ToneType,
    PlatformType,
    StructureType,
)


class DNAExtractor:
    """Extracts DNA profile from content text using heuristic analysis."""

    # ── Keyword dictionaries for classification ───────────────────────────────

    INTENT_SIGNALS: dict[IntentType, list[str]] = {
        IntentType.INFORM: ["here's", "did you know", "according to", "research shows", "data", "report", "study"],
        IntentType.PERSUADE: ["you should", "must", "don't miss", "act now", "imagine", "consider"],
        IntentType.ENTERTAIN: ["lol", "funny", "imagine", "plot twist", "wait for it", "😂", "🤣"],
        IntentType.EDUCATE: ["step", "how to", "guide", "tutorial", "learn", "explained", "breakdown"],
        IntentType.INSPIRE: ["dream", "never give up", "believe", "journey", "resilience", "overcome"],
        IntentType.SELL: ["buy", "discount", "offer", "limited", "price", "deal", "checkout", "order"],
        IntentType.ENGAGE: ["what do you think", "comment", "share", "tag", "poll", "vote", "agree?"],
    }

    TONE_SIGNALS: dict[ToneType, list[str]] = {
        ToneType.PROFESSIONAL: ["furthermore", "consequently", "in summary", "key takeaway"],
        ToneType.CASUAL: ["hey", "btw", "ngl", "tbh", "kinda", "gonna", "pretty much"],
        ToneType.AUTHORITATIVE: ["research proves", "studies confirm", "data shows", "evidence"],
        ToneType.CONVERSATIONAL: ["you know", "right?", "honestly", "look,", "here's the thing"],
        ToneType.PROVOCATIVE: ["hot take", "unpopular opinion", "controversial", "wake up"],
        ToneType.EMPATHETIC: ["i understand", "we've all been", "it's okay", "you're not alone"],
        ToneType.HUMOROUS: ["lol", "😂", "joke", "hilarious", "comedy", "meme"],
        ToneType.URGENT: ["now", "immediately", "hurry", "last chance", "deadline", "breaking"],
    }

    EMOTION_WORDS: dict[str, list[str]] = {
        "excitement": ["amazing", "incredible", "fantastic", "thrilling", "wow", "breakthrough"],
        "fear": ["danger", "risk", "warning", "threat", "crisis", "urgent"],
        "curiosity": ["secret", "hidden", "discover", "mystery", "revealed", "unlock"],
        "trust": ["proven", "reliable", "trusted", "certified", "guaranteed", "backed"],
        "empathy": ["struggle", "challenge", "understand", "support", "together", "care"],
        "anger": ["outrageous", "unacceptable", "enough", "broken", "failed", "betrayed"],
        "joy": ["celebrate", "happy", "love", "grateful", "blessed", "wonderful"],
        "neutral": [],
    }

    PLATFORM_SIGNALS: dict[PlatformType, list[str]] = {
        PlatformType.TWITTER: ["thread", "🧵", "1/", "rt", "tweet"],
        PlatformType.LINKEDIN: ["professional", "career", "industry", "leadership", "networking"],
        PlatformType.INSTAGRAM: ["link in bio", "swipe", "reel", "story", "aesthetic"],
        PlatformType.BLOG: ["article", "read more", "subscribe", "newsletter", "post"],
        PlatformType.EMAIL: ["subject", "unsubscribe", "inbox", "newsletter", "dear"],
        PlatformType.YOUTUBE: ["subscribe", "like and share", "watch", "video", "channel"],
    }

    # ── Public API ────────────────────────────────────────────────────────────

    def extract(self, content: str) -> DNAProfile:
        """Extract a full DNA profile from content text."""
        text_lower = content.lower()
        return DNAProfile(
            intent=self._classify_intent(text_lower),
            tone=self._classify_tone(text_lower),
            emotional_signal=self._detect_emotion(text_lower),
            keyword_clusters=self._extract_keywords(content),
            platform_alignment=self._detect_platform(text_lower),
            structure_type=self._detect_structure(content),
        )

    # ── Private classifiers ───────────────────────────────────────────────────

    def _classify_intent(self, text: str) -> IntentType:
        scores: dict[IntentType, int] = {}
        for intent, signals in self.INTENT_SIGNALS.items():
            scores[intent] = sum(1 for s in signals if s in text)
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        return best if scores[best] > 0 else IntentType.INFORM

    def _classify_tone(self, text: str) -> ToneType:
        scores: dict[ToneType, int] = {}
        for tone, signals in self.TONE_SIGNALS.items():
            scores[tone] = sum(1 for s in signals if s in text)
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        return best if scores[best] > 0 else ToneType.PROFESSIONAL

    def _detect_emotion(self, text: str) -> str:
        scores: dict[str, int] = {}
        for emotion, words in self.EMOTION_WORDS.items():
            scores[emotion] = sum(1 for w in words if w in text)
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        return best if scores[best] > 0 else "neutral"

    def _extract_keywords(self, content: str, top_n: int = 8) -> list[str]:
        """Extract top keywords by frequency, filtering stopwords."""
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "need", "dare", "ought",
            "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "out", "off", "over", "under", "again", "further",
            "then", "once", "and", "but", "or", "nor", "not", "so", "yet",
            "both", "either", "neither", "each", "every", "all", "any", "few",
            "more", "most", "other", "some", "such", "no", "only", "own", "same",
            "than", "too", "very", "just", "because", "if", "when", "where",
            "how", "what", "which", "who", "whom", "this", "that", "these",
            "those", "i", "me", "my", "we", "our", "you", "your", "he", "him",
            "his", "she", "her", "it", "its", "they", "them", "their",
        }
        words = re.findall(r"\b[a-zA-Z]{3,}\b", content.lower())
        filtered = [w for w in words if w not in stopwords]
        counter = Counter(filtered)
        return [word for word, _ in counter.most_common(top_n)]

    def _detect_platform(self, text: str) -> PlatformType:
        scores: dict[PlatformType, int] = {}
        for platform, signals in self.PLATFORM_SIGNALS.items():
            scores[platform] = sum(1 for s in signals if s in text)
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        return best if scores[best] > 0 else PlatformType.GENERAL

    def _detect_structure(self, content: str) -> StructureType:
        lines = content.strip().split("\n")
        numbered = sum(1 for l in lines if re.match(r"^\s*\d+[\.\)]\s", l))
        bullets = sum(1 for l in lines if re.match(r"^\s*[-•*]\s", l))
        questions = sum(1 for l in lines if "?" in l)
        word_count = len(content.split())

        if numbered >= 3 or bullets >= 3:
            return StructureType.LISTICLE
        if questions >= 2:
            return StructureType.QA
        if any(kw in content.lower() for kw in ["step", "how to", "guide"]):
            return StructureType.HOW_TO
        if word_count < 100:
            return StructureType.SHORT_FORM
        if word_count > 500:
            return StructureType.LONG_FORM
        if any(kw in content.lower() for kw in ["however", "on the other hand", "argue"]):
            return StructureType.ARGUMENTATIVE
        return StructureType.NARRATIVE
