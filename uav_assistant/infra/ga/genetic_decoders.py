import numpy as np
from typing import List, Sequence, Mapping, Any


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

def decode_with_stations(
    sol: np.ndarray,
    ids: Sequence[int],
    middle_ids: Sequence[int],
    id2role: Mapping[int, Any],
    threshold: float = 0.5,
) -> List[int]:

    keys = np.asarray(sol, dtype=float)

    if keys.shape[0] != len(middle_ids):
        raise ValueError(
            f"decode_with_stations: len(sol)={keys.shape[0]} "
            f"must equal len(middle_ids)={len(middle_ids)}"
        )

    selected: list[tuple[float, int]] = []

    for key, wid in zip(keys, middle_ids):
        role_obj = id2role.get(wid)
        if hasattr(role_obj, "value"):
            role_name = str(role_obj.value).upper()
        else:
            role_name = str(role_obj).upper()

        if role_name == "REQUIRED":
            selected.append((float(key), wid))
        elif role_name == "STATION":
            if key >= threshold:
                selected.append((float(key), wid))
        else:
            selected.append((float(key), wid))
    selected.sort(key=lambda t: (t[0], t[1]))
    ordered_middles = [wid for _, wid in selected]

    if not ids:
        raise ValueError("decode_with_stations: ids must not be empty")

    start_id = ids[0]
    end_id = ids[-1]

    return [start_id] + ordered_middles + [end_id]