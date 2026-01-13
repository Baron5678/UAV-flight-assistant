from __future__ import annotations
import numpy as np
from typing import Dict, Sequence

from uav_assistant.app.interfaces import PathSummaryRepository
from uav_assistant.domain.metrics import distance_m
from uav_assistant.domain.models import PathSummary, Waypoint, OptimizerStep, PathSummaryStats


def _route_distance_m(waypoint_ids: Sequence[int], id_to_wp: Dict[int, Waypoint]) -> float:
    if len(waypoint_ids) < 2:
        return 0.0
    total = 0.0
    for a, b in zip(waypoint_ids, waypoint_ids[1:]):
        total += float(distance_m(id_to_wp[int(a)].position, id_to_wp[int(b)].position))
    return float(total)


class PathSummaryService:
    def __init__(self, repo: PathSummaryRepository) -> None:
        self._repo = repo

    async def append_step(
        self,
        *,
        mission_id: int,
        step: OptimizerStep,
        id_to_wp: Dict[int, Waypoint],
    ) -> None:
        dist = _route_distance_m(step.waypoint_ids, id_to_wp)
        summary = PathSummary(
            mission_id=int(mission_id),
            generation=int(step.generation),
            cost=float(step.cost),
            total_distance_m=float(dist),
        )
        await self._repo.add(summary)

    async def list_summaries(self, mission_id: int) -> list[PathSummary]:
        return await self._repo.list_by_mission(mission_id)

    async def clear_mission(self, mission_id: int) -> None:
        await self._repo.delete_for_mission(mission_id)


    async def compute_stats(self, mission_id: int) -> PathSummaryStats | None:
        rows = await self._repo.list_by_mission(mission_id)
        if not rows:
            return None

        # numpy arrays for fast aggregates
        costs = np.asarray([float(r.cost) for r in rows], dtype=float)
        dists = np.asarray([float(r.total_distance_m) for r in rows], dtype=float)

        min_cost = float(np.min(costs))
        max_cost = float(np.max(costs))
        avg_cost = float(np.mean(costs))

        min_dist = float(np.min(dists))
        max_dist = float(np.max(dists))
        avg_dist = float(np.mean(dists))

        # convergence metrics
        first_cost = float(costs[0])
        best_cost = min_cost

        improvement_abs = float(first_cost - best_cost)
        improvement_pct = float(improvement_abs / abs(first_cost)) if first_cost != 0.0 else 0.0

        best_so_far = first_cost
        improving_generations = 0
        last_improvement_generation: int | None = None

        stagnation = 0
        max_stagnation = 0

        for r in rows[1:]:
            c = float(r.cost)
            if c < best_so_far:
                improving_generations += 1
                best_so_far = c
                last_improvement_generation = int(r.generation)
                max_stagnation = max(max_stagnation, stagnation)
                stagnation = 0
            else:
                stagnation += 1

        max_stagnation = max(max_stagnation, stagnation)

        return PathSummaryStats(
            min_cost=min_cost,
            max_cost=max_cost,
            avg_cost=avg_cost,
            min_total_distance_m=min_dist,
            max_total_distance_m=max_dist,
            avg_total_distance_m=avg_dist,
            best_cost=float(best_cost),
            first_cost=float(first_cost),
            improvement_abs=float(improvement_abs),
            improvement_pct=float(improvement_pct),
            improving_generations=int(improving_generations),
            last_improvement_generation=last_improvement_generation,
            max_stagnation_generations=int(max_stagnation),
        )

