
from __future__ import annotations

import math
from dataclasses import dataclass
from uav_assistant.cross.enums import WaypointRole, Status, ObjectiveFunction
from typing import List, Optional, Sequence

from uav_assistant.domain.metrics import RADIUS_EARTH_M


@dataclass
class Mission:
    id: Optional[int]
    name: Optional[str]
    status: Status = Status.PENDING


@dataclass
class AlgorithmConfiguration:
    mission: Mission
    algo: str
    objective: ObjectiveFunction
    generations: int
    population_size: int
    seed: int


@dataclass
class Waypoint:
    id: int
    mission: Mission
    name: str
    lat: float
    lon: float
    role: WaypointRole
    wind_speed: float
    wind_direction: float

    def distance_to(self, point: Waypoint) -> float:
        lat1, lon1 = math.radians(self.lat), math.radians(self.lon)
        lat2, lon2 = math.radians(point.lat), math.radians(point.lon)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return RADIUS_EARTH_M * c


@dataclass
class Path:
    waypoint_ids: List[int]
    generation: int
    distance_m: float
    cost: float


@dataclass
class Drone:
    name: str
    speed: float
    battery_capacity_wh: float
    per_meter_wh: float


@dataclass
class GAConfiguration:
    config: AlgorithmConfiguration
    mutation_probability: float
    keep_elitism: int
    k_tournament: int


@dataclass
class ESConfiguration:
    config: AlgorithmConfiguration
    sigma0: float


@dataclass
class MissionOutcome:
    config: AlgorithmConfiguration
    first_cost: float
    best_cost: float
    min_cost: float
    max_cost: float
    avg_cost: float
    improvement_abs: float
    improvement_pct: float
    improving_generations: int
    last_improvement_generation: int
    max_stagnation_generations: int
    min_total_distance_m: float
    max_total_distance_m: float
    avg_total_distance_m: float

@dataclass
class OptimizerStep:
    generation: int
    cost: float
    waypoint_ids: Sequence[int]


@dataclass
class OptimizerFinal:
    algo: str
    generations: int
    cost: float
    waypoint_ids: Sequence[int]
    total_distance_m: float


@dataclass(frozen=True)
class OptimizerError:
    type: str
    feasible: bool
    problem: str
