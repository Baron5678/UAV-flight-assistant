from __future__ import annotations
from typing import Callable, Iterable, Mapping, Sequence
import numpy as np


def build_id_index(points: Sequence) -> dict[int, int]:
    return {p.id: i for i, p in enumerate(points)}


def route_distance(route_ids: Sequence[int],
                   graph: np.ndarray,
                   id2idx: Mapping[int, int]) -> float:
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
        total += w

    return total



def make_distance_fitness(*,
                          decode: Callable[[np.ndarray], Sequence[int]],
                          graph: np.ndarray,
                          id2idx: Mapping[int, int]) -> Callable:
    def fitness_func(ga, sol, idx):
        sol = np.asarray(sol, dtype=float)
        route = decode(sol)
        dist = route_distance(route, graph, id2idx)
        if not np.isfinite(dist):
            return -1e14
        return -dist
    return fitness_func
