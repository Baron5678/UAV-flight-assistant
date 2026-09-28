from __future__ import annotations

from typing import TypedDict


class PathSnapshotDocument(TypedDict):
    mission_id: int
    config_id: int
    generation: int
    waypoint_ids: list[int]
    cost: float
    distance_m: float
