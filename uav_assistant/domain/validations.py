# uav_assistant/domain/validation.py

from __future__ import annotations
from typing import Iterable, Sequence, Set

from .models import Path


def covers_required(path: Path, required_ids: Set[int]) -> bool:
    in_path = set(path.waypoint_ids)
    return required_ids.issubset(in_path)


def validate_unique_ids(path: Path) -> bool:
    ids = path.waypoint_ids
    return len(ids) == len(set(ids))

