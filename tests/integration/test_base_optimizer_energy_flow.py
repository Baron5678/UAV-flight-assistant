import pytest

from uav_assistant.app.base_optimizer import BasePathOptimizer
from uav_assistant.cross.enums import ObjectiveFunction, WaypointRole, Status
from uav_assistant.domain.models import Drone, GeoPoint, Mission, OptimizerDiagnostic, OptimizerRouteValidation, OptimizerStep, Path, Waypoint


def wp(wid: int, lat: float, lon: float, role: WaypointRole) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)


@pytest.mark.asyncio
async def test_optimize_http_returns_diagnostic_when_prerun_fails() -> None:
    def runner(points, *, start_id, end_id, graph, settings, trace=None):
        raise AssertionError("runner must not be called when pre_run_energy fails")

    optimizer = BasePathOptimizer(algo_name="GA", runner=runner)

    mission = Mission(
        id=1,
        name="m",
        start_waypoint_id=1,
        end_waypoint_id=3,
        path_size=3,
        algo="GA",
        objective=ObjectiveFunction.ENERGY,
        generations=5,
        population_size=10,
        best_cost=0.0,
        status=Status("PENDING"),
    )

    start = wp(1, 0.0, 0.0, WaypointRole.START)
    required = wp(2, 0.0, 200.0 / 111_194.9266, WaypointRole.REQUIRED)
    end = wp(3, 0.0, 400.0 / 111_194.9266, WaypointRole.END)

    drone = Drone(id=0, name="d", battery_capacity_wh=100.0, speed_mps=0.0, payload_kg=0.0, per_meter_wh=1000.0)

    result, steps = await optimizer.optimize_http(mission=mission, drones=[drone], candidates=[start, required, end])

    assert steps == []
    assert isinstance(result, OptimizerDiagnostic)
    assert result.type == "diagnostic"
    assert result.feasible is False
    assert len(result.problems) == 1


@pytest.mark.asyncio
async def test_optimize_http_returns_route_validation_when_postrun_fails() -> None:
    def runner(points, *, start_id, end_id, graph, settings, trace=None):
        return [start_id, 2, 4, end_id], 999.0

    optimizer = BasePathOptimizer(algo_name="GA", runner=runner)

    mission = Mission(
        id=1,
        name="m",
        start_waypoint_id=1,
        end_waypoint_id=5,
        path_size=5,
        algo="GA",
        objective=ObjectiveFunction.ENERGY,
        generations=5,
        population_size=10,
        best_cost=0.0,
        status="PENDING",
    )


    start = wp(1, 0.0, 0.0, WaypointRole.START)
    a = wp(2, 0.0, 60.0 / 111_194.9266, WaypointRole.REQUIRED)
    station = wp(3, 0.0, 90.0 / 111_194.9266, WaypointRole.STATION)
    b = wp(4, 0.0, 120.0 / 111_194.9266, WaypointRole.REQUIRED)
    end = wp(5, 0.0, 180.0 / 111_194.9266, WaypointRole.END)

    drone = Drone(id=0, name="d", battery_capacity_wh=100.0, speed_mps=0.0, payload_kg=0.0, per_meter_wh=1000.0)

    result, steps = await optimizer.optimize_http(mission=mission, drones=[drone], candidates=[start, a, station, b, end])

    assert steps == []
    assert isinstance(result, OptimizerRouteValidation)
    assert result.type == "route_validation"
    assert result.objective == "ENERGY"
    assert result.feasible is False
    assert result.report.failure is not None


@pytest.mark.asyncio
async def test_optimize_http_distance_happy_path_returns_path_and_steps() -> None:
    def runner(points, *, start_id, end_id, graph, settings, trace=None):
        if trace is not None:
            trace(OptimizerStep(generation=1, cost=10.0, waypoint_ids=[start_id, end_id]))
            trace(OptimizerStep(generation=2, cost=9.0, waypoint_ids=[start_id, end_id]))
        return [start_id, end_id], 9.0

    optimizer = BasePathOptimizer(algo_name="GA", runner=runner)

    mission = Mission(
        id=1,
        name="m",
        start_waypoint_id=1,
        end_waypoint_id=2,
        path_size=2,
        algo="GA",
        objective=ObjectiveFunction.DISTANCE,
        generations=2,
        population_size=10,
        best_cost=0.0,
        status="PENDING",
    )

    start = wp(1, 0.0, 0.0, WaypointRole.START)
    end = wp(2, 0.0, 10.0 / 111_194.9266, WaypointRole.END)

    drone = Drone(id=0, name="d", battery_capacity_wh=100.0, speed_mps=0.0, payload_kg=0.0, per_meter_wh=1000.0)

    result, steps = await optimizer.optimize_http(mission=mission, drones=[drone], candidates=[start, end])

    assert isinstance(result, Path)
    assert result.waypoint_ids == [1, 2]
    assert result.cost == pytest.approx(9.0)
    assert result.total_distance_m > 0

    assert [s.generation for s in steps] == [1, 2]
