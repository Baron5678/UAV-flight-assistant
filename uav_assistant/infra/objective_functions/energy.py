from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence
import numpy as np

from uav_assistant.cross.enums import WaypointRole, INFEASIBLE_COST
from uav_assistant.domain.metrics import distance_m, estimate_energy_wh
from uav_assistant.domain.models import AlgorithmConfiguration, Drone, Waypoint



def _role_upper(wp: Any) -> str:
    r = getattr(wp, "role", None)
    return str(getattr(r, "value", r)).upper()

def _is_station(wp: Any) -> bool:
    return _role_upper(wp) == "STATION"

def select_genes(points: Sequence[Waypoint], start_id: int, end_id: int) -> list[int]:
    return [
        p.id for p in points
        if p.id not in (start_id, end_id)
        and p.role == WaypointRole.REQUIRED
    ]


def build_decoder(*, points: Sequence[Waypoint], start_id: int, end_id: int, middles: list[int], **kwargs):
    def decode_fn(sol: np.ndarray) -> list[int]:
        keys = np.asarray(sol, dtype=float)
        if keys.shape[0] != len(middles):
            raise ValueError(f"decode_energy: len(sol)={keys.shape[0]} must equal len(middles)={len(middles)}")

        ordered = [wid for _, wid in sorted(zip(keys, middles), key=lambda t: (float(t[0]), int(t[1])))]
        return [start_id] + ordered + [end_id]
    return decode_fn



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

        dist = float(distance_m(wp_prev, wp_cur))
        if not np.isfinite(dist) or dist < 0:
            return float("inf"), False, station_visits

        total_dist += dist

        e = float(estimate_energy_wh(dist, per_meter_wh))
        if not np.isfinite(e) or e < 0:
            return float("inf"), False, station_visits

        if soc - e < reserve:
            return total_dist, False, station_visits

        soc -= e

        role_obj = getattr(wp_cur, "role", None)
        role_name = str(getattr(role_obj, "value", role_obj)).upper()

        if role_name == "STATION":
            soc = float(battery_wh)
            station_visits += 1

        prev_id = cur_id

    return total_dist, True, station_visits


def energy_cost(
    route_ids: Sequence[int],
    id2wp: Mapping[int, Any],
    *,
    battery_wh: float,
    per_meter_wh: float,
    reserve_ratio: float,
) -> float:
    repaired_ids, feasible, station_visits = insert_stations_if_needed(
        route_ids,
        id2wp,
        battery_wh=battery_wh,
        per_meter_wh=per_meter_wh,
        reserve_ratio=reserve_ratio,
    )

    if not feasible:
        return float(INFEASIBLE_COST)

    total_dist = 0.0
    for a, b in zip(repaired_ids, repaired_ids[1:]):
        wp_a = id2wp[a]
        wp_b = id2wp[b]
        d = float(distance_m(wp_a, wp_b))
        if not np.isfinite(d) or d < 0:
            return INFEASIBLE_COST
        total_dist += d

    cost = float(total_dist + 20 * station_visits)
    return cost if np.isfinite(cost) else float(INFEASIBLE_COST)

def build_energy_ga(
    *,
    decode: Callable[[np.ndarray], Sequence[int]],
    points: Sequence[Waypoint],
    configuration: AlgorithmConfiguration,
    drone: Drone,
    reserve_ratio: float = 0.0,
    **kwargs,
) -> Callable:
    def fitness_func(ga, sol, idx):
        sol_arr = np.asarray(sol, dtype=float)
        route_ids = decode(sol_arr)
        id2wp: dict[int, Any] = {p.id: p for p in points}
        cost = energy_cost(
            route_ids=route_ids,
            id2wp=id2wp,
            battery_wh=drone.battery_capacity_wh,
            per_meter_wh=drone.per_meter_wh,
            reserve_ratio=reserve_ratio,
        )
        if not np.isfinite(cost):
            return -INFEASIBLE_COST

        return -float(cost)

    return fitness_func


def build_energy_es(
    *,
    decode: Callable[[np.ndarray], Sequence[int]],
    points: Sequence[Waypoint],
    configuration: AlgorithmConfiguration,
    drone: Drone,
    reserve_ratio: float = 0.0,
    **kwargs,
) -> Callable[[np.ndarray], float]:
    def objective(x: np.ndarray) -> float:
        x = np.asarray(x, dtype=float)
        route_ids = decode(x)
        id2wp: dict[int, Any] = {p.id: p for p in points}
        return float(
            energy_cost(
                route_ids=route_ids,
                id2wp=id2wp,
                battery_wh=drone.battery_capacity_wh,
                per_meter_wh=drone.per_meter_wh,
                reserve_ratio=reserve_ratio,
            )
        )

    return objective

def insert_stations_if_needed(
    route_ids: Sequence[int],
    id2wp: Mapping[int, Any],
    *,
    battery_wh: float,
    per_meter_wh: float,
    reserve_ratio: float,
) -> tuple[list[int], bool, int]:

    if not route_ids:
        return [], False, 0

    station_ids = [wid for wid, wp in id2wp.items() if _is_station(wp)]

    soc = float(battery_wh)
    reserve = float(battery_wh * reserve_ratio)
    station_visits = 0

    out: list[int] = [int(route_ids[0])]

    for next_id in route_ids[1:]:
        next_id = int(next_id)

        while True:
            cur_id = out[-1]
            wp_cur = id2wp[cur_id]
            wp_next = id2wp[next_id]

            dist = float(distance_m(wp_cur, wp_next))
            needed = float(dist * per_meter_wh)
            if needed > (battery_wh - reserve):
                return out + [next_id], False, station_visits

            if soc - needed >= reserve:
                soc -= needed
                out.append(next_id)

                if id2wp[next_id].role == WaypointRole.STATION:
                    soc = float(battery_wh)
                    station_visits += 1

                break


            best_sid = None
            best_score = float("inf")

            for sid in station_ids:
                d1 = float(distance_m(wp_cur, id2wp[sid]))
                e1 = float(d1 * per_meter_wh)
                x = soc - e1
                if x < reserve:
                    continue

                d2 = float(distance_m(id2wp[sid], wp_next))
                score = d1 + d2
                if score < best_score:
                    best_score = score
                    best_sid = sid

            if best_sid is None:
                return out + [next_id], False, station_visits

            d1 = float(distance_m(wp_cur, id2wp[best_sid]))
            e1 = float(d1 * per_meter_wh)
            soc -= e1
            out.append(best_sid)
            soc = float(battery_wh)
            station_visits += 1

    return out, True, station_visits
