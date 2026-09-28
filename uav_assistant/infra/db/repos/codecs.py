from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from uav_assistant.app.interfaces import AlgorithmSpecificConfiguration
from uav_assistant.domain.models import (
    AlgorithmConfiguration as DomAlgorithmConfiguration,
    ESConfiguration as DomESConfiguration,
    GAConfiguration as DomGAConfiguration,
)


class AlgorithmConfigurationCodec(ABC):
    algorithm: ClassVar[str]

    @classmethod
    def supports(cls, algorithm: str) -> bool:
        return cls.algorithm == algorithm.upper()

    @classmethod
    @abstractmethod
    def encode(
        cls,
        config: AlgorithmSpecificConfiguration,
    ) -> dict[str, str]:
        ...

    @classmethod
    @abstractmethod
    def decode(
        cls,
        config: DomAlgorithmConfiguration,
        parameters: dict[str, str],
    ) -> AlgorithmSpecificConfiguration:
        ...


class GAConfigurationCodec(AlgorithmConfigurationCodec):
    algorithm = "GA"

    @classmethod
    def encode(
        cls,
        config: AlgorithmSpecificConfiguration,
    ) -> dict[str, str]:
        if not isinstance(config, DomGAConfiguration):
            raise TypeError("GA parameters require GAConfiguration")
        return {
            "mutation_probability": str(config.mutation_probability),
            "keep_elitism": str(config.keep_elitism),
            "k_tournament": str(config.k_tournament),
        }

    @classmethod
    def decode(
        cls,
        config: DomAlgorithmConfiguration,
        parameters: dict[str, str],
    ) -> DomGAConfiguration:
        try:
            return DomGAConfiguration(
                config=config,
                mutation_probability=float(parameters["mutation_probability"]),
                keep_elitism=int(parameters["keep_elitism"]),
                k_tournament=int(parameters["k_tournament"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid parameters for GA configuration") from exc


class ESConfigurationCodec(AlgorithmConfigurationCodec):
    algorithm = "ES"

    @classmethod
    def encode(
        cls,
        config: AlgorithmSpecificConfiguration,
    ) -> dict[str, str]:
        if not isinstance(config, DomESConfiguration):
            raise TypeError("ES parameters require ESConfiguration")
        return {"sigma0": str(config.sigma0)}

    @classmethod
    def decode(
        cls,
        config: DomAlgorithmConfiguration,
        parameters: dict[str, str],
    ) -> DomESConfiguration:
        try:
            return DomESConfiguration(
                config=config,
                sigma0=float(parameters["sigma0"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid parameters for ES configuration") from exc


def get_configuration_codec(
    algorithm: str,
) -> type[AlgorithmConfigurationCodec]:
    for codec in AlgorithmConfigurationCodec.__subclasses__():
        if codec.supports(algorithm):
            return codec
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def encode_configuration_parameters(
    config: AlgorithmSpecificConfiguration,
) -> dict[str, str]:
    codec = get_configuration_codec(config.config.algo)
    return codec.encode(config)
