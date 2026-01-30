from __future__ import annotations
from pydantic import BaseModel
from typing import List, Tuple
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
    seed: int = 127
    mutation_probability: float = 0.1
    keep_elitism: int = 5
    k_tournament: int = 3
    sigma0: float = 0.25


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
    speed_mps: float = 20.0
    reserve_ratio: float = 0.2


class PathRequest(BaseModel):
    mission_id: int
    generations: int = 30
    population_size: int = 20
    algo: str = "GA"
    seed: int | None = None
    mutation_probability: float | None = None
    keep_elitism: int | None = None
    k_tournament: int | None = None
    sigma0: float | None = None
    drone: DroneRequest | None = None

class PathResponse(PathMeta):
    waypoint_coords: List[Tuple[float, float]]

class WaypointRequest(BaseModel):
    lon: float = 0.0
    lat: float = 0.0
    role: WaypointRole = WaypointRole.REQUIRED
    wind_speed: float = 0.0
    wind_direction: float = 0.0
    name: str = ""
    loss_chance: float = 0.2


class WaypointResponse(BaseModel):
    id: int
    lat: float
    lng: float
    role: str
    wind_speed: float
    wind_direction: float
    color: str
    name: str | None = None

class RestoreWaypointsResponse(BaseModel):
    mission_id: int
    path_id: int
    waypoints: List[WaypointResponse]

class OptimizerErrorResponse(BaseModel):
    type: str
    feasible: bool
    message: str


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
