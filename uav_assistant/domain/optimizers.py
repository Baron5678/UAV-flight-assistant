from __future__ import annotations

from uav_assistant.app.base_optimizer import BasePathOptimizer
from uav_assistant.app.interfaces import PathOptimizer
from uav_assistant.infra.ga.genetic_algorithm import solve_path as solve_ga_path
from uav_assistant.infra.es.es import solve_path as solve_es_path
from uav_assistant.infra.bf.perm import solve_path as solve_bf_path

RUNNERS = {
    "GA": solve_ga_path,
    "ES": solve_es_path,
    "BF": solve_bf_path
}

def build_optimizer(algo: str) -> PathOptimizer:
    a = algo.strip().upper()
    if a in RUNNERS:
        return BasePathOptimizer(algo_name=a, runner=RUNNERS[a])
    raise ValueError(f"Unknown optimizer: {algo}")
