from __future__ import annotations
from typing import Callable, Iterable, Mapping, Sequence, Any
import numpy as np

from uav_assistant.domain.metrics import distance_m, estimate_energy_wh


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

def simulate_energy_route(
    route_ids: Sequence[int],
    id2wp: Mapping[int, Any],
    *,
    battery_wh: float,
    per_meter_wh: float,
    reserve_ratio: float,
) -> tuple[float, bool, int]:
    if not route_ids:
        return 0.0, False, 0

    soc = float(battery_wh)
    reserve = float(battery_wh * reserve_ratio)
    total_dist = 0.0
    station_visits = 0

    prev_id = route_ids[0]
    for cur_id in route_ids[1:]:
        wp_prev = id2wp[prev_id]
        wp_cur = id2wp[cur_id]

        dist = float(distance_m(wp_prev.position, wp_cur.position))
        total_dist += dist
        e = float(estimate_energy_wh(dist, per_meter_wh))
        if soc - e < reserve:
            return total_dist, False, station_visits
        soc -= e
        role_obj = getattr(wp_cur, "role", None)
        if hasattr(role_obj, "value"):
            role_name = str(role_obj.value).upper()
        else:
            role_name = str(role_obj).upper()

        if role_name == "STATION":
            soc = float(battery_wh)
            station_visits += 1

        prev_id = cur_id

    return total_dist, True, station_visits


def make_energy_fitness(
    *,
    decode: Callable[[np.ndarray], Sequence[int]],
    id2wp: Mapping[int, Any],
    battery_wh: float,
    per_meter_wh: float,
    reserve_ratio: float,
    station_penalty_m: float = 0.0,
) -> Callable:

    def fitness_func(ga, sol, idx):
        sol_arr = np.asarray(sol, dtype=float)
        route_ids = decode(sol_arr)
        total_dist, feasible, station_visits = simulate_energy_route(
            route_ids=route_ids,
            id2wp=id2wp,
            battery_wh=battery_wh,
            per_meter_wh=per_meter_wh,
            reserve_ratio=reserve_ratio,
        )
        if (not feasible) or (not np.isfinite(total_dist)):
            return -1e14
        cost = float(total_dist + station_penalty_m * station_visits)
        if not np.isfinite(cost):
            return -1e14
        return -cost

    return fitness_func
