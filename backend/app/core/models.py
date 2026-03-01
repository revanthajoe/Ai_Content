"""
Pydantic models for Content DNA OS.
Defines the data structures for DNA profiles, mutations, fitness scores, and evolution trees.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid
import datetime


# ── Enums ──────────────────────────────────────────────────────────────────────

class MutationStrategy(str, Enum):
    HOOK_AMPLIFICATION = "hook_amplification"
    ANGLE_SHIFT = "angle_shift"
    STORY_REFRAME = "story_reframe"
    COUNTERPOINT_INJECTION = "counterpoint_injection"
    SUMMARY_DISTILLATION = "summary_distillation"
    PLATFORM_FORMATTING = "platform_formatting"


class IntentType(str, Enum):
    INFORM = "inform"
    PERSUADE = "persuade"
    ENTERTAIN = "entertain"
    EDUCATE = "educate"
    INSPIRE = "inspire"
    SELL = "sell"
    ENGAGE = "engage"


class ToneType(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    PROVOCATIVE = "provocative"
    EMPATHETIC = "empathetic"
    HUMOROUS = "humorous"
    URGENT = "urgent"


class PlatformType(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    BLOG = "blog"
    EMAIL = "email"
    YOUTUBE = "youtube"
    GENERAL = "general"


class StructureType(str, Enum):
    LISTICLE = "listicle"
    NARRATIVE = "narrative"
    ARGUMENTATIVE = "argumentative"
    HOW_TO = "how_to"
    QA = "qa"
    THREAD = "thread"
    SHORT_FORM = "short_form"
    LONG_FORM = "long_form"


# ── DNA Profile ────────────────────────────────────────────────────────────────

class DNAProfile(BaseModel):
    """The genetic blueprint of a content piece."""
    intent: IntentType = IntentType.INFORM
    tone: ToneType = ToneType.PROFESSIONAL
    emotional_signal: str = "neutral"
    keyword_clusters: list[str] = Field(default_factory=list)
    platform_alignment: PlatformType = PlatformType.GENERAL
    structure_type: StructureType = StructureType.NARRATIVE


class DNADrift(BaseModel):
    """Tracks what changed between two DNA profiles."""
    field: str
    old_value: str
    new_value: str
    impact: str = ""  # explanation of why this drift matters


# ── Fitness ────────────────────────────────────────────────────────────────────

class FitnessScore(BaseModel):
    """Multi-dimensional fitness evaluation."""
    total: float = 0.0
    length_score: float = 0.0
    structural_clarity: float = 0.0
    intent_alignment: float = 0.0
    strategy_diversity: float = 0.0
    repetition_penalty: float = 0.0
    similarity_penalty: float = 0.0
    novelty_bonus: float = 0.0


class FitnessDelta(BaseModel):
    """Fitness change between parent and child."""
    parent_fitness: float = 0.0
    child_fitness: float = 0.0
    delta: float = 0.0
    improved: bool = False


# ── Mutation ───────────────────────────────────────────────────────────────────

class MutationResult(BaseModel):
    """Result of a single mutation operation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    strategy: MutationStrategy
    content: str
    dna: DNAProfile
    fitness: FitnessScore
    similarity_to_parent: float = 0.0
    accepted: bool = True
    rejection_reason: str = ""
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


# ── Evolution Tree ─────────────────────────────────────────────────────────────

class EvolutionNode(BaseModel):
    """A node in the evolution tree."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    generation: int = 0
    content: str
    strategy: Optional[MutationStrategy] = None
    dna: DNAProfile
    fitness: FitnessScore
    parent_id: Optional[str] = None
    children: list[EvolutionNode] = Field(default_factory=list)
    is_winner: bool = False
    dna_drift: list[DNADrift] = Field(default_factory=list)
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


class EvolutionTree(BaseModel):
    """Complete evolution lineage."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    root: EvolutionNode
    total_generations: int = 0
    total_mutations: int = 0
    total_rejected: int = 0
    winning_strategy: Optional[MutationStrategy] = None
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


# ── API Request/Response Models ────────────────────────────────────────────────

class CreateRequest(BaseModel):
    """Request to create/evolve a single content piece."""
    content: str = Field(..., min_length=10, max_length=10000)
    platform: PlatformType = PlatformType.GENERAL
    strategy: Optional[MutationStrategy] = None


class CreateResponse(BaseModel):
    """Response for single content evolution."""
    original: str
    evolved: MutationResult
    dna_original: DNAProfile
    dna_evolved: DNAProfile
    fitness_delta: FitnessDelta
    dna_drift: list[DNADrift]


class EvolutionLabRequest(BaseModel):
    """Request for multi-generation evolution."""
    content: str = Field(..., min_length=10, max_length=10000)
    platform: PlatformType = PlatformType.GENERAL
    generations: int = Field(default=3, ge=1, le=10)
    strategies: Optional[list[MutationStrategy]] = None


class EvolutionLabResponse(BaseModel):
    """Response for multi-generation evolution."""
    tree: EvolutionTree
    winner: EvolutionNode
    all_mutations: list[MutationResult]
    rejected_mutations: list[MutationResult]
    generation_fitness: list[dict]


class ContentRequest(BaseModel):
    """Simple request body containing content text."""
    content: str = Field(..., min_length=10, max_length=10000)
