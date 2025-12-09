# uav_assistant/transport/routers/waypoints.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.app.services.waypoint import WaypointService, AddWaypointCommand
from uav_assistant.cross.enums import WaypointRole
from uav_assistant.transport.routers.models import WaypointRequest, WaypointResponse, DeleteWaypointRequest

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
        loss_chance=body.loss_chance,
    )

    wp = await service.add_waypoint(cmd)
    role_str = wp.role

    return WaypointResponse(
        id=wp.id,
        lat=wp.position.lat,
        lng=wp.position.lon,
        role=role_str,
        color=COLOR_BY_ROLE.get(role_str, "blue"),
        name=wp.name,
    )

@router.post("/delete_point")
async def delete_point(
    body: DeleteWaypointRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:

    repo = SqlAlchemyWaypointRepository(session)
    service = WaypointService(repo)

    await service.delete(body.waypoint_id)

    return {"ok": True}
