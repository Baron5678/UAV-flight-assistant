from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from uav_assistant.infra.db.models import WaypointRole

COLOR_BY_ROLE = {"required": "red", "optional": "blue", "station": "green"}

class PathMeta(BaseModel):
    waypoint_ids: List[int]
    total_distance_m: float
    best_cost: float
    generations: int
    population_size: int
    algo: str = "GA"

class StartMissionRequest(BaseModel):
    name: str = "default_mission"
    start_waypoint_id: int = -1
    end_waypoint_id: int = -1
    waypoint_ids: List[int]
    generations: int = 0
    population_size: int = 0
    algo: str = "GA"

class StartMissionResponse(BaseModel):
    mission_id: int

class FinishMissionRequest(PathMeta):
    mission_id: int

class CancelMissionRequest(BaseModel):
    mission_id: int


class DeleteWaypointRequest(BaseModel):
    waypoint_id: int

class PathRequest(BaseModel):
    mission_id: int
    generations: int = 30
    population_size: int = 20
    algo: str = "GA"

class PathResponse(PathMeta):
    waypoint_coords: List[Tuple[float, float]]

class WaypointRequest(BaseModel):
    lon: float = 0.0
    lat: float = 0.0
    role: WaypointRole = WaypointRole.REQUIRED
    name: str = ""
    loss_chance: float = 0.2

class WaypointResponse(BaseModel):
    id: int
    lat: float
    lng: float
    role: str
    color: str
    name: str | None = None

