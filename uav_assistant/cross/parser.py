from typing import TypeVar, Iterable, cast

T = TypeVar("T", bound=str)

def parse_literal(value: str, allowed: Iterable[T]) -> T:
    if value not in allowed:
        raise ValueError(f"Invalid value: {value}")
    return cast(T, value)
