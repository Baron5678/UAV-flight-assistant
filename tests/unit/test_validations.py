import pytest

from uav_assistant.domain.models import Path
from uav_assistant.domain.validations import covers_required, validate_unique_ids


def test_covers_required_true_when_subset() -> None:
    path = Path(waypoint_ids=[1, 2, 3, 4])
    assert covers_required(path, {2, 4}) is True


def test_covers_required_false_when_missing_any() -> None:
    path = Path(waypoint_ids=[1, 2, 3])
    assert covers_required(path, {2, 4}) is False


def test_validate_unique_ids_true_when_no_duplicates() -> None:
    path = Path(waypoint_ids=[1, 2, 3])
    assert validate_unique_ids(path) is True


def test_validate_unique_ids_false_when_duplicates_present() -> None:
    path = Path(waypoint_ids=[1, 2, 2, 3])
    assert validate_unique_ids(path) is False
