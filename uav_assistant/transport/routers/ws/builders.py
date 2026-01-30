from __future__ import annotations
import asyncio
import math
from typing import Dict, Sequence, Tuple

from cma.options_parameters import is_feasible
from uav_assistant.cross.sockets import TraceQueue, TraceFn
from uav_assistant.domain.models import Waypoint, OptimizerStep, OptimizerFinal, OptimizerError
from uav_assistant.transport.routers.ws.models import GenerationMessage, FinalMessage, ErrorGenerationMessage

def _coords(waypoint_ids: Sequence[int], id_to_wp: Dict[int, Waypoint]) -> list[Tuple[float, float]]:
    return [(id_to_wp[i].position.lat, id_to_wp[i].position.lon) for i in waypoint_ids]

def build_generation_message(
    algo: str,
    step: OptimizerStep,
    id_to_wp: Dict[int, Waypoint],
) -> GenerationMessage:
    ids = list(step.waypoint_ids)
    str_msg = f"Gen:{step.generation} --- Path's value:{step.cost:.2f}"
    feasible = math.isfinite(step.cost)
    if not feasible:
        step.cost = -1
        str_msg = "Path is impossible to construct."

    return GenerationMessage(
        algo=algo,
        generation=int(step.generation),
        cost=float(step.cost),
        waypoint_ids=ids,
        waypoint_coords=_coords(ids, id_to_wp),
        is_feasible=feasible,
        message=str_msg,
    )

def build_error_message(diag: OptimizerError) -> ErrorGenerationMessage:
    return ErrorGenerationMessage(type=diag.type, feasible=diag.feasible, message=diag.problem)

def build_final_message(
    final: OptimizerFinal,
    id_to_wp: Dict[int, Waypoint],
) -> FinalMessage:
    ids = list(final.waypoint_ids)
    str_msg = f"Final --- Path's value:{final.cost:.2f}"
    feasible = math.isfinite(final.cost)
    if not feasible:
        final.cost = -1
        str_msg = "Path is impossible to construct."
    return FinalMessage(
        algo=str(final.algo),
        generation=int(final.generations),
        cost=float(final.cost),
        total_distance_m=float(final.total_distance_m),
        waypoint_ids=ids,
        waypoint_coords=_coords(ids, id_to_wp),
        is_feasible=feasible,
        message=str_msg,
    )

def build_trace_fn(
    *,
    loop: asyncio.AbstractEventLoop,
    queue: TraceQueue,
) -> TraceFn:
    def trace(step: OptimizerStep) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, step)
    return trace