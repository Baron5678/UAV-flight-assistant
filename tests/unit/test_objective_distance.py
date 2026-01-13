import numpy as np
import pytest

from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.models import AlgoSettings, GeoPoint, Waypoint
from uav_assistant.infra.objective_functions import distance as dist_obj

def wp(wid: int, lat: float, lon: float, role: WaypointRole) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)

points = [wp(1, 0.0, 0.0, WaypointRole.START), wp(2, 0.0, 0.0, WaypointRole.REQUIRED), wp(3, 0.0, 0.0, WaypointRole.END)]
points_tsg = [
    wp(1, 0.0, 0.0, WaypointRole.START),
    wp(2, 0.0, 0.1, WaypointRole.REQUIRED),
    wp(3, 0.0, 0.2, WaypointRole.STATION),
    wp(4, 0.0, 0.3, WaypointRole.REQUIRED),
    wp(5, 0.0, 0.4, WaypointRole.END),
]

def test_select_genes_excludes_start_end_and_only_required() -> None:
    genes = dist_obj.select_genes(points_tsg, start_id=1, end_id=5)
    assert genes == [2, 4]


def test_build_decoder_sorts_by_key_then_id() -> None:
    decode = dist_obj.build_decoder(points=points_tsg, start_id=1, end_id=5, middles=[2, 3, 4])
    sol = np.asarray([0.2, 0.1, 0.1], dtype=float)
    route = decode(sol)
    assert route == [1, 3, 4, 2, 5]


def test_calculate_route_distance_returns_inf_on_missing_id() -> None:
    points_tsr = [wp(1, 0.0, 0.0, WaypointRole.START), wp(2, 0.0, 0.0, WaypointRole.END)]
    id2idx = dist_obj.build_id_index(points_tsr)
    g = np.zeros((2, 2), dtype=float)

    assert np.isinf(dist_obj.calculate_route_distance([1, 999], g, id2idx))


def test_calculate_route_distance_sums_path_weights() -> None:
    points_tcr = [wp(1, 0.0, 0.0, WaypointRole.START), wp(2, 0.0, 0.0, WaypointRole.REQUIRED), wp(3, 0.0, 0.0, WaypointRole.END)]
    id2idx = dist_obj.build_id_index(points_tcr)

    g = np.array(
        [
            [0.0, 2.0, 10.0],
            [2.0, 0.0, 3.0],
            [10.0, 3.0, 0.0],
        ],
        dtype=float,
    )
    assert dist_obj.calculate_route_distance([1, 2, 3], g, id2idx) == pytest.approx(5.0)


def test_build_distance_es_returns_bad_cost_for_infinite_distance() -> None:
    points_tbd = [wp(1, 0.0, 0.0, WaypointRole.START), wp(2, 0.0, 0.0, WaypointRole.REQUIRED), wp(3, 0.0, 0.0, WaypointRole.END)]
    decode = lambda x: [1, 2, 3]
    settings = AlgoSettings(
        generations=1,
        population_size=1,
        battery_wh=1.0,
        per_meter_wh=1.0,
        reserve_ratio=0.0,
        station_threshold=0.0,
        station_penalty_m=0.0,
        objective="DISTANCE",
    )

    g = np.array(
        [
            [0.0, np.inf, 1.0],
            [np.inf, 0.0, 1.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=float,
    )

    obj = dist_obj.build_distance_es(decode=decode, graph=g, points=points_tbd, settings=settings, bad_cost=123.0)
    assert obj(np.array([0.0])) == pytest.approx(123.0)



def test_build_distance_ga_returns_bad_fitness_for_infinite_distance() -> None:
    points_tdsgb = [wp(1, 0.0, 0.0, WaypointRole.START), wp(2, 0.0, 0.0, WaypointRole.REQUIRED), wp(3, 0.0, 0.0, WaypointRole.END)]
    decode = lambda x: [1, 2, 3]
    settings = AlgoSettings(
        generations=1,
        population_size=1,
        battery_wh=1.0,
        per_meter_wh=1.0,
        reserve_ratio=0.0,
        station_threshold=0.0,
        station_penalty_m=0.0,
        objective="DISTANCE",
    )

    g = np.array(
        [
            [0.0, np.inf, 1.0],
            [np.inf, 0.0, 1.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=float,
    )

    fitness = dist_obj.build_distance_ga(decode=decode, graph=g, points=points_tdsgb, settings=settings, bad_fitness=-9.0)
    assert fitness(None, np.array([0.0]), 0) == pytest.approx(-9.0)
