from __future__ import annotations

from typing import Literal, List, Tuple, Union
from pydantic import BaseModel, Field


ObjectiveName = Literal["DISTANCE", "ENERGY", "WEATHER"]
AlgoName = Literal["GA", "ES"]


class DroneMessage(BaseModel):
    battery_capacity_wh: float
    wh_per_km: float
    reserve_ratio: float = 0.2


class PathMessage(BaseModel):
    mission_id: int
    algo: AlgoName = "GA"
    objective_function: ObjectiveName = "DISTANCE"

    generations: int = Field(..., gt=0)
    population_size: int = Field(..., gt=0)
    seed: int | None = None
    mutation_probability: float | None = None
    keep_elitism: int | None = None
    k_tournament: int | None = None
    sigma0: float | None = None

    drone: DroneMessage
    station_threshold: float = 0.5
    station_penalty_m: float = 200.0


class GenerationMessage(BaseModel):
    type: Literal["generation"] = "generation"
    algo: str
    generation: int
    cost: float
    waypoint_ids: List[int]
    waypoint_coords: List[Tuple[float, float]]
    is_feasible: bool
    message: str


class ErrorGenerationMessage(BaseModel):
    type: str
    feasible: bool
    message: str


class FinalMessage(BaseModel):
    type: Literal["final"] = "final"
    algo: str
    generation: int
    cost: float
    total_distance_m: float
    waypoint_ids: List[int]
    waypoint_coords: List[Tuple[float, float]]
    is_feasible: bool
    message: str


WSMessage = Union[GenerationMessage, FinalMessage]
