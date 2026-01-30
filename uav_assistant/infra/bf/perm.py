from __future__ import annotations

from itertools import permutations
from typing import Dict, Sequence, Tuple

import numpy as np

from uav_assistant.cross.sockets import TraceFn
from uav_assistant.domain.models import AlgoSettings, Waypoint, OptimizerStep


def _build_id2idx(points: Sequence[Waypoint]) -> Dict[int, int]:
    # Must match how you built your graph indices; simplest: same order as points list.
    return {int(p.id): i for i, p in enumerate(points)}


def _dist_by_id(a_id: int, b_id: int, graph: np.ndarray, id2idx: Dict[int, int]) -> float:
    ia = id2idx.get(int(a_id))
    ib = id2idx.get(int(b_id))
    if ia is None or ib is None:
        return float("inf")
    w = float(graph[ia, ib])
    return w if np.isfinite(w) and w >= 0 else float("inf")


def _route_cost(route: list[int], graph: np.ndarray, id2idx: Dict[int, int]) -> float:
    total = 0.0
    for a, b in zip(route, route[1:]):
        w = _dist_by_id(a, b, graph, id2idx)
        if not np.isfinite(w):
            return float("inf")
        total += w
    return float(total)


def run(
    points: Sequence[Waypoint],
    *,
    start_id: int,
    end_id: int,
    graph: np.ndarray,
    settings: AlgoSettings,
    trace: TraceFn | None = None,
) -> Tuple[list[int], float]:
    obj = str(getattr(settings.objective, "value", settings.objective)).upper()
    if obj != "DISTANCE":
        raise NotImplementedError(f"BF-perm supports only DISTANCE objective, got {obj}")

    ids = {int(p.id) for p in points}
    if start_id not in ids or end_id not in ids:
        raise ValueError("run_bf_perm_distance: start_id or end_id not present in points")

    req_ids = [
        int(p.id)
        for p in points
        if int(p.id) not in (start_id, end_id)
        and str(getattr(p.role, "value", p.role)).upper() == "REQUIRED"
    ]

    n = len(req_ids)
    if n > 11:
        raise ValueError(f"Permutation brute force disabled for n={n} (>11). Use Held–Karp or GA/ES.")

    id2idx = _build_id2idx(points)

    best_cost = float("inf")
    best_route = [start_id] + req_ids + [end_id]

    checked = 0
    for perm in permutations(req_ids):
        checked += 1
        route = [start_id] + list(perm) + [end_id]
        cost = _route_cost(route, graph, id2idx)
        if cost < best_cost:
            best_cost = cost
            best_route = route

            if trace is not None:
                trace(
                    OptimizerStep(
                        generation=checked,  # "iteration" count
                        cost=float(best_cost),
                        waypoint_ids=list(best_route),
                    )
                )
    print(f"best_cost: {best_cost}");
    return best_route, float(best_cost)
