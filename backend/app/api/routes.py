"""
API Routes for Content DNA OS.
Provides endpoints for single evolution, multi-generation lab,
DNA extraction, and fitness scoring.
"""

from fastapi import APIRouter, HTTPException
from ..core.models import (
    CreateRequest,
    CreateResponse,
    EvolutionLabRequest,
    EvolutionLabResponse,
    DNAProfile,
    FitnessScore,
    MutationStrategy,
    PlatformType,
)
from ..core.evolution_manager import EvolutionManager
from ..core.dna_extractor import DNAExtractor
from ..core.fitness_scorer import FitnessScorer

router = APIRouter()

# Shared instances
_evolution_manager = EvolutionManager()
_dna_extractor = DNAExtractor()
_fitness_scorer = FitnessScorer()


# ── Create Page (Single Evolution) ───────────────────────────────────────────

@router.post("/evolve", response_model=CreateResponse)
def evolve_single(request: CreateRequest):
    """
    Evolve a single content piece using one mutation strategy.
    Returns the evolved content, DNA profiles, fitness delta, and drift analysis.
    """
    try:
        result = _evolution_manager.evolve_single(
            content=request.content,
            platform=request.platform,
            strategy=request.strategy,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Evolution Lab (Multi-Generation) ─────────────────────────────────────────

@router.post("/evolve/lab", response_model=EvolutionLabResponse)
def evolve_lab(request: EvolutionLabRequest):
    """
    Run multi-generation evolution.
    Produces a full evolution tree with fitness tracking and DNA drift analysis.
    """
    try:
        result = _evolution_manager.evolve_lab(
            content=request.content,
            platform=request.platform,
            generations=request.generations,
            strategies=request.strategies,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── DNA Extraction ────────────────────────────────────────────────────────────

@router.post("/dna/extract", response_model=DNAProfile)
def extract_dna(content: str):
    """Extract the DNA profile from a content piece."""
    if len(content) < 10:
        raise HTTPException(status_code=400, detail="Content must be at least 10 characters")
    return _dna_extractor.extract(content)


# ── Fitness Score ─────────────────────────────────────────────────────────────

@router.post("/fitness/score", response_model=FitnessScore)
def score_fitness(content: str):
    """Compute the fitness score for a content piece."""
    if len(content) < 10:
        raise HTTPException(status_code=400, detail="Content must be at least 10 characters")
    dna = _dna_extractor.extract(content)
    return _fitness_scorer.score(content, dna)


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
    }
    return [
        {"value": s.value, "name": s.name, "description": descriptions.get(s, "")}
        for s in MutationStrategy
    ]


@router.get("/platforms")
def list_platforms():
    """List all supported platform types."""
    return [{"value": p.value, "name": p.name} for p in PlatformType]
