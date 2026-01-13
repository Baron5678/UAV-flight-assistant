import pytest

from uav_assistant.cross.parser import parse_literal


def test_parse_literal_accepts_allowed_value() -> None:
    assert parse_literal("GA", ["GA", "ES"]) == "GA"


def test_parse_literal_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        parse_literal("ABC", ["GA", "ES"])
