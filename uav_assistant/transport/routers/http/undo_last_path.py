from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.domain.metrics import build_id2wp
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.path import SqlAlchemyPathRepository
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.transport.routers.http.models import RestoreWaypointsResponse, WaypointResponse
from uav_assistant.transport.routers.http.waypoint import COLOR_BY_ROLE

router = APIRouter()

@router.get("/missions/{mission_id}/restore_waypoints", response_model=RestoreWaypointsResponse)
async def restore_waypoints(
    mission_id: int,
    session: AsyncSession = Depends(get_session),
) -> RestoreWaypointsResponse:
    path_repo = SqlAlchemyPathRepository(session)
    waypoint_repo = SqlAlchemyWaypointRepository(session)

    path_id = await path_repo.get_latest_path_id(mission_id)
    if path_id is None:
        raise HTTPException(status_code=404, detail="No saved path for this mission")

    ordered_ids = await path_repo.get_ordered_waypoint_ids(path_id)
    if not ordered_ids:
        raise HTTPException(status_code=404, detail="Saved path has no waypoints")

    candidates = await waypoint_repo.get_for_mission(mission_id)
    id2wp = build_id2wp(candidates)
    try:
        waypoints = [
            WaypointResponse(
                id=i,
                lat=float(id2wp[i].position.lat),
                lng=float(id2wp[i].position.lon),
                role=str(id2wp[i].role),
                color=COLOR_BY_ROLE.get(id2wp[i].role)
            )
            for i in ordered_ids
        ]
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Saved path contains unknown waypoint id: {e}") from e

    return RestoreWaypointsResponse(
        mission_id=mission_id,
        path_id=path_id,
        waypoints=waypoints,
    )
