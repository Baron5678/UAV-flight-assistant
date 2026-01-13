from __future__ import annotations
from typing import Sequence, Dict, List
import math

import numpy as np

from .models import GeoPoint, Waypoint

RADIUS_EARTH_M = 6_371_000.0

def distance_m(p1: GeoPoint, p2: GeoPoint) -> float:
    """
    Haversine distance between two geographic coordinates in meters.
    """
    lon1, lat1 = math.radians(p1.lon), math.radians(p1.lat)
    lon2, lat2 = math.radians(p2.lon), math.radians(p2.lat)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return RADIUS_EARTH_M * c

def distance_h(w1: "Waypoint", w2: "Waypoint") -> float:
    lon1, lat1 = math.radians(w1.position.lon), math.radians(w1.position.lat)
    lon2, lat2 = math.radians(w2.position.lon), math.radians(w2.position.lat)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return RADIUS_EARTH_M * c


def travel_time_s(distance_m_val: float, speed_mps: float) -> float:
    if speed_mps <= 0:
        raise ValueError("speed_mps must be positive")
    return distance_m_val / speed_mps


def estimate_energy_wh(distance_m_val: float, per_meter_wh: float) -> float:
    return distance_m_val * per_meter_wh


def mse(y: Sequence[float], y_predicted: Sequence[float]) -> float:
    if len(y) != len(y_predicted):
        raise ValueError("y and y_predicted must have the same length")

    if not y:
        return 0.0

    err_sum = 0.0
    for actual, pred in zip(y, y_predicted):
        diff = actual - pred
        err_sum += diff * diff

    return err_sum / len(y)


def coords_by_id(waypoints: Sequence[Waypoint]) -> Dict[int, GeoPoint]:
    return {w.id: w.position for w in waypoints}


def build_distance_matrix(points: list["Waypoint"]) -> np.ndarray:
    n = len(points)
    graph = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            d = distance_h(points[i],points[j])
            graph[i, j] = graph[j, i] = d
    return graph

def build_id_index(points) -> dict[int, int]:
    return {p.id: i for i, p in enumerate(points)}

def build_id2wp(points: Sequence[Waypoint]) -> dict[int, Waypoint]:
    return {p.id: p for p in points}
