from typing import Union, Any, Coroutine

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.app.services.path_summary import PathSummaryService
from uav_assistant.domain.metrics import build_id2wp
from uav_assistant.domain.models import Drone, OptimizerError
from uav_assistant.domain.optimizers import build_optimizer
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.mission_outcome import SqlAlchemyPathSummaryRepository
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.transport.routers.http.models import PathRequest, PathResponse, DroneRequest, OptimizerErrorResponse

router = APIRouter()
@router.post("/path", response_model=Union[PathResponse, OptimizerErrorResponse],
             responses={422: {"model": OptimizerErrorResponse}})
async def preview_path(
    body: PathRequest,
    session: AsyncSession = Depends(get_session),
) -> OptimizerErrorResponse | PathResponse:
    mission_repo = SqlAlchemyMissionRepository(session)
    waypoint_repo = SqlAlchemyWaypointRepository(session)

    mission = await mission_repo.get(body.mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail=f"Mission {body.mission_id} not found")

    mission.generations = body.generations
    mission.population_size = body.population_size
    mission.seed = body.seed
    mission.k_tournament = body.k_tournament
    mission.mutation_probability = body.mutation_probability
    mission.sigma0 = body.sigma0
    mission.keep_elitism = body.keep_elitism
    print(f"MUST BE WEATHER{mission.objective}")
    await mission_repo.add(mission)

    candidates = await waypoint_repo.get_for_mission(body.mission_id)
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidate waypoints for mission")

    dr = body.drone or DroneRequest()

    dom_drone = Drone(
        id=0,
        name="preview",
        battery_capacity_wh=dr.battery_capacity_wh,
        speed_mps=dr.speed_mps,
        payload_kg=getattr(dr, "payload_kg", 0.0),
        per_meter_wh=dr.wh_per_km,
    )

    try:
        optimizer = build_optimizer(body.algo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    path, steps = await optimizer.optimize_http(
        mission=mission,
        drones=[dom_drone],
        candidates=candidates,
    )

    if isinstance(path, OptimizerError):
        diag = OptimizerErrorResponse(type=path.type, feasible=path.feasible, message=path.problem)
        return diag


    summary_repo = SqlAlchemyPathSummaryRepository(session)
    summary_svc = PathSummaryService(summary_repo)

    await summary_svc.clear_mission(mission.id)

    id2wp = build_id2wp(candidates)
    for step in steps:
        await summary_svc.append_step(
            mission_id=mission.id,
            step=step,
            id_to_wp=id2wp,
        )

    id2wp = build_id2wp(candidates)
    try:
        coords = [(id2wp[i].position.lat, id2wp[i].position.lon) for i in path.waypoint_ids]
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Path contains unknown waypoint id: {e}") from e

    for cur_id in path.waypoint_ids:
        print(f"Router {cur_id}")

    return PathResponse(
        waypoint_ids=path.waypoint_ids,
        waypoint_coords=coords,
        total_distance_m=path.total_distance_m,
        best_cost=path.cost,
        generations=body.generations,
        population_size=body.population_size,
        algo=body.algo,
    )
