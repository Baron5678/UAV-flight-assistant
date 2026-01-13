import pytest

from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.models import GeoPoint, Waypoint
from uav_assistant.infra.preprocess.post_run import post_run_energy


def wp(wid: int, lat: float, lon: float, role: WaypointRole) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)


def test_post_run_energy_empty_route_is_infeasible() -> None:
    report = post_run_energy(
        [],
        {},
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.2,
    )
    assert report.feasible is False
    assert report.total_dist_m == pytest.approx(0.0)
    assert report.station_visits == 0


def test_post_run_energy_counts_station_visits_and_resets_soc() -> None:
    start = wp(1, 0.0, 0.0, WaypointRole.START)
    station = wp(2, 0.0, 10.0 / 111_194.9266, WaypointRole.STATION)
    end = wp(3, 0.0, 20.0 / 111_194.9266, WaypointRole.END)
    id2wp = {1: start, 2: station, 3: end}

    report = post_run_energy(
        [1, 2, 3],
        id2wp,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.0,
    )

    assert report.feasible is True
    assert report.station_visits == 1


def test_post_run_energy_detects_insufficient_energy_relative_to_reserve() -> None:
    start = wp(1, 0.0, 0.0, WaypointRole.START)
    end = wp(2, 0.0, 9.0 / 111_194.9266, WaypointRole.END)
    id2wp = {1: start, 2: end}

    report = post_run_energy(
        [1, 2],
        id2wp,
        battery_wh=10.0,
        per_meter_wh=1.0,
        reserve_ratio=0.2,
    )

    assert report.feasible is False
    assert report.failure is not None


def test_post_run_energy_total_distance_should_not_be_double_counted() -> None:
    start = wp(1, 0.0, 0.0, WaypointRole.START)
    end = wp(2, 0.0, 10.0 / 111_194.9266, WaypointRole.END)
    id2wp = {1: start, 2: end}

    report = post_run_energy(
        [1, 2],
        id2wp,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.0,
    )

    assert report.total_dist_m == pytest.approx(10.0, rel=1e-2)
