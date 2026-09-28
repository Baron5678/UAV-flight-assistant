from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, ClassVar, Sequence
import numpy as np

from uav_assistant.cross.enums import ObjectiveFunction
from uav_assistant.domain.models import Waypoint

from uav_assistant.infra.objective_functions import distance, energy, weather


GeneSelector = Callable[[Sequence[Waypoint], int, int], list[int]]
DecodeFn = Callable[[np.ndarray], list[int]]
DecoderBuilder = Callable[..., DecodeFn]


class ObjectiveDecoderBuilder(ABC):
    objective: ClassVar[ObjectiveFunction]

    @classmethod
    def supports(cls, objective: ObjectiveFunction | str) -> bool:
        return cls.objective == ObjectiveFunction(objective)

    @classmethod
    @abstractmethod
    def select_genes(
        cls,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
    ) -> list[int]:
        ...

    @classmethod
    @abstractmethod
    def build_decoder(
        cls,
        *,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
        middles: list[int],
    ) -> DecodeFn:
        ...


class DistanceDecoderBuilder(ObjectiveDecoderBuilder):
    objective = ObjectiveFunction.DISTANCE

    @classmethod
    def select_genes(
        cls,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
    ) -> list[int]:
        return distance.select_genes(points, start_id, end_id)

    @classmethod
    def build_decoder(
        cls,
        *,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
        middles: list[int],
    ) -> DecodeFn:
        return distance.build_decoder(
            points=points,
            start_id=start_id,
            end_id=end_id,
            middles=middles,
        )


class EnergyDecoderBuilder(ObjectiveDecoderBuilder):
    objective = ObjectiveFunction.ENERGY

    @classmethod
    def select_genes(
        cls,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
    ) -> list[int]:
        return energy.select_genes(points, start_id, end_id)

    @classmethod
    def build_decoder(
        cls,
        *,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
        middles: list[int],
    ) -> DecodeFn:
        return energy.build_decoder(
            points=points,
            start_id=start_id,
            end_id=end_id,
            middles=middles,
        )


class WeatherDecoderBuilder(ObjectiveDecoderBuilder):
    objective = ObjectiveFunction.WEATHER

    @classmethod
    def select_genes(
        cls,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
    ) -> list[int]:
        return weather.select_genes(points, start_id, end_id)

    @classmethod
    def build_decoder(
        cls,
        *,
        points: Sequence[Waypoint],
        start_id: int,
        end_id: int,
        middles: list[int],
    ) -> DecodeFn:
        return weather.build_decoder(
            points=points,
            start_id=start_id,
            end_id=end_id,
            middles=middles,
        )


def get_decoder_builder(
    objective: ObjectiveFunction | str,
) -> type[ObjectiveDecoderBuilder]:
    for builder in ObjectiveDecoderBuilder.__subclasses__():
        if builder.supports(objective):
            return builder
    raise ValueError(f"Unsupported objective: {objective}")
