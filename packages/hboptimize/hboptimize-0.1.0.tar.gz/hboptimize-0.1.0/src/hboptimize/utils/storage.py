from __future__ import annotations
from typing import Dict, Any, List, Tuple

class ResultStore:
    def __init__(self):
        self.rows: List[Tuple[Dict[str, Any], float, float | None, float | None]] = []

    def add(self, x, mean, std=None, cost=None):
        self.rows.append((x, mean, std, cost))

    def best(self):
        if not self.rows: return {}, float("inf")
        x, y, *_ = min(self.rows, key=lambda r: r[1])
        return x, y

    def __len__(self): return len(self.rows)
