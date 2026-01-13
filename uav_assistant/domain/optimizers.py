from __future__ import annotations

from uav_assistant.app.base_optimizer import BasePathOptimizer
from uav_assistant.app.interfaces import PathOptimizer
from uav_assistant.infra.ga.genetic_algorithm import run as run_ga
from uav_assistant.infra.es.es import run as run_es

RUNNERS = {
    "GA": run_ga,
    "ES": run_es,
}

def build_optimizer(algo: str) -> PathOptimizer:
    a = algo.strip().upper()
    if a in RUNNERS:
        return BasePathOptimizer(algo_name=a, runner=RUNNERS[a])
    raise ValueError(f"Unknown optimizer: {algo}")
