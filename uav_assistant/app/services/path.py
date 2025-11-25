from __future__ import annotations
from typing import Sequence
from uav_assistant.domain.models import Mission, Waypoint, Path, Drone, WaypointRole
from uav_assistant.domain import validations
from uav_assistant.app.interfaces import (
    MissionRepository,
    WaypointRepository,
    PathRepository,
    PathOptimizer,
)


class PathService:
    def __init__(
        self,
        mission_repo: MissionRepository,
        waypoint_repo: WaypointRepository,
        path_repo: PathRepository,
        optimizer: PathOptimizer,
    ) -> None:
        self._missions = mission_repo
        self._waypoints = waypoint_repo
        self._paths = path_repo
        self._optimizer = optimizer

    async def generate_best_path_for_mission(
        self,
        mission_id: int,
        drones: Sequence[Drone] | None = None,
    ) -> Path:
        if drones is None:
            drones = []
        mission = await self._missions.get(mission_id)
        candidates = await self._waypoints.get_for_mission(mission_id)
        path = await self._optimizer.optimize(mission, list(drones), candidates)

        starts = [w for w in candidates if w.role == WaypointRole.START]
        ends = [w for w in candidates if w.role == WaypointRole.END]

        if len(starts) != 1 or len(ends) != 1:
            raise ValueError("Mission must have exactly one START and one END waypoint.")

        required_ids = {
            w.id for w in candidates if w.role == WaypointRole.REQUIRED
        }
        if not validations.covers_required(path, required_ids):
            raise ValueError("Generated path does not cover all required waypoints.")
        if not validations.validate_unique_ids(path):
            raise ValueError("Generated path contains duplicate waypoints.")

        stored_path = await self._paths.save(
            mission_id=mission.id,
            path=path,
            generation=0
        )

        cost_value = stored_path.cost or 0.0
        await self._missions.set_best(mission_id=mission.id, path=stored_path, cost=cost_value)
        return stored_path
