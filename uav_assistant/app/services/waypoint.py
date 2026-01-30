from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, List
from uav_assistant.domain.models import Waypoint, GeoPoint, WaypointRole
from uav_assistant.app.interfaces import WaypointRepository
import math
import random

WARSAW_CENTER_LAT = 52.2297
WARSAW_CENTER_LON = 21.0122
WARSAW_SIGMA_M = 10000.0

@dataclass
class AddWaypointCommand:
    name: str
    lat: float
    lon: float
    role: WaypointRole
    wind_speed: float
    wind_direction: float

def _meters_to_deg_lat(m: float) -> float:
    return m / 111_139.0


def _meters_to_deg_lon(m: float, lat_deg: float) -> float:
    cos_lat = math.cos(math.radians(lat_deg))
    if cos_lat < 1e-6:
        raise ValueError("Latitude too close to poles for stable lon scaling.")
    return m / (111_139.0 * cos_lat)

class WaypointService:
    def __init__(self, waypoint_repo: WaypointRepository) -> None:
        self._waypoints = waypoint_repo

    async def add_waypoint(self, cmd: AddWaypointCommand) -> Waypoint:
        if not (-90.0 <= cmd.lat <= 90.0 and -180.0 <= cmd.lon <= 180.0):
            raise ValueError("Latitude/longitude out of bounds.")

        if cmd.role in (WaypointRole.START, WaypointRole.END):
            current = await self._waypoints.get_all()
            for w in current:
                if w.role == cmd.role:
                    raise ValueError(f"There is already a {cmd.role.value} waypoint.")

        w = Waypoint(
            id=0,
            name=cmd.name,
            position=GeoPoint(lat=cmd.lat, lon=cmd.lon),
            role=cmd.role,
            wind_speed=cmd.wind_speed,
            wind_direction=cmd.wind_direction,
        )

        stored = await self._waypoints.add(w)
        return stored

    async def add_random_required(self, size: int, *, seed: int = 42) -> List[Waypoint]:
        if size <= 0:
            return []

        rng = random.Random(int(seed))
        res: List[Waypoint] = []

        for i in range(size):
            dx_m = rng.gauss(0.0, WARSAW_SIGMA_M)
            dy_m = rng.gauss(0.0, WARSAW_SIGMA_M)

            lat = WARSAW_CENTER_LAT + _meters_to_deg_lat(dy_m)
            lon = WARSAW_CENTER_LON + _meters_to_deg_lon(dx_m, WARSAW_CENTER_LAT)

            wind_speed = max(0.0, rng.gauss(4.0, 2.0))
            wind_speed = min(wind_speed, 10.0)

            wind_direction = rng.uniform(0.0, 360.0)

            wp = await self.add_waypoint(
                AddWaypointCommand(
                    name=f"req_norm_{seed}_{i}",
                    lat=lat,
                    lon=lon,
                    role=WaypointRole.REQUIRED,
                    wind_speed=wind_speed,
                    wind_direction=wind_direction,
                )
            )
            res.append(wp)


        return res

    async def get_all(self) -> list[Waypoint]:
        return await self._waypoints.get_all()

    async def reset(self) -> None:
        await self._waypoints.reset_all()

    async def delete(self, waypoint_id: int) -> None:
        await self._waypoints.delete(waypoint_id)
