from __future__ import annotations
import asyncio
import math
from typing import Sequence, Callable, List, Tuple, Union
from uav_assistant.app.interfaces import PathOptimizer
from uav_assistant.cross.sockets import TraceFn, TraceQueue
from uav_assistant.domain.metrics import build_distance_matrix, distance_m, build_id2wp
from uav_assistant.domain.models import (AlgoSettings, Mission, Drone, Waypoint, Path, OptimizerFinal, OptimizerError,
                                         OptimizerStep)

Runner = Callable[..., tuple[list[int], float]]

def is_infeasible(cost: float) -> bool:
    return not math.isfinite(cost)


def _validate(mission: Mission, candidates: Sequence[Waypoint]) -> None:
    ids = {w.id for w in candidates}
    if mission.start_waypoint_id not in ids or mission.end_waypoint_id not in ids:
        raise ValueError("Start or end waypoint not in candidates")


def _build_settings(mission: Mission, drones: Sequence[Drone]) -> AlgoSettings:

    per_meter_wh = drones[0].per_meter_wh / 1000.0
    print(mission.objective)
    return AlgoSettings(
        objective=mission.objective,
        generations=mission.generations,
        population_size=mission.population_size,
        battery_wh=drones[0].battery_capacity_wh,
        speed_mps=drones[0].speed_mps,
        per_meter_wh=per_meter_wh,
        keep_elitism=mission.keep_elitism,
        mutation_probability=mission.mutation_probability,
        sigma0=mission.sigma0,
        k_tournament=mission.k_tournament,
        seed=mission.seed,
        reserve_ratio=0.0,
        station_penalty_m=200.0,
        station_threshold=0.0
    )


def _compute_total_distance(route_ids: Sequence[int], points: Sequence[Waypoint]) -> float:
    id_to_wp = {w.id: w for w in points}
    total_dist = 0.0
    for a, b in zip(route_ids, route_ids[1:]):
        total_dist += distance_m(id_to_wp[a].position, id_to_wp[b].position)
    return float(total_dist)


class BasePathOptimizer(PathOptimizer):
    def __init__(self, *, algo_name: str, runner: Runner) -> None:
        self.algo_name = algo_name
        self._runner = runner

    def _run(
            self,
            points: list[Waypoint],
            start_id: int,
            end_id: int,
            graph,
            settings: AlgoSettings,
            trace: TraceFn | None,
    ) -> tuple[list[int], float]:
        return self._runner(
            points,
            start_id=start_id,
            end_id=end_id,
            graph=graph,
            settings=settings,
            trace=trace,
        )

    async def optimize_http(self, mission: Mission, drones: Sequence[Drone], candidates: Sequence[Waypoint]) -> \
            Tuple[Union[Path | OptimizerError], List[OptimizerStep]]:

        _validate(mission, candidates)
        points = list(candidates)
        graph = build_distance_matrix(points)
        settings = _build_settings(mission, drones)
        steps: list[OptimizerStep] = []

        def trace(step: OptimizerStep) -> None:
            steps.append(step)

        best_route_ids, best_cost = await asyncio.to_thread(
            self._run,
            points,
            mission.start_waypoint_id,
            mission.end_waypoint_id,
            graph,
            settings,
            trace,
        )

        if is_infeasible(best_cost):
            return OptimizerError(type="diagnostic", feasible=False, problem="Impossible to construct path!"), []


        total_dist = _compute_total_distance(best_route_ids, points)
        return Path(waypoint_ids=list(best_route_ids), total_distance_m=total_dist, cost=float(best_cost)), steps

    def optimize_ws(
            self,
            mission: Mission,
            drones: Sequence[Drone],
            candidates: Sequence[Waypoint],
            loop: asyncio.AbstractEventLoop,
            queue: TraceQueue,
            trace: TraceFn | None,
    ) -> None:
        _validate(mission, candidates)

        points = list(candidates)
        graph = build_distance_matrix(points)
        settings = _build_settings(mission, drones)

        def worker() -> None:
            best_route_ids, best_cost = self._run(
                points=points,
                start_id=mission.start_waypoint_id,
                end_id=mission.end_waypoint_id,
                graph=graph,
                settings=settings,
                trace=trace,
            )

            # if is_infeasible(best_cost):
            #     diag = OptimizerError(
            #         type="diagnostic",
            #         feasible=False,
            #         problem="Path is impossible to construct",
            #     )
            #     loop.call_soon_threadsafe(queue.put_nowait, diag)
            #     return

            total_dist = _compute_total_distance(best_route_ids, points)
            final_event = OptimizerFinal(
                algo=self.algo_name,
                generations=mission.generations,
                cost=float(best_cost),
                waypoint_ids=list(best_route_ids),
                total_distance_m=total_dist,
            )
            loop.call_soon_threadsafe(queue.put_nowait, final_event)

        loop.run_in_executor(None, worker)