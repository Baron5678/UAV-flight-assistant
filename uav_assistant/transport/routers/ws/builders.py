from __future__ import annotations

import asyncio
from typing import Dict, Sequence, Tuple

from uav_assistant.cross.sockets import TraceQueue, TraceFn
from uav_assistant.domain.models import Waypoint, OptimizerStep, OptimizerFinal, OptimizerDiagnostic
from uav_assistant.transport.routers.http.models import UnreachableRequiredResponse
from uav_assistant.transport.routers.ws.models import GenerationMessage, FinalMessage, PreRunReportMessage


def _coords(waypoint_ids: Sequence[int], id_to_wp: Dict[int, Waypoint]) -> list[Tuple[float, float]]:
    return [(id_to_wp[i].position.lat, id_to_wp[i].position.lon) for i in waypoint_ids]


def build_generation_message(
    algo: str,
    step: OptimizerStep,
    id_to_wp: Dict[int, Waypoint],
) -> GenerationMessage:
    ids = list(step.waypoint_ids)
    return GenerationMessage(
        algo=algo,
        generation=int(step.generation),
        cost=float(step.cost),
        waypoint_ids=ids,
        waypoint_coords=_coords(ids, id_to_wp),
        message=f"Gen:{step.generation} --- Path's value:{step.cost:.2f}",
    )

def build_diagnostic_message(diag: OptimizerDiagnostic) -> PreRunReportMessage:
    return PreRunReportMessage(
        feasible=diag.feasible,
        max_leg_m=diag.max_leg_m,
        problems=[
            UnreachableRequiredResponse(
                required_id=p.required_id,
                nearest_station_id=p.nearest_station_id,
                dist_required_to_station_m=p.dist_required_to_station_m,
                max_leg_m=p.max_leg_m,
                nearest_required_id=p.nearest_required_id,
                dist_required_to_required_m=p.dist_required_to_required_m,
            )
            for p in diag.problems
        ],
    )

def build_final_message(
    final: OptimizerFinal,
    id_to_wp: Dict[int, Waypoint],
) -> FinalMessage:
    ids = list(final.waypoint_ids)
    return FinalMessage(
        algo=str(final.algo),
        generation=int(final.generations),
        cost=float(final.cost),
        total_distance_m=float(final.total_distance_m),
        waypoint_ids=ids,
        waypoint_coords=_coords(ids, id_to_wp),
        message=f"Final --- Path's value:{final.cost:.2f}",
    )

def build_trace_fn(
    *,
    loop: asyncio.AbstractEventLoop,
    queue: TraceQueue,
) -> TraceFn:
    def trace(step: OptimizerStep) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, step)
    return trace