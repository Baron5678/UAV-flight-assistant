from __future__ import annotations
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.app.interfaces import MissionRepository
from uav_assistant.domain.models import Mission as DomMission
from uav_assistant.infra.db.postgre.models import Mission as DbMission
from .convertors import MissionConvertor
from uav_assistant.infra.db.repos.validators import validate_id


class SqlAlchemyMissionRepository(MissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, mission_id: int) -> DomMission:
        validate_id(mission_id, "get", "Mission")
        res = await self.session.execute(select(DbMission).where(DbMission.id == mission_id))
        db_mission = res.scalar_one_or_none()
        if db_mission is None:
            raise ValueError(f"[get]: Mission {mission_id} not found")
        return MissionConvertor.to_domain(db_mission)

    async def create(self, mission_name: str | None) -> int:
        mission = DbMission(name=mission_name or "Mission")
        self.session.add(mission)
        await self.session.flush()
        return MissionConvertor.to_domain(mission).id

    async def delete(self, mission_id: int) -> None:
        validate_id(mission_id, "delete", "Mission")
        await self.session.execute(
            delete(DbMission).where(DbMission.id == mission_id)
        )

        await self.session.flush()

    async def get_all(self) -> list[DomMission]:
        res = await self.session.execute(
            select(DbMission).order_by(DbMission.id.asc())
        )
        db_missions = res.scalars().all()
        return [MissionConvertor.to_domain(m) for m in db_missions]

