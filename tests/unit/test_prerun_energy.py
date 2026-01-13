import pytest

from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.models import AlgoSettings, GeoPoint, Waypoint
from uav_assistant.infra.preprocess.prerun import pre_run_energy


def wp(wid: int, lat: float, lon: float, role: WaypointRole) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)


def test_pre_run_energy_flags_required_unreachable_from_station_or_end() -> None:
    # Battery allows ~100m legs
    settings = AlgoSettings(
        generations=1,
        population_size=1,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.0,
        station_threshold=0.0,
        station_penalty_m=0.0,
        objective="ENERGY",
    )

    start = wp(1, 0.0, 0.0, WaypointRole.START)
    required = wp(2, 0.0, 200.0 / 111_194.9266, WaypointRole.REQUIRED)
    end = wp(3, 0.0, 400.0 / 111_194.9266, WaypointRole.END)

    report = pre_run_energy(points=[start, required, end], end_id=end.id, settings=settings, allow_finish_without_station=True)

    assert report.feasible is False
    assert report.max_leg_m == pytest.approx(100.0)
    assert len(report.problems) == 1
    p = report.problems[0]
    assert p.required_id == required.id
    assert p.dist_required_to_station_m > report.max_leg_m


def test_pre_run_energy_allows_finish_without_station_when_enabled() -> None:
    settings = AlgoSettings(
        generations=1,
        population_size=1,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.0,
        station_threshold=0.0,
        station_penalty_m=0.0,
        objective="ENERGY",
    )

    required = wp(1, 0.0, 50.0 / 111_194.9266, WaypointRole.REQUIRED)
    end = wp(2, 0.0, 0.0, WaypointRole.END)

    report = pre_run_energy(points=[required, end], end_id=end.id, settings=settings, allow_finish_without_station=True)

    assert report.feasible is True
    assert report.problems == []


def test_pre_run_energy_requires_station_when_finish_without_station_disabled() -> None:
    settings = AlgoSettings(
        generations=1,
        population_size=1,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.0,
        station_threshold=0.0,
        station_penalty_m=0.0,
        objective="ENERGY",
    )

    required = wp(1, 0.0, 50.0 / 111_194.9266, WaypointRole.REQUIRED)
    end = wp(2, 0.0, 0.0, WaypointRole.END)

    report = pre_run_energy(points=[required, end], end_id=end.id, settings=settings, allow_finish_without_station=False)

    assert report.feasible is False
    assert len(report.problems) == 1
    assert report.problems[0].nearest_station_id == -1


def test_pre_run_energy_with_zero_per_meter_wh_has_infinite_max_leg() -> None:
    settings = AlgoSettings(
        generations=1,
        population_size=1,
        battery_wh=100.0,
        per_meter_wh=0.0,
        reserve_ratio=0.0,
        station_threshold=0.0,
        station_penalty_m=0.0,
        objective="ENERGY",
    )

    required = wp(1, 0.0, 10.0, WaypointRole.REQUIRED)
    end = wp(2, 0.0, 0.0, WaypointRole.END)

    report = pre_run_energy(points=[required, end], end_id=end.id, settings=settings)

    assert report.max_leg_m == pytest.approx(float("inf"))
    assert report.feasible is True
