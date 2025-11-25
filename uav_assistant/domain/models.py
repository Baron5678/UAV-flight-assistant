# uav_assistant/domain/models.py

from __future__ import annotations
from dataclasses import dataclass
from uav_assistant.cross.enums import WaypointRole, Status
from typing import List, Optional


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
    best_cost: Optional[float] = None
    status: Status = Status.PENDING

