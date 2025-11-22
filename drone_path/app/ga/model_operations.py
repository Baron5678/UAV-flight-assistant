import math
import numpy as np
from drone_path.app.db.models import Waypoint

RADIUS_EARTH_M = 6371000.0

def as_tuple(self):
    return self.x, self.y

def distance_h(w1: "Waypoint", w2: "Waypoint") -> float:
    lon1, lat1 = math.radians(w1.longitude), math.radians(w1.latitude)
    lon2, lat2 = math.radians(w2.longitude), math.radians(w2.latitude)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return RADIUS_EARTH_M * c

def build_distance_matrix(points: list["Waypoint"]) -> np.ndarray:
    n = len(points)
    graph = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            d = distance_h(points[i],points[j])
            graph[i, j] = graph[j, i] = d
    return graph