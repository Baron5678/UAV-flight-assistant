from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.app.services.waypoint import WaypointService, AddWaypointCommand
from uav_assistant.cross.enums import WaypointRole
from uav_assistant.transport.routers.http.models import WaypointRequest, WaypointResponse, DeleteWaypointRequest

router = APIRouter()
COLOR_BY_ROLE = {
    "REQUIRED": "red",
    "START": "blue",
    "END": "black",
    "STATION": "green",
}

@router.post("/add_point", response_model=WaypointResponse)
async def add_point(
    body: WaypointRequest,
    session: AsyncSession = Depends(get_session),
) -> WaypointResponse:
    repo = SqlAlchemyWaypointRepository(session)
    service = WaypointService(repo)

    cmd = AddWaypointCommand(
        name=body.name,
        lat=body.lat,
        lon=body.lon,
        role=WaypointRole(body.role),
        wind_speed=body.wind_speed,
        wind_direction=body.wind_direction
    )

    wp = await service.add_waypoint(cmd)
    role_str = wp.role

    return WaypointResponse(
        id=wp.id,
        lat=wp.position.lat,
        lng=wp.position.lon,
        role=role_str,
        wind_speed=wp.wind_speed,
        wind_direction=wp.wind_direction,
        color=COLOR_BY_ROLE.get(role_str, "blue"),
        name=wp.name,
    )

@router.post("/add_waypoints", response_model=List[WaypointResponse])
async def add_waypoints(
    size: int = Query(..., ge=1, le=10_000),
    seed: int = Query(..., ge=1, le=10_000),
    session: AsyncSession = Depends(get_session),
):
    repo = SqlAlchemyWaypointRepository(session)
    service = WaypointService(repo)

    dom_waypoints = await service.add_random_required(size=size, seed=seed)
    resp_waypoints = [WaypointResponse(id=dom_waypoint.id,
                                       lat=dom_waypoint.position.lat,
                                       lng=dom_waypoint.position.lon,
                                       role=dom_waypoint.role,
                                       color=COLOR_BY_ROLE.get(dom_waypoint.role),
                                       wind_speed=dom_waypoint.wind_speed,
                                       wind_direction=dom_waypoint.wind_direction,
                                       name="") for dom_waypoint in dom_waypoints ]
    return resp_waypoints


@router.post("/delete_point")
async def delete_point(
    body: DeleteWaypointRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:

    repo = SqlAlchemyWaypointRepository(session)
    service = WaypointService(repo)

    await service.delete(body.waypoint_id)

    return {"ok": True}
