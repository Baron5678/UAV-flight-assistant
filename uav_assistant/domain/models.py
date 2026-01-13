# uav_assistant/domain/models.py

from __future__ import annotations

import string
from dataclasses import dataclass

from pydantic import BaseModel
from pydantic_core.core_schema import dataclass_args_schema

from uav_assistant.cross.enums import WaypointRole, Status, ObjectiveFunction
from typing import List, Optional, Literal, Sequence, Tuple, Union


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

@dataclass(frozen=True)
class PathSummary:
    mission_id: int
    generation: int
    cost: float
    total_distance_m: float

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
    best_cost: Optional[float]
    objective: ObjectiveFunction
    status: Status = Status.PENDING

@dataclass
class AlgoSettings:
    generations: int
    population_size: int
    battery_wh: float
    per_meter_wh: float
    reserve_ratio: float
    station_threshold: float
    station_penalty_m: float
    objective: Literal["DISTANCE", "ENERGY", "WEATHER"] = "DISTANCE"

@dataclass(frozen=True)
class OptimizerStep:
    generation: int
    cost: float
    waypoint_ids: Sequence[int]


@dataclass(frozen=True)
class OptimizerFinal:
    algo: str
    generations: int
    cost: float
    waypoint_ids: Sequence[int]
    total_distance_m: float

@dataclass(frozen=True)
class OptimizerDiagnostic:
    type: Literal["diagnostic"]
    feasible: bool
    max_leg_m: float
    problems: Sequence[UnreachableRequired]

@dataclass(frozen=True)
class UnreachableRequired:
    required_id: int
    nearest_station_id: int
    dist_required_to_station_m: float
    max_leg_m: float
    nearest_required_id: Optional[int]
    dist_required_to_required_m: Optional[float]

@dataclass(frozen=True)
class PreRunReport:
    feasible: bool
    max_leg_m: float
    problems: list[UnreachableRequired]

@dataclass(frozen=True)
class RouteEnergyFailure:
    from_id: int
    to_id: int
    dist_m: float
    soc_wh: float
    reserve_wh: float
    needed_wh: float  # energy for the leg

@dataclass(frozen=True)
class PostRunReport:
    feasible: bool
    total_dist_m: float
    station_visits: int
    failure: Optional[RouteEnergyFailure] = None

@dataclass(frozen=True)
class OptimizerRouteValidation:
    type: Literal["route_validation"]  # distinguishable in WS/HTTP
    objective: str                     # e.g. "ENERGY"
    feasible: bool
    report: PostRunReport

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