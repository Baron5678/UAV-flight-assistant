from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, delete
from drone_path.app.db.postgre import get_session
from drone_path.app.db.models import Waypoint
from drone_path.app.routers.models import WaypointRequest, COLOR_BY_ROLE, WaypointResponse

router = APIRouter()

@router.post("/add_waypoint")
async def add_waypoint(waypoint: WaypointRequest, session:AsyncSession = Depends(get_session)):
    print(waypoint.role)
    print("PY ENUM LABELS:", Waypoint.__table__.c.role.type.enums)
    stm = (
            insert(Waypoint)
            .values(id=waypoint.id,
                    latitude=waypoint.lat,
                    longitude=waypoint.lon,
                    role=waypoint.role,
                    name=waypoint.name)
            .returning(Waypoint.id)
            )
    res = await session.execute(stm)
    role = str(waypoint.role).lower()
    wp_id = res.scalar_one()
    return WaypointResponse(
        id=wp_id,
        lat=float(waypoint.lat),
        lng=float(waypoint.lon),
        role=role,
        color=COLOR_BY_ROLE.get(role, "blue"),
        name=waypoint.name,
    )

@router.post("/reset_waypoint")
async def reset_waypoints(session:AsyncSession = Depends(get_session)):
     await session.execute(delete(Waypoint))
     return {"message": "Waypoint reset"}


