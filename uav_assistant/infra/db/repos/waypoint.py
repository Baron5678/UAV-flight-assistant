from __future__ import annotations

from typing import Sequence

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uav_assistant.domain.models import Waypoint as DomWaypoint
from uav_assistant.app.interfaces import WaypointRepository
from uav_assistant.infra.db.postgre.models import Waypoint as DbWaypoint
from uav_assistant.infra.db.repos.convertors import WaypointConvertor
from uav_assistant.infra.db.repos.validators import validate_id


class SqlAlchemyWaypointRepository(WaypointRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, waypoint_id: int) -> DomWaypoint:
        validate_id(waypoint_id, "get", "Waypoint")
        result = await self._session.execute(
            select(DbWaypoint)
            .options(selectinload(DbWaypoint.mission))
            .where(DbWaypoint.id == waypoint_id)
        )
        db_waypoint = result.scalar_one_or_none()
        if db_waypoint is None:
            raise ValueError(f"[get]: Waypoint with id {waypoint_id} not found")
        return WaypointConvertor.to_domain(db_waypoint)

    async def create(self, mission_id: int, waypoint: DomWaypoint) -> int:
        validate_id(mission_id, "create", "Mission")
        db_waypoint = WaypointConvertor.to_db(waypoint, mission_id)
        self._session.add(db_waypoint)
        await self._session.flush()
        return db_waypoint.id

    async def update(self, waypoint: DomWaypoint) -> None:
        validate_id(waypoint.id, "update", "Waypoint")
        waypoint_result = await self._session.execute(
            select(DbWaypoint).where(DbWaypoint.id == waypoint.id)
        )
        db_waypoint = waypoint_result.scalar_one_or_none()

        if db_waypoint is None:
            raise ValueError(f"[update]: Waypoint with id {waypoint.id} not found")

        candidate_values = {
            "name": waypoint.name,
            "latitude": waypoint.lat,
            "longitude": waypoint.lon,
            "role": waypoint.role.value,
            "wind_speed": waypoint.wind_speed,
            "wind_direction": waypoint.wind_direction,
        }
        values = {
            field: value
            for field, value in candidate_values.items()
            if getattr(db_waypoint, field) != value
        }

        if values:
            await self._session.execute(
                update(DbWaypoint)
                .where(DbWaypoint.id == waypoint.id)
                .values(**values)
            )
        await self._session.flush()

    async def delete(self, waypoint_id: int) -> None:
        validate_id(waypoint_id, "delete", "Waypoint")
        await self._session.execute(
            delete(DbWaypoint).where(DbWaypoint.id == waypoint_id)
        )
        await self._session.flush()

    async def get_all_by_mission(self, mission_id: int) -> Sequence[DomWaypoint]:
        validate_id(mission_id, "get_all", "Mission")
        result = await self._session.execute(
            select(DbWaypoint)
            .options(selectinload(DbWaypoint.mission))
            .where(DbWaypoint.mission_id == mission_id)
        )
        return [WaypointConvertor.to_domain(w) for w in result.scalars().all()]

    async def reset_all(self) -> None:
        await self._session.execute(delete(DbWaypoint))
        await self._session.flush()
