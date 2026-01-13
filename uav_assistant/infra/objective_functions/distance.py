from __future__ import annotations
from typing import Callable, Mapping, Sequence
import numpy as np

from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.models import Waypoint, AlgoSettings

DEFAULT_BAD_COST: float = 1.0e14

def build_id_index(points: Sequence) -> dict[int, int]:
    return {p.id: i for i, p in enumerate(points)}

def calculate_route_distance(
    route_ids: Sequence[int],
    graph: np.ndarray,
    id2idx: Mapping[int, int],
) -> float:
    try:
        idx_path = [id2idx[r] for r in route_ids]
    except KeyError:
        return np.inf

    total = 0.0
    for i in range(len(idx_path) - 1):
        a = idx_path[i]
        b = idx_path[i + 1]
        w = graph[a, b]
        if not np.isfinite(w) or w < 0:
            return np.inf
        total += float(w)

    return float(total)


def select_genes(points: Sequence[Waypoint], start_id: int, end_id: int) -> list[int]:
    return [
        p.id for p in points
        if p.id not in (start_id, end_id) and p.role == WaypointRole.REQUIRED
    ]


def build_decoder(*, points: Sequence[Waypoint], start_id: int, end_id: int, middles: list[int]):
    def decode_fn(sol: np.ndarray) -> list[int]:
        keys = np.asarray(sol, dtype=float)
        if keys.shape[0] != len(middles):
            raise ValueError(f"decode_distance: len(sol)={keys.shape[0]} != len(middles)={len(middles)}")
        ordered = [mid for _, mid in sorted(zip(keys, middles), key=lambda t: (float(t[0]), int(t[1])))]
        return [start_id] + ordered + [end_id]
    return decode_fn

def build_distance_es(
        *,
        decode: Callable[[np.ndarray], Sequence[int]],
        graph: np.ndarray,
        points: Sequence[Waypoint],
        settings: AlgoSettings,
        bad_cost: float = DEFAULT_BAD_COST,
) -> Callable[[np.ndarray], float]:
    def objective(x: np.ndarray) -> float:
        id2idx = build_id_index(points)
        sol = np.asarray(x, dtype=float)
        route = decode(sol)
        dist = calculate_route_distance(route, graph, id2idx)
        if not np.isfinite(dist):
            return float(bad_cost)
        return float(dist)
    return objective


def build_distance_ga(
        *,
        decode: Callable[[np.ndarray], Sequence[int]],
        graph: np.ndarray,
        points: Sequence[Waypoint],
        settings: AlgoSettings,
        bad_fitness: float = -1.0e14,
) -> Callable:
    def fitness_func(ga, sol, idx):
        id2idx = build_id_index(points)
        sol = np.asarray(sol, dtype=float)
        route = decode(sol)
        dist = calculate_route_distance(route, graph, id2idx)
        if not np.isfinite(dist):
            return float(bad_fitness)
        return -float(dist)
    return fitness_func
