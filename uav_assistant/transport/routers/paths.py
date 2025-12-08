# uav_assistant/transport/routers/paths.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.domain.models import Drone
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.infra.db.repos.path import SqlAlchemyPathRepository
from uav_assistant.infra.ga.path_optimizer import GAPathOptimizer, ESPathOptimizer
from uav_assistant.app.services.path import PathService
from uav_assistant.transport.routers.models import PathRequest, PathResponse, DroneRequest

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
    dr = body.drone or DroneRequest()

    dom_drone = Drone(
        id=0,
        name="preview",
        battery_capacity_wh=dr.battery_capacity_wh,
        speed_mps=0.0,
        payload_kg=dr.payload_kg if hasattr(dr, "payload_kg") else 0.0,
        per_meter_wh=dr.wh_per_km,  # meaning: Wh/km in your model
    )
    print(dom_drone.battery_capacity_wh, dr.wh_per_km)

    dom_path = await optimizer.optimize(
        mission=mission,
        drones=[ dom_drone ],
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
