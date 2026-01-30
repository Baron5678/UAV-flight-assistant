from __future__ import annotations
from typing import Callable, Mapping, Sequence
import numpy as np
from uav_assistant.cross.enums import WaypointRole, INFEASIBLE_COST
from uav_assistant.domain.metrics import build_id_index
from uav_assistant.domain.models import Waypoint, AlgoSettings

def select_genes(points: Sequence[Waypoint], start_id: int, end_id: int) -> list[int]:
    return [
        int(p.id) for p in points
        if int(p.id) not in (int(start_id), int(end_id)) and p.role == WaypointRole.REQUIRED
    ]

def build_decoder(*, points: Sequence[Waypoint], start_id: int, end_id: int, middles: list[int]):
    def decode_fn(sol: np.ndarray) -> list[int]:
        keys = np.asarray(sol, dtype=float)
        if keys.shape[0] != len(middles):
            raise ValueError(f"decode_weather: len(sol)={keys.shape[0]} != len(middles)={len(middles)}")
        ordered = [mid for _, mid in sorted(zip(keys, middles), key=lambda t: (float(t[0]), int(t[1])))]
        return [int(start_id)] + ordered + [int(end_id)]
    return decode_fn


def _deg2rad(d: float) -> float:
    return float(d) * np.pi / 180.0

def _segment_unit_vector_xy_m(a: Waypoint, b: Waypoint) -> np.ndarray:
    lat1 = float(a.position.lat)
    lon1 = float(a.position.lon)
    lat2 = float(b.position.lat)
    lon2 = float(b.position.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    lat_mean = 0.5 * (lat1 + lat2)
    meters_per_deg_lat = 111_139.0
    meters_per_deg_lon = 111_139.0 * float(np.cos(_deg2rad(lat_mean)))

    dy = dlat * meters_per_deg_lat
    dx = dlon * meters_per_deg_lon

    v = np.array([dx, dy], dtype=float)
    n = float(np.linalg.norm(v))
    if n <= 1e-12:
        return np.array([0.0, 0.0], dtype=float)
    return v / n

def _wind_vector_xy_mps(
    wind_speed_mps: float,
    wind_dir_deg: float,
    *,
    is_meteorological_from: bool = True,
) -> np.ndarray:
    theta = float(wind_dir_deg) % 360.0

    if is_meteorological_from:
        theta = (theta + 180.0) % 360.0
    angle = _deg2rad(90.0 - theta)
    return np.array([wind_speed_mps * float(np.cos(angle)), wind_speed_mps * float(np.sin(angle))], dtype=float)


def calculate_route_time_weather(
    route_ids: Sequence[int],
    graph: np.ndarray,
    id2idx: Mapping[int, int],
    points: Sequence[Waypoint],
    *,
    drone_airspeed_mps: float,
    is_meteorological_from: bool = True,
    min_progress_mps: float = 0.5,
) -> float:

    try:
        idx_path = [id2idx[int(r)] for r in route_ids]
    except KeyError:
        return np.inf

    total_t = 0.0
    for k in range(len(idx_path) - 1):
        ia = idx_path[k]
        ib = idx_path[k + 1]

        leg = float(graph[ia, ib])
        if not np.isfinite(leg) or leg <= 0:
            return np.inf

        a = points[ia]
        b = points[ib]

        u = _segment_unit_vector_xy_m(a, b)
        if float(np.linalg.norm(u)) <= 1e-12:
            return np.inf

        w = _wind_vector_xy_mps(a.wind_speed, a.wind_direction, is_meteorological_from=is_meteorological_from)
        w_along = float(np.dot(w, u))

        v_g = drone_airspeed_mps + w_along
        if not np.isfinite(v_g) or v_g <= float(min_progress_mps):
            return np.inf

        total_t += leg / v_g
    return float(total_t)



def build_weather_es(
    *,
    decode: Callable[[np.ndarray], Sequence[int]],
    graph: np.ndarray,
    points: Sequence[Waypoint],
    settings: AlgoSettings,
) -> Callable[[np.ndarray], float]:
    id2idx = build_id_index(points)
    is_meteo_from = bool(getattr(settings, "wind_is_meteorological_from", True))
    min_progress = float(getattr(settings, "min_progress_mps", 0.5))

    def objective(x: np.ndarray) -> float:
        sol = np.asarray(x, dtype=float)
        route = decode(sol)
        t = calculate_route_time_weather(
            route, graph, id2idx, points,
            drone_airspeed_mps=settings.speed_mps,
            is_meteorological_from=is_meteo_from,
            min_progress_mps=min_progress,
        )
        return float(t)

    return objective


def build_weather_ga(
    *,
    decode: Callable[[np.ndarray], Sequence[int]],
    graph: np.ndarray,
    points: Sequence[Waypoint],
    settings: AlgoSettings,
) -> Callable:
    id2idx = build_id_index(points)
    is_meteo_from = bool(getattr(settings, "wind_is_meteorological_from", True))
    min_progress = float(getattr(settings, "min_progress_mps", 0.5))

    def fitness_func(ga, sol, idx):
        sol = np.asarray(sol, dtype=float)
        route = decode(sol)
        t = calculate_route_time_weather(
            route, graph, id2idx, points,
            drone_airspeed_mps=settings.speed_mps,
            is_meteorological_from=is_meteo_from,
            min_progress_mps=min_progress,
        )

        if not np.isfinite(t):
            return -INFEASIBLE_COST

        # GA maximizes fitness -> minimize time by returning negative time
        return -float(t)

    return fitness_func
