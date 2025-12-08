from typing import Sequence, Tuple, Any

import numpy as np
import pygad
from uav_assistant.infra.db.models import Waypoint, WaypointRole
from uav_assistant.infra.ga.population import build_initial_population
from uav_assistant.infra.ga.fitness_functions import make_distance_fitness, make_energy_fitness
from uav_assistant.infra.ga.genetic_decoders import decode, decode_with_stations


def run_ga(points: list[Waypoint],
           graph,
           start_id: int,
           end_id: int,
           generations: int = 30,
           pop_size: int = 20):

    if start_id == end_id:
        raise ValueError("start_id and end_id must be different.")

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

def run_ga_s(
    points: Sequence[Any],
    *,
    start_id: int,
    end_id: int,
    generations: int = 30,
    pop_size: int = 20,
    battery_wh: float = 200.0,
    per_meter_wh: float = 0.05,
    reserve_ratio: float = 0.2,
    station_threshold: float = 0.5,
    station_penalty_m: float = 200.0,
) -> Tuple[list[int], float]:

    ids = [int(p.id) for p in points]
    id_set = set(ids)
    if start_id not in id_set or end_id not in id_set:
        raise ValueError("run_ga: start_id or end_id not present in points")

    middle_ids = [wid for wid in ids if wid not in {start_id, end_id}]

    if not middle_ids:
        return [start_id, end_id], 0.0

    id2wp: dict[int, Any] = {int(p.id): p for p in points}
    id2role: dict[int, Any] = {
        int(p.id): getattr(p, "role", None) for p in points
    }

    np.random.seed(127)
    num_genes = len(middle_ids)

    init_pop = build_initial_population(
        waypoint_ids=middle_ids,
        pop_size=pop_size,
    )

    ids_for_decoder = [start_id] + middle_ids + [end_id]

    def decode_fn(sol: np.ndarray) -> list[int]:
        return decode_with_stations(
            sol=np.asarray(sol, dtype=float),
            ids=ids_for_decoder,
            middle_ids=middle_ids,
            id2role=id2role,
            threshold=station_threshold,
        )

    fitness = make_energy_fitness(
        decode=decode_fn,
        id2wp=id2wp,
        battery_wh=battery_wh,
        per_meter_wh=per_meter_wh,
        reserve_ratio=reserve_ratio,
        station_penalty_m=station_penalty_m,
    )

    ga = pygad.GA(
        num_generations=generations,
        sol_per_pop=pop_size,
        num_parents_mating=min(pop_size // 2, 10),
        num_genes=num_genes,
        gene_space=[(0.0, 1.0)] * num_genes,
        initial_population=init_pop,
        fitness_func=fitness,
        parent_selection_type="tournament",
        K_tournament=3,
        keep_elitism=max(1, pop_size // 10),
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
    best_cost = -float(best_fit)
    return best_route, best_cost