"""
Evolution Manager – Orchestrates the full evolutionary pipeline.
Coordinates DNA extraction, mutation, fitness scoring, similarity checking,
evolution tree construction, and DynamoDB persistence.
"""

from __future__ import annotations
import random
import hashlib
import logging
from .models import (
    MutationStrategy,
    MutationResult,
    EvolutionNode,
    EvolutionTree,
    FitnessScore,
    FitnessDelta,
    DNADrift,
    DNAProfile,
    CreateResponse,
    EvolutionLabResponse,
    PlatformType,
)
from .dna_extractor import DNAExtractor
from .mutation_engine import MutationEngine
from .fitness_scorer import FitnessScorer
from .similarity_guard import SimilarityGuard

logger = logging.getLogger(__name__)


def _content_id(content: str) -> str:
    """Generate a short deterministic ID from content."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


class EvolutionManager:
    """
    Top-level orchestrator for the Content DNA OS.
    Manages single-step evolution (Create) and multi-generation evolution (Lab).
    Persists results to DynamoDB when available.
    """

    MAX_RETRY_PER_STRATEGY = 3

    def __init__(self):
        self.dna_extractor = DNAExtractor()
        self.mutation_engine = MutationEngine()
        self.fitness_scorer = FitnessScorer()
        self.similarity_guard = SimilarityGuard()
        self._dynamo = None
        try:
            from ..aws.dynamo_client import DynamoClient
            self._dynamo = DynamoClient()
            if not self._dynamo.available:
                logger.info("EvolutionManager: DynamoDB unavailable — results will not persist")
                self._dynamo = None
            else:
                logger.info("EvolutionManager: DynamoDB connected — persistence enabled")
        except Exception as e:
            logger.warning(f"EvolutionManager: Could not init DynamoDB: {e}")
            self._dynamo = None

    # ── Single Evolution (Create Page) ────────────────────────────────────────

    def evolve_single(
        self,
        content: str,
        platform: PlatformType = PlatformType.GENERAL,
        strategy: MutationStrategy | None = None,
    ) -> CreateResponse:
        """
        Perform a single evolution step:
        1. Extract original DNA
        2. Pick a strategy (or use the provided one)
        3. Mutate
        4. Score fitness
        5. Check similarity
        6. Return result with DNA drift
        """
        self.similarity_guard.reset()

        # Extract original DNA
        dna_original = self.dna_extractor.extract(content)
        original_fitness = self.fitness_scorer.score(content, dna_original)

        # Pick strategy
        if strategy is None:
            strategy = random.choice(self.mutation_engine.available_strategies())

        # Mutate
        mutated_content = self.mutation_engine.mutate(content, strategy, platform=platform.value)

        # Check similarity
        accepted, similarity, reason = self.similarity_guard.check(mutated_content, content)

        # Extract evolved DNA
        dna_evolved = self.dna_extractor.extract(mutated_content)

        # Score fitness
        evolved_fitness = self.fitness_scorer.score(
            mutated_content,
            dna_evolved,
            strategy=strategy,
            parent_content=content,
            similarity=similarity,
        )

        # Build mutation result
        mutation = MutationResult(
            strategy=strategy,
            content=mutated_content,
            dna=dna_evolved,
            fitness=evolved_fitness,
            similarity_to_parent=round(similarity, 4),
            accepted=accepted,
            rejection_reason=reason,
        )

        # Calculate drift
        drift = self._compute_drift(dna_original, dna_evolved)

        # Fitness delta
        delta = self.fitness_scorer.compute_delta(
            original_fitness.total, evolved_fitness.total
        )

        result = CreateResponse(
            original=content,
            evolved=mutation,
            dna_original=dna_original,
            dna_evolved=dna_evolved,
            fitness_delta=delta,
            dna_drift=drift,
        )

        # Persist to DynamoDB
        self._persist_single(content, result)

        return result

    # ── Multi-Generation Evolution (Evolution Lab) ────────────────────────────

    def evolve_lab(
        self,
        content: str,
        platform: PlatformType = PlatformType.GENERAL,
        generations: int = 3,
        strategies: list[MutationStrategy] | None = None,
    ) -> EvolutionLabResponse:
        """
        Run multi-generation evolution:
        1. Create root node from original content
        2. For each generation, apply ALL available strategies
        3. Score, filter via similarity guard
        4. Select winner per generation
        5. Feed winner into next generation
        6. Build complete evolution tree
        """
        self.similarity_guard.reset()

        # Build root node
        root_dna = self.dna_extractor.extract(content)
        root_fitness = self.fitness_scorer.score(content, root_dna)

        root = EvolutionNode(
            generation=0,
            content=content,
            strategy=None,
            dna=root_dna,
            fitness=root_fitness,
        )

        all_mutations: list[MutationResult] = []
        rejected_mutations: list[MutationResult] = []
        generation_fitness: list[dict] = [
            {"generation": 0, "best_fitness": root_fitness.total, "strategy": None}
        ]

        current_parent = root
        current_content = content

        # Determine strategy pool
        if strategies:
            strategy_pool = list(strategies)
        else:
            strategy_pool = list(MutationStrategy)

        total_mutations = 0
        total_rejected = 0

        for gen in range(1, generations + 1):
            gen_candidates: list[tuple[MutationResult, EvolutionNode]] = []

            # Try each strategy
            available = [s for s in strategy_pool if self.similarity_guard.check_strategy(s)]
            if not available:
                # Reset strategy tracking if all used, allow re-use with penalty
                available = list(strategy_pool)

            for strategy in available:
                mutation_result = self._attempt_mutation(
                    current_content, strategy, gen, current_parent.id, platform
                )
                total_mutations += 1

                if mutation_result.accepted:
                    # Build evolution node
                    node = EvolutionNode(
                        generation=gen,
                        content=mutation_result.content,
                        strategy=strategy,
                        dna=mutation_result.dna,
                        fitness=mutation_result.fitness,
                        parent_id=current_parent.id,
                        dna_drift=self._compute_drift(current_parent.dna, mutation_result.dna),
                    )
                    gen_candidates.append((mutation_result, node))
                    all_mutations.append(mutation_result)
                else:
                    rejected_mutations.append(mutation_result)
                    total_rejected += 1

            # Select generation winner
            if gen_candidates:
                # Sort by fitness (descending)
                gen_candidates.sort(key=lambda x: x[0].fitness.total, reverse=True)
                winner_mutation, winner_node = gen_candidates[0]
                winner_node.is_winner = True

                # Add all candidates as children of current parent
                for _, node in gen_candidates:
                    current_parent.children.append(node)

                # Register winner and advance
                self.similarity_guard.register(winner_mutation.content, winner_mutation.strategy)
                current_parent = winner_node
                current_content = winner_mutation.content

                generation_fitness.append({
                    "generation": gen,
                    "best_fitness": winner_mutation.fitness.total,
                    "strategy": winner_mutation.strategy.value,
                    "candidates": len(gen_candidates),
                    "rejected": total_rejected,
                })
            else:
                generation_fitness.append({
                    "generation": gen,
                    "best_fitness": current_parent.fitness.total,
                    "strategy": None,
                    "candidates": 0,
                    "rejected": total_rejected,
                    "note": "No viable mutations — all rejected by similarity guard",
                })

        # Find overall winner (deepest generation winner)
        winner = self._find_winner(root)

        # Build tree
        tree = EvolutionTree(
            root=root,
            total_generations=generations,
            total_mutations=total_mutations,
            total_rejected=total_rejected,
            winning_strategy=winner.strategy if winner else None,
        )

        result = EvolutionLabResponse(
            tree=tree,
            winner=winner or root,
            all_mutations=all_mutations,
            rejected_mutations=rejected_mutations,
            generation_fitness=generation_fitness,
        )

        # Persist to DynamoDB
        self._persist_evolution(content, result)

        return result

    def _persist_evolution(self, content: str, response: EvolutionLabResponse):
        """Persist evolution results to DynamoDB (fire-and-forget)."""
        if not self._dynamo:
            return
        try:
            cid = _content_id(content)
            # Store full tree
            self._dynamo.store_full_evolution(cid, response.tree.model_dump())
            # Store original DNA
            self._dynamo.store_dna(cid, response.tree.root.dna.model_dump())
            # Store per-generation fitness
            for gf in response.generation_fitness:
                gen = gf.get("generation", 0)
                self._dynamo.store_fitness(cid, gen, gf)
            # Store each accepted mutation as a generation record
            for mut in response.all_mutations:
                self._dynamo.store_evolution(cid, int(mut.id[:8], 16) % 10000, mut.model_dump())
            logger.info(f"Persisted evolution {cid} to DynamoDB")
        except Exception as e:
            logger.error(f"Failed to persist evolution to DynamoDB: {e}")

    def _persist_single(self, content: str, response: CreateResponse):
        """Persist single evolution result to DynamoDB."""
        if not self._dynamo:
            return
        try:
            cid = _content_id(content)
            self._dynamo.store_dna(cid, response.dna_original.model_dump())
            self._dynamo.store_evolution(cid, 0, {
                "original": content,
                "evolved": response.evolved.model_dump(),
                "fitness_delta": response.fitness_delta.model_dump(),
            })
            logger.info(f"Persisted single evolution {cid} to DynamoDB")
        except Exception as e:
            logger.error(f"Failed to persist single evolution to DynamoDB: {e}")

    # ── Internal Helpers ──────────────────────────────────────────────────────

    def _attempt_mutation(
        self,
        content: str,
        strategy: MutationStrategy,
        generation: int,
        parent_id: str,
        platform: PlatformType = PlatformType.GENERAL,
    ) -> MutationResult:
        """Attempt a single mutation with similarity checking."""
        mutated_content = self.mutation_engine.mutate(content, strategy, platform=platform.value)

        # Similarity check
        accepted, similarity, reason = self.similarity_guard.check(mutated_content, content)

        # Extract DNA
        dna = self.dna_extractor.extract(mutated_content)

        # Score fitness
        fitness = self.fitness_scorer.score(
            mutated_content,
            dna,
            strategy=strategy,
            parent_content=content,
            used_strategies=self.similarity_guard.get_used_strategies(),
            similarity=similarity,
        )

        return MutationResult(
            strategy=strategy,
            content=mutated_content,
            dna=dna,
            fitness=fitness,
            similarity_to_parent=round(similarity, 4),
            accepted=accepted,
            rejection_reason=reason,
        )

    def _compute_drift(self, dna_old: DNAProfile, dna_new: DNAProfile) -> list[DNADrift]:
        """Compute DNA drift between two profiles."""
        drifts: list[DNADrift] = []
        fields = ["intent", "tone", "emotional_signal", "platform_alignment", "structure_type"]

        for field in fields:
            old_val = str(getattr(dna_old, field, ""))
            new_val = str(getattr(dna_new, field, ""))
            if old_val != new_val:
                drifts.append(
                    DNADrift(
                        field=field,
                        old_value=old_val,
                        new_value=new_val,
                        impact=self._explain_drift(field, old_val, new_val),
                    )
                )

        # Check keyword drift
        old_kw = set(dna_old.keyword_clusters)
        new_kw = set(dna_new.keyword_clusters)
        added = new_kw - old_kw
        removed = old_kw - new_kw
        if added or removed:
            drifts.append(
                DNADrift(
                    field="keyword_clusters",
                    old_value=", ".join(sorted(old_kw)),
                    new_value=", ".join(sorted(new_kw)),
                    impact=f"Added: {', '.join(sorted(added)) or 'none'}; Removed: {', '.join(sorted(removed)) or 'none'}",
                )
            )

        return drifts

    @staticmethod
    def _explain_drift(field: str, old_val: str, new_val: str) -> str:
        """Generate a human-readable drift explanation."""
        explanations = {
            "intent": f"Content intent shifted from '{old_val}' to '{new_val}' — this changes the core purpose of the message.",
            "tone": f"Tone evolved from '{old_val}' to '{new_val}' — this alters how the audience perceives the message.",
            "emotional_signal": f"Emotional signal shifted from '{old_val}' to '{new_val}' — this changes the emotional resonance.",
            "platform_alignment": f"Platform fit changed from '{old_val}' to '{new_val}' — content may perform differently across channels.",
            "structure_type": f"Structure type changed from '{old_val}' to '{new_val}' — this affects readability and engagement patterns.",
        }
        return explanations.get(field, f"{field} changed from '{old_val}' to '{new_val}'")

    def _find_winner(self, node: EvolutionNode) -> EvolutionNode | None:
        """Find the winning node (deepest generation winner) in the tree."""
        if node.is_winner and not any(c.is_winner for c in node.children):
            return node
        for child in node.children:
            winner = self._find_winner(child)
            if winner:
                return winner
        if node.is_winner:
            return node
        return None
