from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, Iterable
from .core.search_space import SearchSpace
from .core.surrogate import HeteroGP
from .core.acquisition import NoisyEI
from .core.scheduler import AsyncBatch
from .risk.base import RiskEstimator
from .utils.storage import ResultStore


@dataclass
class Config:
    budget_evals: int = 100
    batch_size: int = 4
    seed: int = 0

class HBOptimize:
    def __init__(self,  
                 space: SearchSpace,
                 risk: RiskEstimator,
                 surrogate: Optional[HeteroGP] = None,
                 acquisition: Optional[NoisyEI] = None,
                 scheduler: Optional[AsyncBatch] = None,
                 config: Optional[Config] = None):
        self.space = space
        self.risk = risk
        self.surrogate = surrogate or HeteroGP(space)
        self.acq = acquisition or NoisyEI(self.surrogate)
        self.sched = scheduler or AsyncBatch(self.acq, self.space, batch_size=(config.batch_size if config else 4))
        self.cfg = config or Config()
        self.store = ResultStore()
    
    def suggest(self, n: Optional[int] = None) -> Iterable[Dict[str, Any]]:
        n = n or self.sched.batch_size
        return self.sched.propose(n)
    
    def observe(self, x: Dict[str, Any], mean: float, std: Optional[float] = None, 
                cost: Optional[float] = None, n_scores: Optional[int] = None):
        """
        Observe evaluation result and update surrogate.
        
        Args:
            x: Parameter configuration
            mean: Mean CV risk
            std: Standard deviation across CV folds
            cost: Evaluation cost (e.g., runtime)
            n_scores: Number of CV scores (folds × repeats) for SE calculation
        """
        self.store.add(x, mean, std, cost)
        self.surrogate.update(self.space.to_array(x), mean, std, n_scores)
        self.sched.update(self.surrogate, self.store)
    
    def best(self) -> Tuple[Dict[str, Any], float]:
        return self.store.best()
    
    def run(self):
        while len(self.store) < self.cfg.budget_evals:
            for x in self.suggest():
                mean, std, meta = self.risk.evaluate(x)
                # Thread n_scores to surrogate for correct noise model
                self.observe(x, mean, std, cost=meta.get('time'), n_scores=meta.get('n_scores'))
        return self.best()