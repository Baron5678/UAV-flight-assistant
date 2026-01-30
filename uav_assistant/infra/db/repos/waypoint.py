from __future__ import annotations
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.domain.models import Waypoint as DomWaypoint, GeoPoint, WaypointRole
from uav_assistant.app.interfaces import WaypointRepository
from uav_assistant.infra.db.models import Waypoint as DbWaypoint, MissionWaypoint

def to_domain(db_wp: DbWaypoint) -> DomWaypoint:
    return DomWaypoint(
        id=db_wp.id,
        name=db_wp.name,
        position=GeoPoint(lat=db_wp.latitude, lon=db_wp.longitude),
        role=WaypointRole(db_wp.role.value if hasattr(db_wp.role, "value") else db_wp.role),
        wind_speed=db_wp.wind_speed,
        wind_direction=db_wp.wind_direction,
    )

class SqlAlchemyWaypointRepository(WaypointRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, waypoint: DomWaypoint) -> DomWaypoint:
        db_wp = DbWaypoint(
            name=waypoint.name,
            latitude=waypoint.position.lat,
            longitude=waypoint.position.lon,
            role=waypoint.role,
            wind_speed=waypoint.wind_speed,
            wind_direction=waypoint.wind_direction,
        )
        self.session.add(db_wp)
        await self.session.flush()
        return to_domain(db_wp)

    async def get_all(self) -> list[DomWaypoint]:
        stmt = select(DbWaypoint)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [to_domain(w) for w in rows]

    async def get_for_mission(self, mission_id: int) -> list[DomWaypoint]:
        stmt = (
            select(DbWaypoint)
            .join(MissionWaypoint, MissionWaypoint.waypoint_id == DbWaypoint.id)
            .where(MissionWaypoint.mission_id == mission_id)
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [to_domain(w) for w in rows]

    async def delete(self, waypoint_id: int) -> None:
        await self.session.execute(
            delete(DbWaypoint).where(DbWaypoint.id == waypoint_id)
        )
        await self.session.flush()

    async def reset_all(self) -> None:
        await self.session.execute(delete(DbWaypoint))
