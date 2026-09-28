from __future__ import annotations

from typing import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.app.interfaces import DroneRepository
from uav_assistant.domain.models import Drone as DomDrone
from uav_assistant.infra.db.postgre.models import Drone as DbDrone
from uav_assistant.infra.db.repos.convertors import DroneConvertor
from uav_assistant.infra.db.repos.utils import patch_update
from uav_assistant.infra.db.repos.validators import validate_id


class SqlAlchemyDroneRepository(DroneRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, drone_id: int) -> DomDrone:
        validate_id(drone_id, "get", "Drone")
        result = await self._session.execute(
            select(DbDrone).where(DbDrone.id == drone_id)
        )
        db_drone = result.scalar_one_or_none()
        if db_drone is None:
            raise ValueError(f"[get]: Drone with id {drone_id} not found")
        return DroneConvertor.to_domain(db_drone)

    async def create(self, drone: DomDrone) -> int:
        db_drone = DroneConvertor.to_db(drone)
        self._session.add(db_drone)
        await self._session.flush()
        return db_drone.id

    async def update(self, drone_id: int, drone: DomDrone) -> None:
        validate_id(drone_id, "update", "Drone")
        result = await self._session.execute(
            select(DbDrone).where(DbDrone.id == drone_id)
        )
        db_drone = result.scalar_one_or_none()
        if db_drone is None:
            raise ValueError(f"[update]: Drone with id {drone_id} not found")

        values = patch_update(
            DbDrone.__mapper__.columns,
            {"id"},
            db_drone,
            drone,
        )
        if values is None:
            return

        await self._session.execute(
            update(DbDrone)
            .where(DbDrone.id == drone_id)
            .values(**values)
        )
        await self._session.flush()

    async def delete(self, drone_id: int) -> None:
        validate_id(drone_id, "delete", "Drone")
        await self._session.execute(
            delete(DbDrone).where(DbDrone.id == drone_id)
        )
        await self._session.flush()

    async def get_all(self) -> Sequence[DomDrone]:
        result = await self._session.execute(
            select(DbDrone).order_by(DbDrone.id.asc())
        )
        return [
            DroneConvertor.to_domain(db_drone)
            for db_drone in result.scalars().all()
        ]
