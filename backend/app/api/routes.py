"""
API Routes for Content DNA OS.
Provides endpoints for single evolution, multi-generation lab,
DNA extraction, fitness scoring, audience simulation, feedback, and evolution history.
"""

import logging
import threading
from fastapi import APIRouter, HTTPException
from ..core.models import (
    CreateRequest,
    CreateResponse,
    EvolutionLabRequest,
    EvolutionLabResponse,
    ContentRequest,
    DNAProfile,
    FitnessScore,
    MutationStrategy,
    PlatformType,
    LanguageType,
    AudienceSimRequest,
    FeedbackRequest,
)
from ..core.evolution_manager import EvolutionManager
from ..core.dna_extractor import DNAExtractor
from ..core.fitness_scorer import FitnessScorer

logger = logging.getLogger(__name__)

router = APIRouter()

# Thread-safe factory for EvolutionManager (Step 13)
_manager_lock = threading.Lock()
_dna_extractor = DNAExtractor()
_fitness_scorer = FitnessScorer()

# Strategy feedback weights — boosted by thumbs-up, lowered by thumbs-down
_feedback_weights: dict[str, float] = {s.value: 1.0 for s in MutationStrategy}
_feedback_lock = threading.Lock()


def _new_manager() -> EvolutionManager:
    """Create a fresh EvolutionManager per request to avoid shared mutable state."""
    return EvolutionManager()


# ── Create Page (Single Evolution) ───────────────────────────────────────────

@router.post("/evolve", response_model=CreateResponse)
def evolve_single(request: CreateRequest):
    """Evolve a single content piece using one mutation strategy."""
    try:
        manager = _new_manager()
        result = manager.evolve_single(
            content=request.content,
            platform=request.platform,
            strategy=request.strategy,
            language=request.language,
        )
        return result
    except Exception as e:
        logger.exception("evolve_single failed")
        raise HTTPException(status_code=500, detail="Evolution failed. Please try again.")


# ── Evolution Lab (Multi-Generation) ─────────────────────────────────────────

@router.post("/evolve/lab", response_model=EvolutionLabResponse)
def evolve_lab(request: EvolutionLabRequest):
    """Run multi-generation evolution."""
    try:
        manager = _new_manager()
        result = manager.evolve_lab(
            content=request.content,
            platform=request.platform,
            generations=request.generations,
            strategies=request.strategies,
            language=request.language,
        )
        return result
    except Exception as e:
        logger.exception("evolve_lab failed")
        raise HTTPException(status_code=500, detail="Evolution lab failed. Please try again.")


# ── DNA Extraction ────────────────────────────────────────────────────────────

@router.post("/dna/extract", response_model=DNAProfile)
def extract_dna(request: ContentRequest):
    """Extract the DNA profile from a content piece."""
    return _dna_extractor.extract(request.content)


# ── Fitness Score ─────────────────────────────────────────────────────────────

@router.post("/fitness/score", response_model=FitnessScore)
def score_fitness(request: ContentRequest):
    """Compute the fitness score for a content piece."""
    dna = _dna_extractor.extract(request.content)
    return _fitness_scorer.score(request.content, dna)


# ── Audience Simulation (Step 6) ─────────────────────────────────────────────

@router.post("/audience/simulate")
def simulate_audience(request: AudienceSimRequest):
    """Simulate how Indian audience segments would react to content."""
    try:
        from ..aws.bedrock_client import BedrockClient
        bedrock = BedrockClient()
        if not bedrock.available:
            return _fallback_audience_sim(request.content)
        result = bedrock.simulate_audience(request.content, request.platform.value)
        if result:
            return result
        return _fallback_audience_sim(request.content)
    except Exception:
        logger.exception("audience simulation failed")
        return _fallback_audience_sim(request.content)


def _fallback_audience_sim(content: str) -> dict:
    """Rule-based audience simulation when Bedrock is unavailable."""
    word_count = len(content.split())
    has_emoji = any(ord(c) > 0x1F600 for c in content if ord(c) > 127)
    has_question = "?" in content

    segments = [
        {
            "name": "Gen Z India",
            "reaction": "Quick, visual content grabs attention. Could use more slang and relatability.",
            "engagement_score": min(85, 40 + (10 if has_emoji else 0) + (15 if word_count < 100 else 0) + (10 if has_question else 0)),
            "sample_comment": "This hits different fr fr 🔥" if has_emoji else "Needs more vibes tbh",
            "would_share": word_count < 150,
            "emoji_reaction": "🔥",
        },
        {
            "name": "Urban Professionals",
            "reaction": "Looking for actionable insights and data-driven points.",
            "engagement_score": min(85, 50 + (15 if word_count > 80 else 0) + (10 if not has_emoji else -5)),
            "sample_comment": "Great insights. Saving this for my team meeting.",
            "would_share": word_count > 80,
            "emoji_reaction": "💡",
        },
        {
            "name": "Rural Digital India",
            "reaction": "Simplicity and relatability matter most. Regional language would help.",
            "engagement_score": min(75, 35 + (10 if word_count < 120 else 0)),
            "sample_comment": "Very good information 👍",
            "would_share": True,
            "emoji_reaction": "👍",
        },
        {
            "name": "College Students",
            "reaction": "Looking for exam-relevant or career-boosting content.",
            "engagement_score": min(80, 45 + (10 if has_question else 0) + (10 if "learn" in content.lower() else 0)),
            "sample_comment": "Bhai ye toh boards ke liye bhi kaam aayega 📚",
            "would_share": has_question,
            "emoji_reaction": "📚",
        },
        {
            "name": "Business Owners",
            "reaction": "Time is money. Give me the ROI or move on.",
            "engagement_score": min(75, 40 + (15 if word_count < 200 else 0)),
            "sample_comment": "How does this translate to revenue growth?",
            "would_share": False,
            "emoji_reaction": "📊",
        },
    ]

    avg_score = sum(s["engagement_score"] for s in segments) // len(segments)
    return {
        "segments": segments,
        "overall_virality_score": avg_score,
        "best_platform": "instagram" if word_count < 100 else "linkedin",
        "improvement_tip": "Add regional language variants and cultural references for wider Bharat reach.",
    }


# ── Feedback Loop (Step 7) ───────────────────────────────────────────────────

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Submit thumbs up/down on a mutation to bias future strategy selection."""
    with _feedback_lock:
        current = _feedback_weights.get(request.strategy.value, 1.0)
        delta = 0.1 * request.rating  # +0.1 for thumbs up, -0.1 for down
        _feedback_weights[request.strategy.value] = max(0.1, min(2.0, current + delta))

    # Persist to DynamoDB if available
    try:
        manager = _new_manager()
        if manager._dynamo:
            manager._dynamo.store_evolution(
                request.content_id,
                20000 + hash(request.mutation_id) % 1000,
                {
                    "type": "feedback",
                    "mutation_id": request.mutation_id,
                    "strategy": request.strategy.value,
                    "rating": request.rating,
                },
            )
    except Exception:
        pass

    return {"status": "recorded", "weights": dict(_feedback_weights)}


@router.get("/feedback/weights")
def get_feedback_weights():
    """Get current strategy weights based on user feedback."""
    with _feedback_lock:
        return dict(_feedback_weights)


# ── Shareable Evolution (Step 8) ──────────────────────────────────────────────

@router.get("/share/{content_id}")
def get_shared_evolution(content_id: str):
    """Retrieve a shared evolution by content_id for replay."""
    manager = _new_manager()
    if not manager._dynamo:
        raise HTTPException(status_code=404, detail="Sharing unavailable in offline mode.")
    result = manager._dynamo.get_evolution(content_id)
    if not result:
        raise HTTPException(status_code=404, detail="Evolution not found.")
    return {"content_id": content_id, "evolution": result}


# ── Evolution History ─────────────────────────────────────────────────────────

@router.get("/evolutions")
def list_evolutions():
    """List recent evolution runs (from DynamoDB if available)."""
    manager = _new_manager()
    if manager._dynamo:
        return manager._dynamo.list_evolutions(limit=20)
    return []


# ── Meta ──────────────────────────────────────────────────────────────────────

@router.get("/strategies")
def list_strategies():
    """List all available mutation strategies with descriptions."""
    descriptions = {
        MutationStrategy.HOOK_AMPLIFICATION: "Amplify the opening hook into a bold, attention-grabbing lead.",
        MutationStrategy.ANGLE_SHIFT: "Shift perspective to a contrarian or alternative viewpoint.",
        MutationStrategy.STORY_REFRAME: "Restructure content as a narrative arc (setup → conflict → resolution).",
        MutationStrategy.COUNTERPOINT_INJECTION: "Inject a devil's advocate counterpoint to create depth.",
        MutationStrategy.SUMMARY_DISTILLATION: "Distill content to its essential core insight.",
        MutationStrategy.PLATFORM_FORMATTING: "Reformat for maximum platform-specific impact.",
        MutationStrategy.REGIONAL_ADAPTATION: "Adapt content for Indian audiences with cultural context.",
    }
    return [
        {"value": s.value, "name": s.name, "description": descriptions.get(s, "")}
        for s in MutationStrategy
    ]


@router.get("/platforms")
def list_platforms():
    """List all supported platform types."""
    return [{"value": p.value, "name": p.name} for p in PlatformType]


@router.get("/languages")
def list_languages():
    """List all supported languages."""
    return [{"value": l.value, "name": l.name} for l in LanguageType]
