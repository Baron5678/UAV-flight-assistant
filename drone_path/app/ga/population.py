import numpy as np
from typing import Sequence, Optional


def build_initial_population(
    *,
    waypoint_ids: Sequence[int],
    pop_size: int = 200,
) -> np.ndarray:
    n = len(waypoint_ids)
    rng = np.random.default_rng(n)
    pop = rng.uniform(0.0, 1.0, size=(pop_size, n))
    return pop
