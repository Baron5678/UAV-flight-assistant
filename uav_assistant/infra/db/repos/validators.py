from __future__ import annotations


def validate_id(
    value: int,
    operation: str,
    entity_name: str,
) -> None:
    if value is None:
        raise ValueError(f"[{operation}]: {entity_name} id is not provided")
