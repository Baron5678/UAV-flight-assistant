from __future__ import annotations

from typing import Callable, Dict, Literal, Sequence
import numpy as np

from uav_assistant.domain.models import Waypoint

from uav_assistant.infra.objective_functions import distance, energy, weather


GeneSelector = Callable[[Sequence[Waypoint], int, int], list[int]]
DecodeFn = Callable[[np.ndarray], list[int]]
DecoderBuilder = Callable[..., DecodeFn]



class Decoders:
    GENES: Dict[str, GeneSelector] = {
        "DISTANCE": distance.select_genes,
        "ENERGY": energy.select_genes,
        "WEATHER": weather.select_genes,
    }
    BUILD: Dict[str, DecoderBuilder] = {
        "DISTANCE": distance.build_decoder,
        "ENERGY": energy.build_decoder,
        "WEATHER": weather.build_decoder,
    }
