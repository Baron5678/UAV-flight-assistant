from typing import Callable, Dict

from uav_assistant.infra.objective_functions.distance import (
    build_distance_ga,
    build_distance_es,
)
from uav_assistant.infra.objective_functions.energy import (
    build_energy_es,
    build_energy_ga,
)
from uav_assistant.infra.objective_functions.weather import (
    build_weather_ga,
    build_weather_es)


def _not_implemented(*args, **kwargs):
    raise NotImplementedError("Objective not implemented yet.")

class Objectives:
    GA: Dict[str, Callable] = {
        "DISTANCE": build_distance_ga,
        "ENERGY": build_energy_ga,
        "WEATHER": build_weather_ga,
    }

    ES: Dict[str, Callable] = {
        "DISTANCE": build_distance_es,
        "ENERGY": build_energy_es,
        "WEATHER": build_weather_es,
    }
