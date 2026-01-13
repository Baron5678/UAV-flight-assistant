import asyncio

import pytest

from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.models import (
    GeoPoint,
    OptimizerDiagnostic,
    OptimizerFinal,
    OptimizerStep,
    UnreachableRequired,
    Waypoint,
)
from uav_assistant.transport.routers.ws.builders import (
    build_diagnostic_message,
    build_final_message,
    build_generation_message,
    build_trace_fn,
)


def wp(wid: int, lat: float, lon: float, role: WaypointRole) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)


def test_build_generation_message_includes_coords_and_message() -> None:
    id2wp = {
        1: wp(1, 10.0, 20.0, WaypointRole.START),
        2: wp(2, 11.0, 21.0, WaypointRole.REQUIRED),
    }
    step = OptimizerStep(generation=3, cost=12.3456, waypoint_ids=[1, 2])
    msg = build_generation_message(algo="GA", step=step, id_to_wp=id2wp)

    assert msg.type == "generation"
    assert msg.algo == "GA"
    assert msg.generation == 3
    assert msg.cost == pytest.approx(12.3456)
    assert msg.waypoint_ids == [1, 2]
    assert msg.waypoint_coords == [(10.0, 20.0), (11.0, 21.0)]
    assert "Gen:3" in msg.message


def test_build_final_message_includes_coords_and_total_distance() -> None:
    id2wp = {
        1: wp(1, 10.0, 20.0, WaypointRole.START),
        2: wp(2, 11.0, 21.0, WaypointRole.END),
    }
    final = OptimizerFinal(
        algo="ES",
        generations=30,
        cost=9.9,
        waypoint_ids=[1, 2],
        total_distance_m=123.0,
    )

    msg = build_final_message(final=final, id_to_wp=id2wp)

    assert msg.type == "final"
    assert msg.algo == "ES"
    assert msg.generation == 30
    assert msg.cost == pytest.approx(9.9)
    assert msg.total_distance_m == pytest.approx(123.0)
    assert msg.waypoint_ids == [1, 2]
    assert msg.waypoint_coords == [(10.0, 20.0), (11.0, 21.0)]
    assert "Final" in msg.message


def test_build_diagnostic_message_maps_problems() -> None:
    diag = OptimizerDiagnostic(
        type="diagnostic",
        feasible=False,
        max_leg_m=100.0,
        problems=[
            UnreachableRequired(
                required_id=10,
                nearest_station_id=5,
                dist_required_to_station_m=123.0,
                max_leg_m=100.0,
                nearest_required_id=None,
                dist_required_to_required_m=None,
            )
        ],
    )

    msg = build_diagnostic_message(diag)
    assert msg.type == "diagnostic"
    assert msg.feasible is False
    assert msg.max_leg_m == pytest.approx(100.0)
    assert len(msg.problems) == 1
    assert msg.problems[0].required_id == 10
    assert msg.problems[0].nearest_station_id == 5


@pytest.mark.asyncio
async def test_build_trace_fn_puts_items_into_queue() -> None:
    loop = asyncio.get_running_loop()
    q: asyncio.Queue = asyncio.Queue()

    trace = build_trace_fn(loop=loop, queue=q)

    step = OptimizerStep(generation=1, cost=1.0, waypoint_ids=[1, 2])
    trace(step)

    got = await asyncio.wait_for(q.get(), timeout=1.0)
    assert got == step
