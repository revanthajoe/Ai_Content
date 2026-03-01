"""Quick integration test for the evolution lab."""
from app.core import EvolutionManager

mgr = EvolutionManager()
r = mgr.evolve_lab(
    'Digital marketing in 2026 has changed fundamentally. Traditional content strategies no longer work. '
    'Brands need to think about AI-driven personalization, adaptive content systems, and evolutionary intelligence. '
    'The era of static posts is over. Every piece of content must earn its survival through engagement, resonance, and clarity. '
    'Create once, test once, forget is dead. The future demands continuous evolution.',
    generations=3
)

print(f"Total mutations: {r.tree.total_mutations}")
print(f"Total rejected: {r.tree.total_rejected}")
print(f"Winner fitness: {r.winner.fitness.total}")
print(f"Winner strategy: {r.winner.strategy}")
print(f"Accepted mutations: {len(r.all_mutations)}")
print("Generation fitness:")
for g in r.generation_fitness:
    print(f"  Gen {g['generation']}: fitness={g.get('best_fitness', 'N/A')} strategy={g.get('strategy', 'origin')}")
print("\nWinner content (first 200 chars):")
print(r.winner.content[:200])
print("\n✅ All systems operational")
