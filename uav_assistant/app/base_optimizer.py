from __future__ import annotations
import asyncio
import math
from typing import Sequence, Callable, List, Tuple, Union
from uav_assistant.app.interfaces import AlgorithmRunConfiguration, PathOptimizer
from uav_assistant.cross.enums import WaypointRole
from uav_assistant.cross.sockets import TraceFn, TraceQueue
from uav_assistant.domain.metrics import build_distance_matrix, distance_m
from uav_assistant.domain.models import Drone, Waypoint, Path, OptimizerFinal, OptimizerError, OptimizerStep

Runner = Callable[..., tuple[list[int], float]]

def is_infeasible(cost: float) -> bool:
    return not math.isfinite(cost)


def _find_endpoint_ids(candidates: Sequence[Waypoint]) -> tuple[int, int]:
    start_id = None
    end_id = None

    for waypoint in candidates:
        if waypoint.role == WaypointRole.START:
            start_id = waypoint.id
        elif waypoint.role == WaypointRole.END:
            end_id = waypoint.id

    if start_id is None or end_id is None:
        raise ValueError("Start or end waypoint not in candidates")

    return start_id, end_id


def _compute_total_distance(route_ids: Sequence[int], points: Sequence[Waypoint]) -> float:
    id_to_wp = {w.id: w for w in points}
    total_dist = 0.0
    for a, b in zip(route_ids, route_ids[1:]):
        total_dist += distance_m(id_to_wp[a], id_to_wp[b])
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
            config: AlgorithmRunConfiguration,
            drone: Drone,
            trace: TraceFn | None,
    ) -> tuple[list[int], float]:
        return self._runner(
            points,
            start_id=start_id,
            end_id=end_id,
            graph=graph,
            configuration=config,
            drone=drone,
            trace=trace,
        )

    async def optimize_http(self, config: AlgorithmRunConfiguration, drone: Drone, candidates: Sequence[Waypoint]) -> \
            Tuple[Union[Path | OptimizerError], List[OptimizerStep]]:

        start_id, end_id = _find_endpoint_ids(candidates)
        points = list(candidates)
        graph = build_distance_matrix(points)
        steps: list[OptimizerStep] = []

        def trace(step: OptimizerStep) -> None:
            steps.append(step)

        best_route_ids, best_cost = await asyncio.to_thread(
            self._run,
            points,
            start_id,
            end_id,
            graph,
            config,
            drone,
            trace,
        )

        if is_infeasible(best_cost):
            return OptimizerError(type="diagnostic", feasible=False, problem="Impossible to construct path!"), []


        total_dist = _compute_total_distance(best_route_ids, points)
        return Path(
            waypoint_ids=list(best_route_ids),
            generation=config.config.generations if hasattr(config, "config") else config.generations,
            distance_m=total_dist,
            cost=float(best_cost),
        ), steps

    def optimize_ws(
            self,
            config: AlgorithmRunConfiguration,
            drone: Drone,
            candidates: Sequence[Waypoint],
            loop: asyncio.AbstractEventLoop,
            queue: TraceQueue,
            trace: TraceFn | None,
    ) -> None:
        start_id, end_id = _find_endpoint_ids(candidates)

        points = list(candidates)
        graph = build_distance_matrix(points)

        def worker() -> None:
            best_route_ids, best_cost = self._run(
                points=points,
                start_id=start_id,
                end_id=end_id,
                graph=graph,
                config=config,
                drone=drone,
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
                generations=config.config.generations if hasattr(config, "config") else config.generations,
                cost=float(best_cost),
                waypoint_ids=list(best_route_ids),
                total_distance_m=total_dist,
            )
            loop.call_soon_threadsafe(queue.put_nowait, final_event)

        loop.run_in_executor(None, worker)
