from __future__ import annotations
import asyncio
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uav_assistant.domain.optimizers import build_optimizer
from uav_assistant.infra.db.postgre import get_session
from uav_assistant.infra.db.repos.mission import SqlAlchemyMissionRepository
from uav_assistant.infra.db.repos.waypoint import SqlAlchemyWaypointRepository
from uav_assistant.domain.models import Waypoint, OptimizerStep, Drone, OptimizerFinal, OptimizerError
from uav_assistant.cross.sockets import TraceQueue
from uav_assistant.transport.routers.ws.models import PathMessage
from uav_assistant.transport.routers.ws.builders import (build_generation_message, build_final_message, build_trace_fn,
                                                         build_error_message)

router = APIRouter()

async def receive_path_message(websocket: WebSocket) -> PathMessage:
    data = await websocket.receive_json()
    return PathMessage(**data)

async def send_trace_events(
    websocket: WebSocket,
    queue: TraceQueue,
    *,
    algo: str,
    id_to_wp: Dict[int, Waypoint],
) -> None:
    try:
        while True:
            event = await queue.get()
            if isinstance(event, OptimizerStep):
                msg = build_generation_message(algo=algo, step=event, id_to_wp=id_to_wp)
                await websocket.send_json(msg.model_dump())
                continue

            if isinstance(event, OptimizerError):
                msg = build_error_message(event)
                await websocket.send_json(msg.model_dump())
                break

            if isinstance(event, OptimizerFinal):
                msg = build_final_message(final=event, id_to_wp=id_to_wp)
                await websocket.send_json(msg.model_dump())
                break

            await websocket.send_json({"type": "error", "detail": f"Unknown event type: {type(event).__name__}"})
            break

    except WebSocketDisconnect:
        return

@router.websocket("/ws/path_progress")
async def path_progress_ws(
    websocket: WebSocket,
    session: AsyncSession = Depends(get_session),
) -> None:
    await websocket.accept()
    loop = asyncio.get_running_loop()
    queue: TraceQueue = asyncio.Queue()

    try:
        msg = await receive_path_message(websocket)
        mission_repo = SqlAlchemyMissionRepository(session)
        wp_repo = SqlAlchemyWaypointRepository(session)
        mission = await mission_repo.get(msg.mission_id)
        waypoints = await wp_repo.get_for_mission(mission.id)
        id_to_wp = {w.id: w for w in waypoints}
        mission.generations = msg.generations
        mission.population_size = msg.population_size
        mission.seed = msg.seed
        mission.k_tournament = msg.k_tournament
        mission.mutation_probability = msg.mutation_probability
        mission.sigma0 = msg.sigma0
        mission.keep_elitism = msg.keep_elitism
        mission.objective = msg.objective_function


        drones = [
           Drone(
               id=0,
               name="ws_drone",
               battery_capacity_wh=msg.drone.battery_capacity_wh,
               speed_mps=0.0,
               payload_kg=getattr(msg.drone, "payload_kg", 0.0),
               per_meter_wh=msg.drone.wh_per_km,
           )
        ]

        optimizer = build_optimizer(msg.algo)
        trace = build_trace_fn(loop=loop, queue=queue)

        sender_task = asyncio.create_task(
            send_trace_events(websocket, queue, algo=msg.algo, id_to_wp=id_to_wp)
        )

        optimizer.optimize_ws(
            mission=mission,
            drones=drones,
            candidates=waypoints,
            loop=loop,
            queue=queue,
            trace=trace,
        )

        await sender_task

    except WebSocketDisconnect:
        return
