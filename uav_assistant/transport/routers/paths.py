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
async def generate_path(
    body: PathRequest,
    session: AsyncSession = Depends(get_session),
) -> PathResponse:
    mission_repo = SqlAlchemyMissionRepository(session)
    waypoint_repo = SqlAlchemyWaypointRepository(session)
    path_repo = SqlAlchemyPathRepository(session)
    # optimizer = GAPathOptimizer()

    mission = await mission_repo.get(body.mission_id)

    # choose optimizer based on mission.algo
    algo = (mission.algo or "GA").upper()
    if algo == "ES":
        optimizer = ESPathOptimizer()
    else:
        optimizer = GAPathOptimizer()

    service = PathService(
        mission_repo=mission_repo,
        waypoint_repo=waypoint_repo,
        path_repo=path_repo,
        optimizer=optimizer,
    )

    try:
        path = await service.generate_best_path_for_mission(mission_id=body.mission_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    candidates = await waypoint_repo.get_for_mission(body.mission_id)
    id2wp = {w.id: w for w in candidates}

    coords: list[tuple[float, float]] = []
    for wp_id in path.waypoint_ids:
        wp = id2wp.get(wp_id)
        if wp is None:
            continue
        coords.append((wp.position.lat, wp.position.lon))

    return PathResponse(
        mission_id=body.mission_id,
        waypoint_coords=coords,
        total_distance_m=float(path.total_distance_m or 0.0),
        cost=float(path.cost or 0.0),
    )
