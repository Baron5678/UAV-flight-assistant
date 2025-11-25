# cma_es_algorithm.py
from __future__ import annotations

from typing import Sequence, Tuple
import numpy as np
import cma

from uav_assistant.domain.metrics import build_distance_matrix
from uav_assistant.domain.models import Waypoint
from uav_assistant.infra.ga.population import build_initial_population
from uav_assistant.infra.ga.genetic_decoders import decode
from uav_assistant.infra.ga.fitness_functions import build_id_index, route_distance

def run_es(
    *,
    points: Sequence[Waypoint],
    start_id: int,
    end_id: int,
    generations: int = 50,
    pop_size: int = 20,
    sigma0: float = 0.3,
) -> Tuple[list[int], float]:
    if not points:
        raise ValueError("run_es: empty points")

    ids_all = [p.id for p in points]
    if start_id not in ids_all or end_id not in ids_all:
        raise ValueError("run_es: start_id or end_id not in points")

    id2idx = build_id_index(points)

    W = np.asarray(build_distance_matrix(list(points)), dtype=float)

    middle_ids = [wid for wid in ids_all if wid not in (start_id, end_id)]
    decode_ids = [start_id] + middle_ids + [end_id]
    num_genes = len(middle_ids)

    if num_genes == 0:
        route = [start_id, end_id]
        cost = route_distance(route, W, id2idx)
        return route, float(cost)

    def decode_fn(sol: np.ndarray) -> list[int]:
        return decode(
            sol=np.asarray(sol, dtype=float),
            ids=decode_ids,
            middles=middle_ids,
        )

    init_pop = build_initial_population(
        waypoint_ids=middle_ids,
        pop_size=pop_size,
    )
    x0 = init_pop.mean(axis=0)

    def objective(x: np.ndarray) -> float:
        route = decode_fn(x)
        dist = route_distance(route, W, id2idx)
        if not np.isfinite(dist):
            return 1.0e14
        return float(dist)

    es = cma.CMAEvolutionStrategy(
        x0.tolist(),
        sigma0,
        {
            "popsize": pop_size,
            "bounds": [0.0, 1.0],
            "maxiter": generations,
            "verb_disp": 1,
            "seed": 127,
        },
    )

    es.optimize(objective)

    best_x = np.asarray(es.result.xbest, dtype=float)
    best_route = decode_fn(best_x)
    best_cost = objective(best_x)

    return best_route, float(best_cost)
