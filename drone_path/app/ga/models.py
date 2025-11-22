from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Iterable, Tuple, Optional, Set
import numpy as np

@dataclass
class Chromosome:
    path: List[int]
    meta: dict = field(default_factory=dict)

    def copy(self) -> "Chromosome":
        return Chromosome(self.path[:], dict(self.meta))

    def nodes(self) -> List[int]:
        return self.path[:]

    def edges(self, loop: bool = False) -> List[Tuple[int, int]]:
        if len(self.path) < 2:
            return []
        es = list(zip(self.path[:-1], self.path[1:]))
        if loop:
            es.append((self.path[-1], self.path[0]))
        return es

    def length_from_matrix(self, W: np.ndarray, loop: bool = False) -> float:
        return float(sum(W[i, j] for i, j in self.edges(loop=loop))) if len(self.path) >= 2 else 0.0

    def validate(
        self,
        start_id: Optional[int] = None,
        end_id: Optional[int] = None,
        required_ids: Optional[Iterable[int]] = None,
        k_min: Optional[int] = None,
        k_max: Optional[int] = None,
        loop: bool = False,
    ) -> Tuple[bool, str]:
        if not self.path:
            return False, "Empty path."

        if loop:
            if start_id is None or end_id is None or start_id != end_id:
                return False, "Loop mode requires start_id == end_id."
            if self.path[0] != start_id:
                return False, "Loop path must start at the base (start_id)."
            if self.path[-1] != start_id:
                return False, "Loop path must end at the base (start_id)."
        else:
            if start_id is not None and self.path[0] != start_id:
                return False, "Path must start at start_id."
            if end_id is not None and self.path[-1] != end_id:
                return False, "Path must end at end_id."

        if required_ids:
            missing = set(required_ids).difference(self.path)
            if missing:
                return False, f"Missing required IDs: {sorted(missing)}"

        n = len(self.path)
        if k_min is not None and n < k_min:
            return False, f"Path shorter than k_min ({k_min})."
        if k_max is not None and n > k_max:
            return False, f"Path longer than k_max ({k_max})."

        return True, "OK"

    def normalized_unique_intermediates(self, start_id: int, end_id: int, keep_first: bool = True) -> "Chromosome":
        if not self.path:
            return self.copy()

        if self.path[0] != start_id or self.path[-1] != end_id:
            raise ValueError("normalized_unique_intermediates expects full path with given start/end.")

        seen: Set[int] = {start_id, end_id}
        keep: List[int] = [start_id]
        for node in self.path[1:-1]:
            if (node not in seen) if keep_first else (node not in seen or keep.append(node) is None):
                keep.append(node)
                seen.add(node)
        keep.append(end_id)
        return Chromosome(keep, dict(self.meta))

    @staticmethod
    def from_midpoints(
        mids: Iterable[int],
        start_id: int,
        end_id: int,
        enforce_unique: bool = True
    ) -> "Chromosome":
        mids_list = list(mids)
        if enforce_unique:
            seen: Set[int] = set()
            mids_list = [x for x in mids_list if (x not in (start_id, end_id)) and (x not in seen and not seen.add(x))]
        path = [start_id] + mids_list + [end_id]
        return Chromosome(path)

    @staticmethod
    def loop_from_order(order: Iterable[int], base_id: int, enforce_unique: bool = True) -> "Chromosome":
        order_list = list(order)
        if enforce_unique:
            seen: Set[int] = {base_id}
            filtered = []
            for x in order_list:
                if x != base_id and x not in seen:
                    filtered.append(x)
                    seen.add(x)
            order_list = filtered
        return Chromosome([base_id] + order_list + [base_id])




