"""
Tests for Content DNA OS — covers DNAExtractor, FitnessScorer, MutationEngine, SimilarityGuard, and models.
"""

import pytest
from app.core.models import (
    DNAProfile,
    MutationStrategy,
    IntentType,
    ToneType,
    PlatformType,
    StructureType,
    FitnessScore,
    FitnessDelta,
    MutationResult,
    EvolutionNode,
    EvolutionTree,
    CreateRequest,
    EvolutionLabRequest,
    LanguageType,
    AudienceSimRequest,
    FeedbackRequest,
    ContentRequest,
)
from app.core.dna_extractor import DNAExtractor
from app.core.fitness_scorer import FitnessScorer
from app.core.similarity_guard import SimilarityGuard


# ─── DNAExtractor Tests ───────────────────────────────────────────────────────

class TestDNAExtractor:
    def setup_method(self):
        self.extractor = DNAExtractor()

    def test_extract_returns_dna_profile(self):
        dna = self.extractor.extract("Here's an amazing guide on how to learn Python step by step.")
        assert isinstance(dna, DNAProfile)

    def test_intent_inform(self):
        dna = self.extractor.extract("According to research, data shows that this report is significant.")
        assert dna.intent == IntentType.INFORM

    def test_intent_educate(self):
        dna = self.extractor.extract("Step by step guide: how to learn machine learning. Tutorial breakdown explained.")
        assert dna.intent == IntentType.EDUCATE

    def test_intent_persuade(self):
        dna = self.extractor.extract("You should consider this now. Don't miss out. Imagine the possibilities. You must act now.")
        assert dna.intent == IntentType.PERSUADE

    def test_tone_casual(self):
        dna = self.extractor.extract("Hey btw ngl this is kinda cool, gonna try it out pretty much right now tbh.")
        assert dna.tone == ToneType.CASUAL

    def test_tone_authoritative(self):
        dna = self.extractor.extract("Research proves that studies confirm the data shows clear evidence of impact.")
        assert dna.tone == ToneType.AUTHORITATIVE

    def test_emotion_excitement(self):
        dna = self.extractor.extract("This is amazing and incredible, a fantastic breakthrough that is wow!")
        assert dna.emotional_signal == "excitement"

    def test_emotion_neutral_for_plain_text(self):
        dna = self.extractor.extract("The quick brown fox jumped over the lazy dog near the river bank.")
        assert dna.emotional_signal == "neutral"

    def test_keywords_extracted(self):
        dna = self.extractor.extract("Python Python Python machine learning data science AI artificial intelligence deep learning")
        assert len(dna.keyword_clusters) > 0
        assert "python" in [k.lower() for k in dna.keyword_clusters]

    def test_platform_twitter(self):
        dna = self.extractor.extract("New thread 🧵 1/ Here's my tweet about this topic. RT if you agree.")
        assert dna.platform_alignment == PlatformType.TWITTER

    def test_platform_linkedin(self):
        dna = self.extractor.extract("Professional leadership in the industry requires career networking and growth.")
        assert dna.platform_alignment == PlatformType.LINKEDIN

    def test_structure_detection(self):
        dna = self.extractor.extract("Here's a normal piece of content, nothing special about the structure.")
        assert isinstance(dna.structure_type, StructureType)


# ─── FitnessScorer Tests ──────────────────────────────────────────────────────

class TestFitnessScorer:
    def setup_method(self):
        self.scorer = FitnessScorer()
        self.sample_dna = DNAProfile(intent=IntentType.INFORM, tone=ToneType.PROFESSIONAL)

    def test_score_returns_fitness_score(self):
        text = "This is a well-structured piece of content. " * 20
        score = self.scorer.score(text, self.sample_dna)
        assert isinstance(score, FitnessScore)
        assert 0.0 <= score.total <= 1.0

    def test_score_total_bounded(self):
        score = self.scorer.score("Short.", self.sample_dna)
        assert 0.0 <= score.total <= 1.0

    def test_length_score_ideal_range(self):
        ideal_text = " ".join(["word"] * 200)
        score = self.scorer.score(ideal_text, self.sample_dna)
        assert score.length_score == 1.0

    def test_length_score_short_penalized(self):
        short_text = "Just five words here today."
        score = self.scorer.score(short_text, self.sample_dna)
        assert score.length_score < 1.0

    def test_fitness_delta_improved(self):
        delta = self.scorer.compute_delta(0.4, 0.7)
        assert isinstance(delta, FitnessDelta)
        assert delta.improved is True
        assert delta.delta == pytest.approx(0.3, abs=0.01)

    def test_fitness_delta_declined(self):
        delta = self.scorer.compute_delta(0.8, 0.5)
        assert delta.improved is False
        assert delta.delta < 0

    def test_strategy_diversity_new_strategy(self):
        score = self.scorer.score(
            " ".join(["content"] * 100),
            self.sample_dna,
            strategy=MutationStrategy.HOOK_AMPLIFICATION,
            used_strategies=[MutationStrategy.ANGLE_SHIFT],
        )
        assert score.strategy_diversity > 0.0

    def test_novelty_bonus_different_content(self):
        parent = "The original content about cats and dogs living together."
        child = "A completely different article about quantum physics and space exploration."
        score = self.scorer.score(child, self.sample_dna, parent_content=parent)
        assert score.novelty_bonus > 0.0


# ─── SimilarityGuard Tests ────────────────────────────────────────────────────

class TestSimilarityGuard:
    def setup_method(self):
        self.guard = SimilarityGuard()

    def test_identical_rejected(self):
        text = "This is a complete piece of content about technology and innovation in modern society."
        accepted, sim, reason = self.guard.check(text, text)
        assert not accepted
        assert sim >= 0.65

    def test_different_accepted(self):
        parent = "Exploring the depths of ocean life and marine biology research."
        child = "A critical analysis of modern architecture trends in urban planning design."
        accepted, sim, reason = self.guard.check(child, parent)
        assert accepted
        assert sim < 0.65

    def test_register_and_track(self):
        self.guard.register("First piece of unique content about programming languages.", strategy=MutationStrategy.HOOK_AMPLIFICATION)
        self.guard.register("Second piece about cooking recipes and kitchen tips.", strategy=MutationStrategy.ANGLE_SHIFT)
        assert len(self.guard._used_texts) == 2

    def test_strategy_reuse_check(self):
        self.guard.register("Content text.", strategy=MutationStrategy.HOOK_AMPLIFICATION)
        assert MutationStrategy.HOOK_AMPLIFICATION in self.guard._used_strategies

    def test_similarity_score_range(self):
        _, sim, _ = self.guard.check("Hello world", "Goodbye moon")
        assert 0.0 <= sim <= 1.0


# ─── Model Validation Tests ───────────────────────────────────────────────────

class TestModels:
    def test_create_request_too_short(self):
        with pytest.raises(Exception):
            CreateRequest(content="short")

    def test_create_request_valid(self):
        req = CreateRequest(content="This is a valid request with enough characters for testing.")
        assert req.platform == PlatformType.GENERAL
        assert req.language == LanguageType.ENGLISH

    def test_language_type_values(self):
        assert len(LanguageType) == 8
        assert LanguageType.HINDI.value == "hindi"
        assert LanguageType.TAMIL.value == "tamil"

    def test_mutation_strategy_includes_regional(self):
        assert MutationStrategy.REGIONAL_ADAPTATION.value == "regional_adaptation"
        assert len(MutationStrategy) == 7

    def test_evolution_lab_request_defaults(self):
        req = EvolutionLabRequest(content="A valid seed content for evolution lab testing purposes.")
        assert req.generations == 3
        assert req.language == LanguageType.ENGLISH

    def test_audience_sim_request(self):
        req = AudienceSimRequest(content="Test content for audience simulation that is long enough.")
        assert req.platform == PlatformType.GENERAL

    def test_feedback_request_valid(self):
        req = FeedbackRequest(content_id="abc", mutation_id="xyz", strategy=MutationStrategy.HOOK_AMPLIFICATION, rating=1)
        assert req.rating == 1

    def test_feedback_request_invalid_rating(self):
        with pytest.raises(Exception):
            FeedbackRequest(content_id="abc", mutation_id="xyz", strategy=MutationStrategy.HOOK_AMPLIFICATION, rating=5)

    def test_dna_profile_defaults(self):
        dna = DNAProfile()
        assert dna.intent == IntentType.INFORM
        assert dna.tone == ToneType.PROFESSIONAL
        assert dna.emotional_signal == "neutral"

    def test_fitness_score_defaults(self):
        fs = FitnessScore()
        assert fs.total == 0.0

    def test_mutation_result_generates_id(self):
        mr = MutationResult(strategy=MutationStrategy.ANGLE_SHIFT, content="test", dna=DNAProfile(), fitness=FitnessScore())
        assert len(mr.id) == 8

    def test_content_request_min_length(self):
        with pytest.raises(Exception):
            ContentRequest(content="tiny")


# ─── MutationEngine Fallback Tests ────────────────────────────────────────────

class TestMutationEngineFallback:
    """Test rule-based fallback mutations (no Bedrock needed)."""

    def setup_method(self):
        from app.core.mutation_engine import MutationEngine
        self.engine = MutationEngine()
        self.engine._bedrock = None  # Force fallback
        self.sample = (
            "Content creation is evolving rapidly. Many tools now use AI to help writers. "
            "The landscape is changing faster than ever. New strategies emerge daily. "
            "Understanding these shifts is crucial for success in the digital age."
        )

    def test_hook_amplification_modifies(self):
        result = self.engine._mutate_rule_based(self.sample, MutationStrategy.HOOK_AMPLIFICATION)
        assert result != self.sample
        assert len(result) > 20

    def test_angle_shift_modifies(self):
        result = self.engine._mutate_rule_based(self.sample, MutationStrategy.ANGLE_SHIFT)
        assert result != self.sample

    def test_story_reframe_modifies(self):
        result = self.engine._mutate_rule_based(self.sample, MutationStrategy.STORY_REFRAME)
        assert result != self.sample

    def test_counterpoint_injection_modifies(self):
        result = self.engine._mutate_rule_based(self.sample, MutationStrategy.COUNTERPOINT_INJECTION)
        assert result != self.sample

    def test_summary_distillation_modifies(self):
        result = self.engine._mutate_rule_based(self.sample, MutationStrategy.SUMMARY_DISTILLATION)
        assert result != self.sample

    def test_platform_formatting_modifies(self):
        result = self.engine._mutate_rule_based(self.sample, MutationStrategy.PLATFORM_FORMATTING)
        assert result != self.sample

    def test_regional_adaptation_modifies(self):
        result = self.engine._mutate_rule_based(self.sample, MutationStrategy.REGIONAL_ADAPTATION)
        assert result != self.sample
        # Should contain Indian cultural framing elements
        assert any(word in result.lower() for word in ["india", "bharat", "desi", "yaar", "🇮🇳", "namaste", "desh"])

    def test_mutate_method_uses_fallback(self):
        result = self.engine.mutate(self.sample, MutationStrategy.HOOK_AMPLIFICATION)
        assert result != self.sample
        assert len(result) > 20
