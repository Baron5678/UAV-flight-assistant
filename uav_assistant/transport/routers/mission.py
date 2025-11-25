from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.cross.enums import Status
from uav_assistant.domain.models import Mission
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.transport.routers.models import (
    StartMissionRequest,
    StartMissionResponse,
)
from uav_assistant.infra.db.models import (
    Mission as DbMission,
    MissionWaypoint,
    Path as DbPath,
    PathWaypoint,
    Waypoint as DbWaypoint,
)
router = APIRouter(tags=["missions"])

@router.post("/start_mission", response_model=StartMissionResponse)
async def start_mission(
    body: StartMissionRequest,
    session: AsyncSession = Depends(get_session),
) -> StartMissionResponse:

    if body.start_waypoint_id not in body.waypoint_ids:
        raise HTTPException(
            status_code=400,
            detail="start_waypoint_id must be included in waypoint_ids",
        )
    if body.end_waypoint_id not in body.waypoint_ids:
        raise HTTPException(
            status_code=400,
            detail="end_waypoint_id must be included in waypoint_ids",
        )
    if body.start_waypoint_id == body.end_waypoint_id:
        raise HTTPException(
            status_code=400,
            detail="start_waypoint_id and end_waypoint_id must differ",
        )

    mission_repo = SqlAlchemyMissionRepository(session)

    mission = Mission(
        id=None,
        name=body.name,
        start_waypoint_id=body.start_waypoint_id,
        end_waypoint_id=body.end_waypoint_id,
        path_size=len(body.waypoint_ids),
        algo=body.algo.upper(),
        generations=body.generations,
        population_size=body.population_size,
        best_cost=0.0,
        status=Status.PENDING,
    )

    mission = await mission_repo.save(mission)
    for wp_id in body.waypoint_ids:
        session.add(MissionWaypoint(mission_id=mission.id, waypoint_id=wp_id))
    await session.flush()
    return StartMissionResponse(mission_id=mission.id)


@router.post("/reset_all")
async def reset_all(session: AsyncSession = Depends(get_session)):
    await session.execute(delete(PathWaypoint))
    await session.execute(delete(DbPath))
    await session.execute(delete(MissionWaypoint))
    await session.execute(delete(DbMission))
    await session.execute(delete(DbWaypoint))
    return {"status": "ok"}