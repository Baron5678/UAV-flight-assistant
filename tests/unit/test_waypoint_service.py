import pytest

from uav_assistant.app.services.waypoint import AddWaypointCommand, WaypointService
from uav_assistant.cross.enums import WaypointRole
from uav_assistant.domain.models import Waypoint


class InMemoryWaypointRepo:
    def __init__(self) -> None:
        self._rows: list[Waypoint] = []
        self._next_id = 1

    async def add(self, waypoint: Waypoint) -> Waypoint:
        stored = Waypoint(
            id=self._next_id,
            name=waypoint.name,
            position=waypoint.position,
            role=waypoint.role,
            loss_chance=waypoint.loss_chance,
        )
        self._next_id += 1
        self._rows.append(stored)
        return stored

    async def delete(self, waypoint_id: int) -> None:
        self._rows = [w for w in self._rows if w.id != waypoint_id]

    async def get_all(self) -> list[Waypoint]:
        return list(self._rows)

    async def get_for_mission(self, mission_id: int) -> list[Waypoint]:
        raise NotImplementedError

    async def reset_all(self) -> None:
        self._rows = []
        self._next_id = 1


@pytest.mark.asyncio
async def test_add_waypoint_rejects_out_of_bounds_lat_lon() -> None:
    svc = WaypointService(InMemoryWaypointRepo())

    with pytest.raises(ValueError, match="out of bounds"):
        await svc.add_waypoint(AddWaypointCommand(name="bad", lat=95.0, lon=0.0, role=WaypointRole.REQUIRED))

    with pytest.raises(ValueError, match="out of bounds"):
        await svc.add_waypoint(AddWaypointCommand(name="bad", lat=0.0, lon=181.0, role=WaypointRole.REQUIRED))


@pytest.mark.asyncio
async def test_add_waypoint_enforces_single_start() -> None:
    repo = InMemoryWaypointRepo()
    svc = WaypointService(repo)

    w1 = await svc.add_waypoint(AddWaypointCommand(name="s1", lat=0.0, lon=0.0, role=WaypointRole.START))
    assert w1.role == WaypointRole.START

    with pytest.raises(ValueError, match="already a START"):
        await svc.add_waypoint(AddWaypointCommand(name="s2", lat=0.1, lon=0.1, role=WaypointRole.START))


@pytest.mark.asyncio
async def test_add_waypoint_enforces_single_end() -> None:
    repo = InMemoryWaypointRepo()
    svc = WaypointService(repo)

    w1 = await svc.add_waypoint(AddWaypointCommand(name="e1", lat=0.0, lon=0.0, role=WaypointRole.END))
    assert w1.role == WaypointRole.END

    with pytest.raises(ValueError, match="already a END"):
        await svc.add_waypoint(AddWaypointCommand(name="e2", lat=0.1, lon=0.1, role=WaypointRole.END))


@pytest.mark.asyncio
async def test_add_waypoint_persists_and_returns_stored_entity() -> None:
    repo = InMemoryWaypointRepo()
    svc = WaypointService(repo)

    cmd = AddWaypointCommand(name="wp", lat=10.0, lon=20.0, role=WaypointRole.REQUIRED, loss_chance=0.5)
    stored = await svc.add_waypoint(cmd)

    assert stored.id == 1
    assert stored.name == "wp"
    assert stored.position.lat == pytest.approx(10.0)
    assert stored.position.lon == pytest.approx(20.0)
    assert stored.role == WaypointRole.REQUIRED
    assert stored.loss_chance == pytest.approx(0.5)
