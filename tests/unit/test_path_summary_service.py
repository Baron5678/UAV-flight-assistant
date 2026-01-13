import pytest

from uav_assistant.app.services.path_summary import PathSummaryService
from uav_assistant.domain.models import GeoPoint, OptimizerStep, PathSummary, PathSummaryStats, Waypoint
from uav_assistant.cross.enums import WaypointRole


class InMemoryPathSummaryRepo:
    def __init__(self) -> None:
        self._rows: list[PathSummary] = []

    async def add(self, summary: PathSummary) -> None:
        self._rows.append(summary)

    async def add_many(self, summaries):
        self._rows.extend(summaries)

    async def list_by_mission(self, mission_id: int) -> list[PathSummary]:
        return [r for r in self._rows if r.mission_id == mission_id]

    async def delete_for_mission(self, mission_id: int) -> None:
        self._rows = [r for r in self._rows if r.mission_id != mission_id]


def wp(wid: int, lat: float, lon: float, role: WaypointRole = WaypointRole.REQUIRED) -> Waypoint:
    return Waypoint(id=wid, name=f"wp{wid}", position=GeoPoint(lat=lat, lon=lon), role=role)


@pytest.mark.asyncio
async def test_append_step_computes_and_persists_distance() -> None:
    repo = InMemoryPathSummaryRepo()
    svc = PathSummaryService(repo)

    # ~111m apart
    a = wp(1, 0.0, 0.0)
    b = wp(2, 0.0, 0.001)
    id2wp = {1: a, 2: b}

    step = OptimizerStep(generation=1, cost=123.0, waypoint_ids=[1, 2])

    await svc.append_step(mission_id=99, step=step, id_to_wp=id2wp)

    rows = await repo.list_by_mission(99)
    assert len(rows) == 1
    r = rows[0]

    assert r.mission_id == 99
    assert r.generation == 1
    assert r.cost == pytest.approx(123.0)
    assert r.total_distance_m > 0


@pytest.mark.asyncio
async def test_compute_stats_none_when_no_rows() -> None:
    repo = InMemoryPathSummaryRepo()
    svc = PathSummaryService(repo)

    assert await svc.compute_stats(1) is None


@pytest.mark.asyncio
async def test_compute_stats_aggregates_and_convergence_metrics() -> None:
    repo = InMemoryPathSummaryRepo()
    svc = PathSummaryService(repo)

    repo._rows.extend(
        [
            PathSummary(mission_id=1, generation=1, cost=10.0, total_distance_m=100.0),
            PathSummary(mission_id=1, generation=2, cost=8.0, total_distance_m=90.0),
            PathSummary(mission_id=1, generation=3, cost=8.0, total_distance_m=80.0),
            PathSummary(mission_id=1, generation=4, cost=7.0, total_distance_m=70.0),
        ]
    )

    stats = await svc.compute_stats(1)
    assert isinstance(stats, PathSummaryStats)

    assert stats.first_cost == pytest.approx(10.0)
    assert stats.best_cost == pytest.approx(7.0)

    assert stats.min_cost == pytest.approx(7.0)
    assert stats.max_cost == pytest.approx(10.0)
    assert stats.avg_cost == pytest.approx((10.0 + 8.0 + 8.0 + 7.0) / 4.0)

    assert stats.min_total_distance_m == pytest.approx(70.0)
    assert stats.max_total_distance_m == pytest.approx(100.0)
    assert stats.avg_total_distance_m == pytest.approx((100.0 + 90.0 + 80.0 + 70.0) / 4.0)

    assert stats.improvement_abs == pytest.approx(3.0)
    assert stats.improvement_pct == pytest.approx(0.3)

    assert stats.improving_generations == 2
    assert stats.last_improvement_generation == 4
    assert stats.max_stagnation_generations == 1


@pytest.mark.asyncio
async def test_clear_mission_removes_rows() -> None:
    repo = InMemoryPathSummaryRepo()
    svc = PathSummaryService(repo)

    repo._rows.extend(
        [
            PathSummary(mission_id=1, generation=1, cost=10.0, total_distance_m=100.0),
            PathSummary(mission_id=2, generation=1, cost=10.0, total_distance_m=100.0),
        ]
    )

    await svc.clear_mission(1)
    assert [r.mission_id for r in repo._rows] == [2]
