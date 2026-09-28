from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.app.services.mission import MissionService, CancelMissionCommand
from uav_assistant.cross.enums import Status, ObjectiveFunction
from uav_assistant.domain.models import Mission
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.path import SqlAlchemyPathRepository
from uav_assistant.domain.models import Path as DomPath
from uav_assistant.transport.routers.http.models import (
    StartMissionRequest,
    StartMissionResponse,
    FinishMissionRequest, CancelMissionRequest
)
from uav_assistant.infra.db.postgre.models import (
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

    print(f"Objective: {body.objective}")

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
        objective=ObjectiveFunction(body.objective),
        keep_elitism=body.keep_elitism,
        k_tournament=body.k_tournament,
        mutation_probability=body.mutation_probability,
        sigma0=body.sigma0,
        seed=body.seed
    )


    mission = await mission_repo.add(mission)
    for wp_id in body.waypoint_ids:
        session.add(MissionWaypoint(mission_id=mission.id, waypoint_id=wp_id))
    await session.flush()
    await session.commit()  # ensures persisted
    return StartMissionResponse(mission_id=mission.id)

@router.post("/finish_mission")
async def finish_mission(
    body: FinishMissionRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    mission_repo = SqlAlchemyMissionRepository(session)
    path_repo = SqlAlchemyPathRepository(session)

    mission = await mission_repo.get(body.mission_id)

    final_path = DomPath(
        waypoint_ids=body.waypoint_ids,
        total_distance_m=body.total_distance_m,
        cost=body.best_cost,
    )

    saved_path = await path_repo.save_for_mission(
        mission_id=body.mission_id,
        path=final_path,
    )

    mission.best_cost = saved_path.cost
    mission.status = Status.COMPLETE
    await mission_repo.add(mission)

    return {"mission_id": mission.id}


@router.post("/cancel_mission")
async def cancel_mission(
    body: CancelMissionRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    mission_repo = SqlAlchemyMissionRepository(session)
    path_repo = SqlAlchemyPathRepository(session)
    service = MissionService(mission_repo, path_repo)

    await service.cancel_mission(CancelMissionCommand(mission_id=body.mission_id))

    return {"mission_id": body.mission_id}

@router.post("/reset_all")
async def reset_all(session: AsyncSession = Depends(get_session)):
    await session.execute(delete(PathWaypoint))
    await session.execute(delete(DbPath))
    await session.execute(delete(MissionWaypoint))
    await session.execute(delete(DbMission))
    await session.execute(delete(DbWaypoint))
    return {"status": "ok"}