from dataclasses import dataclass
from uav_assistant.app.interfaces import MissionRepository, PathRepository


@dataclass
class CancelMissionCommand:
    mission_id: int


class MissionService:
    def __init__(self, mission_repo: MissionRepository, path_repo: PathRepository) -> None:
        self._mission_repo = mission_repo
        self._path_repo = path_repo

    async def cancel_mission(self, cmd: CancelMissionCommand) -> None:
        await self._path_repo.delete_for_mission(cmd.mission_id)
        await self._mission_repo.delete(cmd.mission_id)
