from typing import Sequence, Tuple
import numpy as np
import pygad

from uav_assistant.cross.sockets import TraceFn
from uav_assistant.domain.models import AlgoSettings, OptimizerStep
from uav_assistant.domain.models import Waypoint
from uav_assistant.infra.ga.population import build_initial_population
from uav_assistant.infra.objective_functions.decoders import Decoders
from uav_assistant.infra.objective_functions.energy import insert_stations_if_needed
from uav_assistant.infra.objective_functions.objectives import Objectives
from uav_assistant.infra.preprocess.prerun import pre_run_energy


def build_on_generation(trace: TraceFn | None, decode_fn):
    def on_generation(ga_instance: pygad.GA) -> None:
        if trace is None:
            return

        pop_fitness = getattr(ga_instance, "last_generation_fitness", None)
        if pop_fitness is None:
            try:
                pop_fitness = ga_instance.cal_pop_fitness()
            except Exception as e:
                print("cal_pop_fitness failed inside on_generation:", e)
            return

        sol, fit, _ = ga_instance.best_solution(pop_fitness=pop_fitness)
        route_ids = decode_fn(sol)
        cost = -float(fit)
        gen = ga_instance.generations_completed

        trace(
            OptimizerStep(
                generation=gen,
                cost=float(cost),
                waypoint_ids=list(route_ids)
            )
        )
    return on_generation


def run(
    points: Sequence[Waypoint],
    *,
    start_id: int,
    end_id: int,
    graph,
    settings: AlgoSettings,
    trace: TraceFn | None = None,
) -> Tuple[list[int], float]:
    ids = [int(p.id) for p in points]
    id_set = set(ids)
    if start_id not in id_set or end_id not in id_set:
        raise ValueError("run_ga: start_id or end_id not present in points")
    gene_ids = Decoders.GENES[settings.objective](points, start_id, end_id)  #
    if not gene_ids:
        return [start_id, end_id], 0.0
    np.random.seed(127)
    num_genes = len(gene_ids)
    init_pop = build_initial_population(
        waypoint_ids=gene_ids,
        pop_size=settings.population_size,
    )
    decode_fn = Decoders.BUILD[settings.objective](
        points=points,
        start_id=start_id,
        end_id=end_id,
        middles=gene_ids,
    )

    fitness_func = Objectives.GA[settings.objective](
        decode=decode_fn,
        graph=graph,
        points=points,
        settings=settings,
    )

    on_generation = build_on_generation(trace, decode_fn)

    ga = pygad.GA(
        num_generations=settings.generations,
        sol_per_pop=settings.population_size,
        num_parents_mating=min(settings.population_size // 2, 10),
        num_genes=num_genes,
        gene_space=[(0.0, 1.0)] * num_genes,
        initial_population=init_pop,
        fitness_func=fitness_func,
        parent_selection_type="tournament",
        K_tournament=3,
        keep_elitism=max(1, settings.population_size // 10),
        mutation_type="random",
        mutation_probability=0.12,
        crossover_type="scattered",
        keep_parents=max(1, settings.population_size // 40),
        allow_duplicate_genes=True,
        save_best_solutions=True,
        random_seed=127,
        on_generation=on_generation,
    )

    ga.run()

    best_sol, best_fit, _ = ga.best_solution()
    best_required = decode_fn(best_sol)


    obj = getattr(settings.objective, "value", settings.objective)
    if str(obj).upper() == "ENERGY":
        id2wp = {p.id: p for p in points}
        best_route, feasible, _ = insert_stations_if_needed(
            best_required,
            id2wp,
            battery_wh=settings.battery_wh,
            per_meter_wh=settings.per_meter_wh,
            reserve_ratio=settings.reserve_ratio,
        )
        if not feasible:
            return list(best_required), float("inf")
    else:
        best_route = best_required

    best_cost = -float(best_fit)
    return list(best_route), float(best_cost)
