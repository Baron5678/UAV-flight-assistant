from typing import Callable, Dict, Literal

from uav_assistant.infra.objective_functions.distance import (
    build_distance_ga,
    build_distance_es,
)
from uav_assistant.infra.objective_functions.energy import (
    build_energy_es,
    build_energy_ga,
)

ObjectiveName = Literal["DISTANCE", "ENERGY", "WEATHER"]

def _not_implemented(*args, **kwargs):
    raise NotImplementedError("Objective not implemented yet.")

class Objectives:
    GA: Dict[ObjectiveName, Callable] = {
        "DISTANCE": build_distance_ga,
        "ENERGY": build_energy_ga,
        "WEATHER": _not_implemented,
    }

    ES: Dict[ObjectiveName, Callable] = {
        "DISTANCE": build_distance_es,
        "ENERGY": build_energy_es,
        "WEATHER": _not_implemented,
    }
