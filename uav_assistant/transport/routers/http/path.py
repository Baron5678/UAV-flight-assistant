from typing import Union, Any, Coroutine

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.app.services.path_summary import PathSummaryService
from uav_assistant.domain.metrics import build_id2wp
from uav_assistant.domain.models import Drone, OptimizerDiagnostic, OptimizerRouteValidation
from uav_assistant.domain.optimizers import build_optimizer
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.path_summary import SqlAlchemyPathSummaryRepository
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.transport.routers.http.models import PathRequest, PathResponse, DroneRequest, PreRunReportResponse, \
    UnreachableRequiredResponse, PostRunRouteValidationResponse, RouteEnergyFailureResponse


def to_postrun_response(
    validation: OptimizerRouteValidation,
    *,
    per_meter_wh: float,
) -> PostRunRouteValidationResponse:
    f = validation.report.failure

    soc = float(f.soc_wh)
    reserve = float(f.reserve_wh)
    needed = float(f.needed_wh)
    dist = float(f.dist_m)
    available = max(0.0, soc - reserve)
    deficit_wh = max(0.0, needed - available)
    deficit_m = (deficit_wh / per_meter_wh) if per_meter_wh and per_meter_wh > 0 else float("inf")

    return PostRunRouteValidationResponse(
        type="route_validation",
        failure=RouteEnergyFailureResponse(
            from_id=int(f.from_id),
            to_id=int(f.to_id),
            dist_m=dist,
            soc_wh=soc,
            reserve_wh=reserve,
            needed_wh=needed,
            deficit_wh=deficit_wh,
            deficit_m=deficit_m,
        )
    )
router = APIRouter()
@router.post("/path", response_model=Union[PathResponse, PreRunReportResponse, PostRunRouteValidationResponse],
             responses={422: {"model": Union[PreRunReportResponse, PostRunRouteValidationResponse]}})
async def preview_path(
    body: PathRequest,
    session: AsyncSession = Depends(get_session),
) -> PostRunRouteValidationResponse | PreRunReportResponse | PathResponse:
    mission_repo = SqlAlchemyMissionRepository(session)
    waypoint_repo = SqlAlchemyWaypointRepository(session)

    mission = await mission_repo.get(body.mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail=f"Mission {body.mission_id} not found")

    mission.generations = body.generations
    mission.population_size = body.population_size
    await mission_repo.add(mission)

    candidates = await waypoint_repo.get_for_mission(body.mission_id)
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidate waypoints for mission")

    dr = body.drone or DroneRequest()

    dom_drone = Drone(
        id=0,
        name="preview",
        battery_capacity_wh=dr.battery_capacity_wh,
        speed_mps=0.0,
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

    if isinstance(path, OptimizerDiagnostic):  # preferred
        diag = PreRunReportResponse(
            feasible=path.feasible,
            max_leg_m=path.max_leg_m,
            problems=[
                UnreachableRequiredResponse(
                    required_id=p.required_id,
                    nearest_station_id=p.nearest_station_id,
                    dist_required_to_station_m=p.dist_required_to_station_m,
                    max_leg_m=p.max_leg_m,
                    nearest_required_id=p.nearest_required_id,
                    dist_required_to_required_m=p.dist_required_to_required_m,
                )
                for p in path.problems
            ],
        )
        return diag

    if isinstance(path, OptimizerRouteValidation):
        failure = to_postrun_response(path, per_meter_wh=body.drone.wh_per_km / 1000)
        print(failure.feasible)
        return failure

    summary_repo = SqlAlchemyPathSummaryRepository(session)
    summary_svc = PathSummaryService(summary_repo)

    await summary_svc.clear_mission(mission.id)

    id2wp = build_id2wp(candidates)  # used for both coords and distance calculations

    # Persist every generation step (cost is already in step, distance computed in service)
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
