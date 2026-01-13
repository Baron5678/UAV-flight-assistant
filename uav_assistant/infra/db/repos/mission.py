from __future__ import annotations

from imaplib import Literal
from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.cross.enums import Status, ObjectiveFunction
from uav_assistant.cross.parser import parse_literal
from uav_assistant.domain.models import Mission
from uav_assistant.app.interfaces import MissionRepository
from uav_assistant.infra.db.models import Mission as DbMission, MissionWaypoint
from uav_assistant.infra.objective_functions.objectives import Objectives


def to_domain(db: DbMission) -> Mission:
    return Mission(
        id=db.id,
        name=db.name,
        start_waypoint_id=db.start_waypoint_id,
        end_waypoint_id=db.end_waypoint_id,
        path_size=db.path_size,
        algo=db.algo,
        generations=db.generations,
        population_size=db.population_size,
        best_cost=db.best_cost,
        status=Status(db.status),
        objective=ObjectiveFunction(db.objective),
    )


class SqlAlchemyMissionRepository(MissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, mission_id: int) -> Mission:
        res = await self.session.execute(select(DbMission).where(DbMission.id == mission_id))
        db_mission = res.scalar_one_or_none()
        if db_mission is None:
            raise ValueError(f"Mission {mission_id} not found")
        return to_domain(db_mission)

    async def add(self, mission: Mission) -> Mission:
        if mission.id is None:
            mission = DbMission(
                name=mission.name,
                start_waypoint_id=mission.start_waypoint_id,
                end_waypoint_id=mission.end_waypoint_id,
                path_size=mission.path_size,
                algo=mission.algo,
                generations=mission.generations,
                population_size=mission.population_size,
                best_cost=mission.best_cost or 0.0,
                status=mission.status,
                objective=mission.objective
            )
            self.session.add(mission)
            await self.session.flush()
            return to_domain(mission)

        res = await self.session.execute(select(DbMission).where(DbMission.id == mission.id))
        db_mission = res.scalar_one_or_none()
        if db_mission is None:
            raise ValueError(f"Mission {db_mission.id} not found")

        db_mission.name = mission.name
        db_mission.start_waypoint_id = mission.start_waypoint_id
        db_mission.end_waypoint_id = mission.end_waypoint_id
        db_mission.k_total = mission.path_size
        db_mission.algo = mission.algo
        db_mission.generations = mission.generations
        db_mission.population_size = mission.population_size
        db_mission.best_cost = mission.best_cost or 0.0
        db_mission.status = mission.status
        db_mission.objective = mission.objective

        await self.session.flush()
        return to_domain(db_mission)

    async def get_all(self) -> list[Mission]:
        res = await self.session.execute(
            select(DbMission).order_by(DbMission.id.asc())
        )
        db_missions = res.scalars().all()
        return [to_domain(m) for m in db_missions]

    async def set_best(self, mission_id: int, path, cost: float) -> None:
        res = await self.session.execute(select(DbMission).where(DbMission.id == mission_id))
        db_mission = res.scalar_one_or_none()
        if db_mission is None:
            raise ValueError(f"Mission {mission_id} not found")
        db_mission.best_cost = cost
        db_mission.status = Status.COMPLETE
        await self.session.flush()

    async def delete(self, mission_id: int) -> None:
        await self.session.execute(
            delete(MissionWaypoint).where(MissionWaypoint.mission_id == mission_id)
        )

        await self.session.execute(
            delete(DbMission).where(DbMission.id == mission_id)
        )

        await self.session.flush()
