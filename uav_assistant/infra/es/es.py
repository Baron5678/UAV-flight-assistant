from __future__ import annotations

from typing import Sequence, Tuple
import numpy as np
import cma

from uav_assistant.cross.sockets import TraceFn
from uav_assistant.domain.models import Drone, ESConfiguration, Waypoint, OptimizerStep
from uav_assistant.infra.ga.population import build_initial_population
from uav_assistant.infra.objective_functions.decoders import get_decoder_builder
from uav_assistant.infra.objective_functions.energy import insert_stations_if_needed
from uav_assistant.infra.objective_functions.objectives import Objectives


def solve_path(
    points: Sequence[Waypoint],
    *,
    start_id: int,
    end_id: int,
    graph,
    configuration: ESConfiguration,
    drone: Drone,
    trace: TraceFn | None = None,
) -> Tuple[list[int], float]:
    base_config = configuration.config
    objective_name = base_config.objective
    decoder_builder = get_decoder_builder(objective_name)

    ids = [int(p.id) for p in points]
    id_set = set(ids)
    if start_id not in id_set or end_id not in id_set:
        raise ValueError("run_es: start_id or end_id not present in points")

    gene_ids = decoder_builder.select_genes(points, start_id, end_id)
    if not gene_ids:
        return [start_id, end_id], 0.0

    num_genes = len(gene_ids)
    np.random.seed(base_config.seed)
    init_pop = build_initial_population(
        waypoint_ids=gene_ids,
        pop_size=max(2, base_config.population_size),
    )
    x0 = np.asarray(init_pop[0], dtype=float)

    decode_fn = decoder_builder.build_decoder(
        points=points,
        start_id=start_id,
        end_id=end_id,
        middles=gene_ids,
    )

    objective = Objectives.ES[objective_name](
        decode=decode_fn,
        graph=graph,
        points=points,
        configuration=base_config,
        drone=drone,
    )

    sigma0 = configuration.sigma0
    pop_size = base_config.population_size
    generations = base_config.generations

    es = cma.CMAEvolutionStrategy(
        x0.tolist(),
        float(sigma0),
        {
            "popsize": int(pop_size),
            "bounds": [0.0, 1.0],
            "maxiter": int(generations),
            "seed": base_config.seed,
            "tolstagnation": int(generations),
            "verb_disp": 1,
        },
    )

    best_x: np.ndarray | None = None
    best_cost: float = float("inf")
    best_route: list[int] = [start_id, end_id]

    while not es.stop():
        xs = es.ask()
        fs = []
        for x in xs:
            x_arr = np.asarray(x, dtype=float)
            f = float(objective(x_arr))
            fs.append(f)

            if f < best_cost:
                best_cost = f
                best_x = x_arr
                best_route = decode_fn(best_x)

        es.tell(xs, fs)

        if trace is not None:
            gen = int(es.countiter)
            trace(OptimizerStep(
                generation=gen,
                cost=float(best_cost),
                waypoint_ids=list(best_route))
            )

    if best_x is None:
        best_x = np.asarray(x0, dtype=float)
        best_cost = float(objective(best_x))
        best_route = decode_fn(best_x)

    route_required = decode_fn(best_x)

    id2wp: dict[int, Waypoint] = {p.id: p for p in points}
    obj = getattr(objective_name, "value", objective_name)
    is_energy = str(obj).upper() == "ENERGY"
    if is_energy:
        route_fixed, feasible, _ = insert_stations_if_needed(
            route_required,
            id2wp,
            battery_wh=drone.battery_capacity_wh,
            per_meter_wh=drone.per_meter_wh,
            reserve_ratio=0.0,
        )
        best_route = route_fixed if feasible else list(route_required)
    else:
        best_route = list(route_required)

    return best_route, float(best_cost)
