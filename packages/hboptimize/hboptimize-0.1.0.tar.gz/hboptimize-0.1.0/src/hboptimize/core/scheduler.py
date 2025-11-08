from __future__ import annotations
from typing import List, Dict, Any
import numpy as np
from .optimizer import propose_from_acquisition


class AsyncBatch:
    """
    Proposes batches of configurations by optimizing acquisition function.
    Uses Sobol+L-BFGS-B for efficient global optimization with pending penalization.
    """
    
    def __init__(self, acquisition, space, batch_size: int = 4, seed: int = 0):
        self.acq = acquisition
        self.space = space
        self.batch_size = batch_size
        self.seed = seed
        self.pending = []  # List of numeric vectors currently in-flight

    def propose(self, n: int) -> List[Dict[str, Any]]:
        """
        Optimize acquisition function to find next candidates.
        Uses local penalization to avoid suggesting near-pending points.
        
        Args:
            n: Number of candidates to propose
            
        Returns:
            List of parameter configs to evaluate next
        """
        def acq_with_penalty(x_vec: np.ndarray) -> float:
            """Acquisition with penalty against pending points."""
            base_acq = self.acq.value(x_vec)
            
            # Local penalization against pending points
            # Penalize points near pending evaluations
            pen = 0.0
            for p in self.pending:
                d = np.linalg.norm(x_vec - p)
                pen += -np.exp(-(d ** 2))  # Gaussian repulsion
            
            return base_acq + pen
        
        # Use gradient-based optimization with multi-start
        cands = propose_from_acquisition(
            self.space, 
            acq_with_penalty, 
            n=n, 
            seed=self.seed
        )
        
        # Track pending in numeric space
        self.pending.extend([self.space.to_array(c) for c in cands])
        
        return cands

    def update(self, surrogate, store):
        """
        Update incumbent and clear completed pending points.
        
        Args:
            surrogate: GP surrogate with observed data
            store: Result storage with best configuration
        """
        # Clear pending points that match observed X
        # Use numeric comparison with tolerance
        def _key(v):
            return tuple(np.round(np.asarray(v, float), 8))
        
        obs = {_key(x) for x in surrogate.X}
        self.pending = [p for p in self.pending if _key(p) not in obs]
        
        # Refresh robust incumbent for NoisyEI
        if hasattr(self.acq, 'refresh_incumbent'):
            X_obs = np.vstack(surrogate.X) if surrogate.X else np.zeros((0, self.space.n_dims))
            self.acq.refresh_incumbent(X_obs)
        else:
            # Legacy: use best observed
            _, y_best = store.best()
            if hasattr(self.acq, 'set_incumbent'):
                self.acq.set_incumbent(y_best)
            else:
                self.acq.incumbent = y_best


