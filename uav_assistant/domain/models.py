
from __future__ import annotations

from dataclasses import dataclass
from uav_assistant.cross.enums import WaypointRole, Status, ObjectiveFunction
from typing import List, Optional, Literal, Sequence

@dataclass(frozen=True)
class GeoPoint:
    lat: float
    lon: float

@dataclass
class Waypoint:
    id: int
    name: str
    position: GeoPoint
    role: WaypointRole
    wind_speed: float
    wind_direction: float
    loss_chance: float = 0.2

@dataclass
class Path:
    waypoint_ids: List[int]
    total_distance_m: Optional[float] = None
    cost: Optional[float] = None

@dataclass
class Drone:
    id: int
    name: str
    speed_mps: float
    payload_kg: float
    battery_capacity_wh: Optional[float] = None
    mass_kg: Optional[float] = None
    per_meter_wh: Optional[float] = None


@dataclass
class Mission:
    id: Optional[int]
    name: Optional[str]
    start_waypoint_id: int
    end_waypoint_id: int
    path_size: int
    algo: str
    generations: int
    population_size: int
    seed: Optional[int]
    mutation_probability: Optional[float]
    keep_elitism: Optional[int]
    k_tournament: Optional[int]
    sigma0: Optional[float]
    best_cost: Optional[float]
    objective: ObjectiveFunction = ObjectiveFunction.DISTANCE
    status: Status = Status.PENDING

@dataclass
class AlgoSettings:
    generations: int
    population_size: int
    seed: Optional[int]
    mutation_probability: Optional[float]
    keep_elitism: Optional[int]
    k_tournament: Optional[int]
    sigma0: Optional[float]
    battery_wh: float
    per_meter_wh: float
    speed_mps: float
    reserve_ratio: float
    station_threshold: float
    station_penalty_m: float
    objective: str

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

@dataclass(frozen=True)
class PathSummary:
    mission_id: int
    generation: int
    cost: float
    total_distance_m: float

@dataclass(frozen=True)
class PathSummaryStats:
    min_cost: float
    max_cost: float
    avg_cost: float
    min_total_distance_m: float
    max_total_distance_m: float
    avg_total_distance_m: float
    best_cost: float
    first_cost: float
    improvement_abs: float
    improvement_pct: float
    improving_generations: int
    last_improvement_generation: int | None
    max_stagnation_generations: int