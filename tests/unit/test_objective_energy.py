import pytest

from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.models import GeoPoint, Waypoint
from uav_assistant.infra.objective_functions import energy as energy_obj


def wp(wid: int, lat: float, lon: float, role: WaypointRole) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)


def test_select_genes_excludes_start_end_and_only_required() -> None:
    points = [
        wp(1, 0.0, 0.0, WaypointRole.START),
        wp(2, 0.0, 0.1, WaypointRole.REQUIRED),
        wp(3, 0.0, 0.2, WaypointRole.STATION),
        wp(4, 0.0, 0.3, WaypointRole.REQUIRED),
        wp(5, 0.0, 0.4, WaypointRole.END),
    ]
    genes = energy_obj.select_genes(points, start_id=1, end_id=5)
    assert genes == [2, 4]


def test_insert_stations_if_needed_inserts_station_when_soc_would_drop_below_reserve() -> None:
    start = wp(1, 0.0, 0.0, WaypointRole.START)

    a = wp(2, 0.0, 60.0 / 111_194.9266, WaypointRole.REQUIRED)

    s = wp(3, 0.0, (60.0 + 20.0) / 111_194.9266, WaypointRole.STATION)

    b = wp(4, 0.0, (60.0 + 60.0) / 111_194.9266, WaypointRole.REQUIRED)

    end = wp(5, 0.0, (60.0 + 60.0 + 40.0) / 111_194.9266, WaypointRole.END)

    id2wp = {w.id: w for w in [start, a, s, b, end]}

    route = [1, 2, 4, 5]

    repaired, feasible, visits = energy_obj.insert_stations_if_needed(
        route,
        id2wp,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.1,
    )

    assert feasible is True
    assert visits == 1
    assert repaired == [1, 2, 3, 4, 5]


def test_energy_cost_adds_station_visit_penalty_of_20() -> None:
    start = wp(1, 0.0, 0.0, WaypointRole.START)
    a = wp(2, 0.0, 60.0 / 111_194.9266, WaypointRole.REQUIRED)
    s = wp(3, 0.0, (60.0 + 20.0) / 111_194.9266, WaypointRole.STATION)
    b = wp(4, 0.0, (60.0 + 60.0) / 111_194.9266, WaypointRole.REQUIRED)
    end = wp(5, 0.0, (60.0 + 60.0 + 40.0) / 111_194.9266, WaypointRole.END)

    id2wp = {w.id: w for w in [start, a, s, b, end]}

    cost = energy_obj.energy_cost(
        route_ids=[1, 2, 4, 5],
        id2wp=id2wp,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.1,
        station_penalty_m=9999.0,
    )

    repaired = [1, 2, 3, 4, 5]
    total_dist, feasible, visits = energy_obj.simulate_energy_route(
        repaired,
        id2wp,
        battery_wh=100.0,
        per_meter_wh=1.0,
        reserve_ratio=0.1,
    )
    assert feasible is True
    assert visits == 1
    assert cost == pytest.approx(total_dist + 20.0)



