from __future__ import annotations
import numpy as np
from math import erf, sqrt, exp, pi


class NoisyEI:
    """
    Noisy Expected Improvement acquisition function.
    Uses robust incumbent based on posterior mean (with optional credible bound).
    """
    
    def __init__(self, surrogate, kappa: float = 0.0):
        """
        Args:
            surrogate: GP surrogate model
            kappa: Credible bound multiplier (0=use posterior mean, >0 more conservative)
        """
        self.surr = surrogate
        self.kappa = kappa
        self.incumbent = None  # Scalar threshold for EI

    def refresh_incumbent(self, X_obs: np.ndarray):
        """
        Compute robust incumbent from posterior at observed points.
        Uses lower credible bound: mu - kappa*sigma to be noise-aware.
        
        Args:
            X_obs: Array of observed points in transformed space (N, d)
        """
        if X_obs.size == 0 or len(X_obs) == 0:
            self.incumbent = None
            return
        
        # Get posterior mean and variance at all observed points
        mus, vars_ = zip(*(self.surr.predict(x) for x in X_obs))
        mus = np.array(mus)
        sig = np.sqrt(np.maximum(np.array(vars_), 1e-12))
        
        # Lower credible bound: mu - kappa*sigma
        # kappa=0 -> use posterior mean (best for noise)
        # kappa>0 -> more conservative (for high noise)
        scores = mus - self.kappa * sig
        self.incumbent = float(np.min(scores))

    def set_incumbent(self, value: float):
        """Set incumbent directly (legacy interface)."""
        self.incumbent = value

    def value(self, x_vec: np.ndarray) -> float:
        """
        Compute Expected Improvement at x_vec.
        
        Args:
            x_vec: Point in transformed space
            
        Returns:
            EI value (higher is better)
        """
        if self.incumbent is None:
            return 0.0
        
        mu, var = self.surr.predict(x_vec)
        sigma = sqrt(max(var, 1e-12))
        
        # Improvement = incumbent - mu (we're minimizing)
        z = (self.incumbent - mu) / sigma
        
        # EI formula: (incumbent - mu) * Phi(z) + sigma * phi(z)
        # where Phi is CDF and phi is PDF of standard normal
        Phi = 0.5 * (1.0 + erf(z / sqrt(2)))
        phi = (1.0 / sqrt(2 * pi)) * exp(-0.5 * z * z)
        
        ei = (self.incumbent - mu) * Phi + sigma * phi
        return ei

