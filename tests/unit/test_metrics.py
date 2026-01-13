import math

import numpy as np
import pytest

from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.metrics import (
    RADIUS_EARTH_M,
    build_distance_matrix,
    coords_by_id,
    distance_m,
    estimate_energy_wh,
    mse,
    travel_time_s,
)
from uav_assistant.domain.models import GeoPoint, Waypoint


def wp(wid: int, lat: float, lon: float, role: WaypointRole = WaypointRole.REQUIRED) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)


def test_distance_m_zero_for_same_point() -> None:
    p = GeoPoint(lat=10.0, lon=20.0)
    assert distance_m(p, p) == pytest.approx(0.0, abs=1e-9)


def test_distance_m_known_value_equator_1deg_lon() -> None:
    # With R=6,371,000m, 1 degree of longitude at the equator is ~111,194.93m
    p1 = GeoPoint(lat=0.0, lon=0.0)
    p2 = GeoPoint(lat=0.0, lon=1.0)
    d = distance_m(p1, p2)
    assert d == pytest.approx(111_194.9266, rel=1e-6)


def test_travel_time_s_basic() -> None:
    assert travel_time_s(100.0, 10.0) == pytest.approx(10.0)


def test_travel_time_s_rejects_non_positive_speed() -> None:
    with pytest.raises(ValueError):
        travel_time_s(100.0, 0.0)
    with pytest.raises(ValueError):
        travel_time_s(100.0, -1.0)


def test_estimate_energy_wh_linear() -> None:
    assert estimate_energy_wh(250.0, 0.5) == pytest.approx(125.0)


def test_mse_basic() -> None:
    y = [1.0, 2.0, 3.0]
    y_hat = [1.0, 1.0, 5.0]
    # errors: 0^2, 1^2, (-2)^2 => (0+1+4)/3
    assert mse(y, y_hat) == pytest.approx(5.0 / 3.0)


def test_mse_empty_returns_zero() -> None:
    assert mse([], []) == 0.0


def test_mse_requires_equal_length() -> None:
    with pytest.raises(ValueError):
        mse([1.0], [1.0, 2.0])


def test_coords_by_id() -> None:
    w1 = wp(1, 10.0, 20.0)
    w2 = wp(2, 11.0, 21.0)
    out = coords_by_id([w1, w2])
    assert out[1] == w1.position
    assert out[2] == w2.position


def test_build_distance_matrix_is_symmetric_with_zero_diagonal() -> None:
    pts = [wp(1, 0.0, 0.0), wp(2, 0.0, 1.0), wp(3, 1.0, 0.0)]
    g = build_distance_matrix(pts)

    assert g.shape == (3, 3)
    assert np.allclose(np.diag(g), 0.0)

    # symmetric
    assert np.allclose(g, g.T)

    # sanity: distance(0,0)-(0,1) matches direct distance_m
    d01 = distance_m(pts[0].position, pts[1].position)
    assert g[0, 1] == pytest.approx(d01)
