# uav_assistant/transport/routers/ws_paths.py
from __future__ import annotations

import asyncio
from typing import Any, Dict, Sequence, Callable, Tuple

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.transport.routers.models import PathRequest
from uav_assistant.domain.models import Mission, Waypoint
from uav_assistant.domain.metrics import distance_m
from uav_assistant.infra.ga.genetic_algorithm import run_ga_s
from uav_assistant.infra.es.es import run_es  # your ES impl

router = APIRouter()

TraceEvent = Dict[str, Any]
TraceFn = Callable[[TraceEvent], None]
TraceQueue = "asyncio.Queue[TraceEvent]"

async def receive_path_request(websocket: WebSocket) -> PathRequest:
    """
    First WS message must be exactly the same JSON as POST /path body.
    """
    data = await websocket.receive_json()
    return PathRequest(**data)

async def load_mission_and_waypoints(
    session: AsyncSession, path_request: PathRequest
) -> Tuple[Mission, Sequence[Waypoint]]:
    mission_repo = SqlAlchemyMissionRepository(session)
    wp_repo = SqlAlchemyWaypointRepository(session)

    mission = await mission_repo.get(path_request.mission_id)
    waypoints = await wp_repo.get_for_mission(mission.id)

    return mission, waypoints

def create_trace_fn(
    loop: asyncio.AbstractEventLoop,
    queue: TraceQueue,
    id_to_wp: Dict[int, Waypoint],
    algo: str,
) -> TraceFn:
    """
    Returns a function `trace(event)` that GA/ES will call.
    It enriches events with coords & message and puts them to the queue.
    """

    def trace(event: TraceEvent) -> None:
        gen = int(event["generation"])
        best_cost = float(event["best_cost"])
        waypoint_ids = list(event["waypoint_ids"])

        coords = [
            (id_to_wp[i].position.lat, id_to_wp[i].position.lon)
            for i in waypoint_ids
        ]

        enriched: TraceEvent = {
            "type": "generation",
            "algo": algo,
            "generation": gen,
            "best_cost": best_cost,
            "waypoint_ids": waypoint_ids,
            "waypoint_coords": coords,
            "message": f"Gen:{gen} --- Path's value:{best_cost:.2f}",
        }

        loop.call_soon_threadsafe(queue.put_nowait, enriched)

    return trace

async def send_trace_events(
    websocket: WebSocket, queue: TraceQueue
) -> None:
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
            if event.get("type") == "final":
                break
    except WebSocketDisconnect:
        # client closed – just stop
        return

def run_optimizer_blocking(
    *,
    algo: str,
    mission: Mission,
    waypoints: Sequence[Waypoint],
    path_request: PathRequest,
    id_to_wp: Dict[int, Waypoint],
    trace: TraceFn,
    loop: asyncio.AbstractEventLoop,
    queue: TraceQueue,
) -> None:

    if algo == "GA":
        best_route_ids, best_cost = run_ga_s(
            points=waypoints,
            start_id=mission.start_waypoint_id,
            end_id=mission.end_waypoint_id,
            generations=path_request.generations,
            pop_size=path_request.population_size,
            battery_wh=path_request.drone.battery_capacity_wh,
            per_meter_wh=path_request.drone.wh_per_km / 1000.0,
            trace=trace,
        )
    else:
        best_route_ids, best_cost = run_es(
            points=waypoints,
            start_id=mission.start_waypoint_id,
            end_id=mission.end_waypoint_id,
            generations=path_request.generations,
            pop_size=path_request.population_size,
            trace=trace,
        )

    total_dist = 0.0
    for a, b in zip(best_route_ids, best_route_ids[1:]):
        wp_a = id_to_wp[a]
        wp_b = id_to_wp[b]
        total_dist += distance_m(wp_a.position, wp_b.position)

    coords = [
        (id_to_wp[i].position.lat, id_to_wp[i].position.lon)
        for i in best_route_ids
    ]

    final_event: TraceEvent = {
        "type": "final",
        "algo": algo,
        "generation": path_request.generations,
        "best_cost": best_cost,
        "total_distance_m": total_dist,
        "waypoint_ids": best_route_ids,
        "waypoint_coords": coords,
        "message": f"Final --- Path's value:{best_cost:.2f}",
    }

    loop.call_soon_threadsafe(queue.put_nowait, final_event)


@router.websocket("/ws/path_progress")
async def path_progress_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
) -> None:
    await websocket.accept()
    loop = asyncio.get_running_loop()
    queue: TraceQueue = asyncio.Queue()

    try:
        print("START WS")
        # 1. Read and validate initial request (same as POST /path)
        path_request = await receive_path_request(websocket)
        print(path_request.drone.battery_capacity_wh)

        # 2. Load mission + waypoints
        mission, waypoints = await load_mission_and_waypoints(session, path_request)
        id_to_wp = {w.id: w for w in waypoints}
        algo = path_request.algo.upper()

        # 3. Create tracer that will forward GA/ES events into queue
        trace = create_trace_fn(loop, queue, id_to_wp, algo)

        # 4. Kick off both sender and optimizer in parallel
        sender_task = asyncio.create_task(send_trace_events(websocket, queue))
        optimizer_task = asyncio.create_task(
            asyncio.to_thread(
                run_optimizer_blocking,
                algo=algo,
                mission=mission,
                waypoints=waypoints,
                path_request=path_request,
                id_to_wp=id_to_wp,
                trace=trace,
                loop=loop,
                queue=queue,
            )
        )

        await asyncio.gather(sender_task, optimizer_task)

    except WebSocketDisconnect:
        # client aborted – nothing special
        return



