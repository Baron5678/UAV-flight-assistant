from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Literal
from uav_assistant.cross.enums import WaypointRole

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
    objective: str = "DISTANCE"
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

class DroneRequest(BaseModel):
    battery_capacity_wh: float = 2000.0
    wh_per_km: float = 10.0
    reserve_ratio: float = 0.2

class PathRequest(BaseModel):
    mission_id: int
    generations: int = 30
    population_size: int = 20
    algo: str = "GA"
    drone: DroneRequest | None = None

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

class UnreachableRequiredResponse(BaseModel):
    required_id: int
    nearest_station_id: int
    dist_required_to_station_m: float
    max_leg_m: float
    nearest_required_id: Optional[int] = None
    dist_required_to_required_m: Optional[float] = None

class PreRunReportResponse(BaseModel):
    type: Literal["diagnostic"] = "diagnostic"
    feasible: bool
    max_leg_m: float
    problems: List[UnreachableRequiredResponse]

class RouteEnergyFailureResponse(BaseModel):
    from_id: int
    to_id: int
    dist_m: float
    soc_wh: float
    reserve_wh: float
    needed_wh: float
    deficit_wh: float
    deficit_m: float

class PostRunRouteValidationResponse(BaseModel):
    type: Literal["route_validation"] = "route_validation"
    feasible: Literal[False] = False
    objective: Literal["ENERGY"] = "ENERGY"
    failure: RouteEnergyFailureResponse

class PathSummaryRowResponse(BaseModel):
    generation: int
    cost: float
    total_distance_m: float


class PathSummaryStatsResponse(BaseModel):
    best_cost: float
    first_cost: float
    min_cost: float
    max_cost: float
    avg_cost: float
    min_total_distance_m: float
    max_total_distance_m: float
    avg_total_distance_m: float
    improvement_abs: float
    improvement_pct: float
    improving_generations: int
    last_improvement_generation: int | None
    max_stagnation_generations: int


class PathSummaryResponse(BaseModel):
    mission_id: int
    paths: List[PathSummaryRowResponse]
    stats: PathSummaryStatsResponse