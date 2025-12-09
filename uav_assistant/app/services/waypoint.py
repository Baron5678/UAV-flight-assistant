from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from uav_assistant.domain.models import Waypoint, GeoPoint, WaypointRole
from uav_assistant.app.interfaces import WaypointRepository


@dataclass
class AddWaypointCommand:
    name: str
    lat: float
    lon: float
    role: WaypointRole
    loss_chance: float = 0.2


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
            loss_chance=cmd.loss_chance,
        )

        stored = await self._waypoints.add(w)
        return stored

    async def get_all(self) -> list[Waypoint]:
        return await self._waypoints.get_all()

    async def reset(self) -> None:
        await self._waypoints.reset_all()

    async def delete(self, waypoint_id: int) -> None:
        await self._waypoints.delete(waypoint_id)
