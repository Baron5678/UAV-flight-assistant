import numpy as np
import pygad
from drone_path.app.db.models import Waypoint, WaypointRole
from drone_path.app.ga.population import build_initial_population
from drone_path.app.ga.model_operations import build_distance_matrix
from drone_path.app.ga.fitness_functions import make_distance_fitness
from drone_path.app.ga.genetic_decoders import decode


def run_ga(points: list[Waypoint],
           start_id: int,
           end_id: int,
           generations: int = 30,
           pop_size: int = 20):

    if start_id == end_id:
        raise ValueError("start_id and end_id must be different.")

    graph = build_distance_matrix(points)
    id2idx = {p.id: i for i, p in enumerate(points)}

    required_ids = [
        p.id for p in points
        if p.id not in (start_id, end_id) and p.role == WaypointRole.REQUIRED
    ]

    if not required_ids:
        raise ValueError("No REQUIRED waypoints defined between start and end.")

    middles = required_ids[:]
    num_genes = len(middles)

    initial_population = build_initial_population(
        waypoint_ids=middles,
        pop_size=pop_size,
    )

    ids_for_decoder = [start_id] + middles + [end_id]

    def decode_fn(sol: np.ndarray):
        return decode(sol, ids_for_decoder, middles)

    fitness_func = make_distance_fitness(
        decode=decode_fn,
        graph=graph,
        id2idx=id2idx,
    )

    ga = pygad.GA(
        num_generations=generations,
        sol_per_pop=pop_size,
        num_parents_mating=min(10, pop_size),
        num_genes=num_genes,
        gene_space=[(0.0, 1.0)] * num_genes,
        initial_population=initial_population,
        fitness_func=fitness_func,
        parent_selection_type="tournament",
        K_tournament=3,
        keep_elitism=min(5, pop_size),
        mutation_type="random",
        mutation_probability=0.12,
        crossover_type="scattered",
        keep_parents=max(1, pop_size // 20),
        allow_duplicate_genes=True,
        save_best_solutions=True,
        random_seed=127,
    )

    ga.run()
    best_sol, best_fit, _ = ga.best_solution()
    best_route = decode_fn(best_sol)
    best_cost = -best_fit
    return best_route, float(best_cost)
