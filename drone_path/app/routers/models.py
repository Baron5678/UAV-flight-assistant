from typing import Literal, List, Tuple
from pydantic import BaseModel
from drone_path.app.db.models import WaypointRole

COLOR_BY_ROLE = {"required": "red", "optional": "blue", "station": "green"}

class WaypointRequest(BaseModel):
    id: int = 0
    lon: float = 0.0
    lat: float = 0.0
    role: WaypointRole = WaypointRole.OPTIONAL
    name: str = ""
    visits: int = 2
    wind_speed: float = 4.0
    loss_chance: float = 0.2

class WaypointResponse(BaseModel):
    id: int
    lat: float
    lng: float
    role: str
    color: str
    name: str | None = None

class PathRequest(BaseModel):
    start_id: int
    end_id: int
    generations: int = 30
    population_size: int = 20

class PathResponse(BaseModel):
    waypoint_coords: List[Tuple[float, float]]
    best_cost: float
