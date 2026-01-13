import pytest

from uav_assistant.app.interfaces import MissionRepository, PathRepository
from uav_assistant.app.services.mission import CancelMissionCommand, MissionService


class FakeMissionRepo(MissionRepository):
    def __init__(self) -> None:
        self.deleted: list[int] = []

    async def get(self, mission_id: int):
        raise NotImplementedError

    async def add(self, mission):
        raise NotImplementedError

    async def get_all(self):
        raise NotImplementedError

    async def set_best(self, mission_id: int, path, cost: float) -> None:
        raise NotImplementedError

    async def delete(self, mission_id: int) -> None:
        self.deleted.append(mission_id)


class FakePathRepo(PathRepository):
    def __init__(self) -> None:
        self.deleted_for_mission: list[int] = []

    async def save(self, mission_id: int, path, generation: int | None = None):
        raise NotImplementedError

    async def save_for_mission(self, mission_id: int, path):
        raise NotImplementedError

    async def get_by_mission(self, mission_id: int):
        raise NotImplementedError

    async def get(self, path_id: int):
        raise NotImplementedError

    async def delete_for_mission(self, mission_id: int) -> None:
        self.deleted_for_mission.append(mission_id)


@pytest.mark.asyncio
async def test_cancel_mission_deletes_paths_then_mission() -> None:
    mission_repo = FakeMissionRepo()
    path_repo = FakePathRepo()

    svc = MissionService(mission_repo=mission_repo, path_repo=path_repo)
    await svc.cancel_mission(CancelMissionCommand(mission_id=123))

    assert path_repo.deleted_for_mission == [123]
    assert mission_repo.deleted == [123]
