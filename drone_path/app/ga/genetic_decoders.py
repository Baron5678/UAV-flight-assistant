import numpy as np
from typing import List

def decode(
    sol: np.ndarray,
    ids: List[int],
    middles: List[int],
) -> List[int]:
    keys = np.asarray(sol, dtype=float)

    if keys.shape[0] != len(middles):
        raise ValueError(
            f"decode: len(sol)={keys.shape[0]} must equal len(middles)={len(middles)}"
        )

    pairs = sorted(zip(keys, middles), key=lambda t: (t[0], t[1]))
    ordered_middles = [mid for _, mid in pairs]

    start_id = ids[0]
    end_id = ids[-1]

    return [start_id] + ordered_middles + [end_id]
