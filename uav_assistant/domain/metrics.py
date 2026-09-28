from __future__ import annotations
from typing import Sequence

import numpy as np

from .models import  Waypoint

RADIUS_EARTH_M = 6_371_000.0


def _lat_lon(point) -> tuple[float, float]:
    position = getattr(point, "position", None)
    if position is not None:
        return float(position.lat), float(position.lon)
    return float(point.lat), float(point.lon)


def distance_m(a, b) -> float:
    lat1, lon1 = _lat_lon(a)
    lat2, lon2 = _lat_lon(b)

    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)

    haversine = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    )
    central_angle = 2 * np.arcsin(np.sqrt(haversine))
    return float(RADIUS_EARTH_M * central_angle)

def travel_time_s(distance_m_val: float, speed_mps: float) -> float:
    if speed_mps <= 0:
        raise ValueError("speed_mps must be positive")
    return distance_m_val / speed_mps


def estimate_energy_wh(distance_m_val: float, per_meter_wh: float) -> float:
    if per_meter_wh < 0:
        raise ValueError("per_meter_wh must be non-negative")
    return distance_m_val * per_meter_wh


def build_distance_matrix(points: list["Waypoint"]) -> np.ndarray:
    n = len(points)
    graph = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            d = distance_m(points[i], points[j])
            graph[i, j] = graph[j, i] = d
    return graph

def build_id_index(points) -> dict[int, int]:
    return {p.id: i for i, p in enumerate(points)}

def build_id2wp(points: Sequence[Waypoint]) -> dict[int, Waypoint]:
    return {p.id: p for p in points}
