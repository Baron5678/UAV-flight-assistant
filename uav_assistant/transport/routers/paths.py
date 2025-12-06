# uav_assistant/transport/routers/paths.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.infra.db.repos.path import SqlAlchemyPathRepository
from uav_assistant.infra.ga.path_optimizer import GAPathOptimizer, ESPathOptimizer
from uav_assistant.app.services.path import PathService
from uav_assistant.transport.routers.models import PathRequest, PathResponse

router = APIRouter()


@router.post("/path", response_model=PathResponse)
async def preview_path(
    body: PathRequest,
    session: AsyncSession = Depends(get_session),
) -> PathResponse:
    mission_repo = SqlAlchemyMissionRepository(session)
    waypoint_repo = SqlAlchemyWaypointRepository(session)

    mission = await mission_repo.get(body.mission_id)
    mission.generations = body.generations
    mission.population_size = body.population_size
    await mission_repo.add(mission)
    candidates = await waypoint_repo.get_for_mission(body.mission_id)
    optimizer = GAPathOptimizer()
    dom_path = await optimizer.optimize(
        mission=mission,
        drones=[],
        candidates=candidates,
    )

    id2wp = {w.id: w for w in candidates}
    coords = [
        (id2wp[i].position.lat, id2wp[i].position.lon)
        for i in dom_path.waypoint_ids
    ]

    return PathResponse(
        waypoint_ids=dom_path.waypoint_ids,
        waypoint_coords=coords,
        total_distance_m=dom_path.total_distance_m,
        best_cost=dom_path.cost,
        generations=body.generations,
        population_size=body.population_size,
        algo=body.algo,
    )
