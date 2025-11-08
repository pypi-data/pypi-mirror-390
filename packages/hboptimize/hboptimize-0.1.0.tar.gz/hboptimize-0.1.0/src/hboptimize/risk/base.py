from __future__ import annotations
from typing import Dict, Any, Tuple

class RiskEstimator:
    def evaluate(self, cfg: Dict[str, Any]) -> Tuple[float, float, Dict[str, Any]]:
        raise NotImplementedError
