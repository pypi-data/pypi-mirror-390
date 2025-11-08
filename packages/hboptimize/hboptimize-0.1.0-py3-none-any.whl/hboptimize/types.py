from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional, Sequence, Tuple, TypedDict, Union


Number = Union[int, float]

# --------------------------
# Parameter specifications
# --------------------------

@dataclass(frozen=True)
class Real:
    """Continuous parameter in [low, high]. Optionally optimize in log10 domain."""
    low: float
    high: float
    log10: bool = False
    default_value: Optional[float] = None

    def check(self, x: Number) -> bool:
        return isinstance(x, (int, float)) and self.low <= float(x) <= self.high

    def default(self) -> float:
        if self.default_value is not None:
            return float(self.default_value)
        return (self.low + self.high) / 2.0


@dataclass(frozen=True)
class Integer:
    """Integer parameter in [low, high]."""
    low: int
    high: int
    default_value: Optional[int] = None

    def check(self, x: Number) -> bool:
        try:
            xi = int(x)
        except Exception:
            return False
        return self.low <= xi <= self.high

    def default(self) -> int:
        if self.default_value is not None:
            return int(self.default_value)
        return int((self.low + self.high) // 2)


@dataclass(frozen=True)
class Categorical:
    """Categorical parameter with finite choices."""
    choices: Tuple[Any, ...]
    default_index: int = 0

    def check(self, x: Any) -> bool:
        return x in self.choices

    def default(self) -> Any:
        idx = min(max(self.default_index, 0), len(self.choices) - 1)
        return self.choices[idx]


ParamSpec = Union[Real, Integer, Categorical]
SpecDict = Mapping[str, ParamSpec]

# --------------------------
# Runtime records
# --------------------------

class Observation(TypedDict, total=False):
    x: Dict[str, Any]          # config dict
    mean: float                # mean risk (lower is better)
    std: float                 # std/SE of risk estimator (e.g., CV std)
    cost: float                # runtime (seconds) or user-defined cost

class Suggestion(TypedDict):
    x: Dict[str, Any]

class BestResult(TypedDict):
    x: Dict[str, Any]
    mean: float

# --------------------------
# Utilities
# --------------------------

def is_numeric_param(p: ParamSpec) -> bool:
    return isinstance(p, (Real, Integer))

def is_categorical_param(p: ParamSpec) -> bool:
    return isinstance(p, Categorical)
