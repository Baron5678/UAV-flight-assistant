from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from drone_path.app.db.postgre import get_session
from drone_path.app.db.models import Waypoint
from drone_path.app.routers.models import PathRequest, PathResponse
from drone_path.app.ga.genetic_algorithm import run_ga
from drone_path.app.routers.model_operations import get_coords_by_id

router = APIRouter()

@router.post("/path", response_model=PathResponse)
async def render_path(req: PathRequest, session:AsyncSession = Depends(get_session)):
    res = await session.scalars(select(Waypoint))
    waypoints = res.all()
    best_route, best_cost = run_ga(list(waypoints), req.start_id, req.end_id, req.generations, req.population_size)
    coords_list = []
    for wp_id in best_route:
        coords_list.append(get_coords_by_id(list(waypoints), wp_id))
    return PathResponse(waypoint_coords=coords_list, best_cost=best_cost)

