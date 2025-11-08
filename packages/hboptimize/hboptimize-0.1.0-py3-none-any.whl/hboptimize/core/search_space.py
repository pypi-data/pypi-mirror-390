from __future__ import annotations
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy.stats import qmc
from ..types import SpecDict, Real, Integer, Categorical, ParamSpec
from ..exceptions import SpaceError


class SearchSpace:
    """
    Manages parameter transformations and sampling.
    Converts between config dicts and continuous arrays for GP modeling.
    """
    
    def __init__(self, spec: SpecDict):
        self.spec = dict(spec)
        self.param_names = list(self.spec.keys())
        self.n_dims = len(self.param_names)
        
        # Build bounds for each dimension in transformed space
        self._bounds = self._compute_bounds()
        
    def _compute_bounds(self) -> np.ndarray:
        """Compute bounds in transformed (unconstrained) space."""
        bounds = []
        for name in self.param_names:
            param = self.spec[name]
            if isinstance(param, Real):
                if param.log10:
                    # log10 transform: bounds become log10(low), log10(high)
                    bounds.append([np.log10(param.low), np.log10(param.high)])
                else:
                    bounds.append([param.low, param.high])
            elif isinstance(param, Integer):
                # Integers: use continuous relaxation [low-0.5, high+0.5]
                bounds.append([param.low - 0.5, param.high + 0.5])
            elif isinstance(param, Categorical):
                # Categorical: index space [0, n_choices-1]
                bounds.append([0, len(param.choices) - 1])
            else:
                raise SpaceError(f"Unknown parameter type: {type(param)}")
        return np.array(bounds)
    
    @property
    def bounds(self) -> np.ndarray:
        """Returns (n_dims, 2) array of [low, high] for each dimension."""
        return self._bounds
    
    def sample(self, n: int, method: str = "sobol", seed: int = 0) -> List[Dict[str, Any]]:
        """
        Generate n initial samples using space-filling design.
        
        Args:
            n: Number of samples
            method: 'sobol', 'lhs', or 'random'
            seed: Random seed
            
        Returns:
            List of config dicts
        """
        rng = np.random.default_rng(seed)
        
        if method == "sobol":
            sampler = qmc.Sobol(d=self.n_dims, scramble=True)
            sampler.reset()
            # Skip ahead based on seed for reproducibility
            if seed > 0:
                sampler.fast_forward(seed)
            # Generate samples in [0,1]^d then scale to bounds
            samples_unit = sampler.random(n)
        elif method == "lhs":
            sampler = qmc.LatinHypercube(d=self.n_dims)
            # Use internal RNG state for reproducibility
            np.random.seed(seed)
            samples_unit = sampler.random(n)
        elif method == "random":
            samples_unit = rng.random((n, self.n_dims))
        else:
            raise SpaceError(f"Unknown sampling method: {method}")
        
        # Scale from [0,1] to bounds
        lower = self._bounds[:, 0]
        upper = self._bounds[:, 1]
        samples_scaled = qmc.scale(samples_unit, lower, upper)
        
        # Convert to config dicts
        return [self.from_array(x) for x in samples_scaled]
    
    def default(self) -> Dict[str, Any]:
        """Return default configuration (midpoint of ranges)."""
        return {k: v.default() for k, v in self.spec.items()}
    
    def to_array(self, x: Dict[str, Any]) -> np.ndarray:
        """
        Convert config dict to continuous array (transformed space).
        
        Args:
            x: Configuration dict
            
        Returns:
            1D numpy array of shape (n_dims,)
        """
        arr = np.zeros(self.n_dims)
        for i, name in enumerate(self.param_names):
            param = self.spec[name]
            val = x.get(name)
            
            if val is None:
                raise SpaceError(f"Missing parameter: {name}")
            
            if isinstance(param, Real):
                if not param.check(val):
                    raise SpaceError(f"Value {val} out of bounds for {name}")
                # Apply log10 transform if needed
                arr[i] = np.log10(float(val)) if param.log10 else float(val)
                
            elif isinstance(param, Integer):
                if not param.check(val):
                    raise SpaceError(f"Value {val} out of bounds for {name}")
                arr[i] = float(val)
                
            elif isinstance(param, Categorical):
                if val not in param.choices:
                    raise SpaceError(f"Invalid choice {val} for {name}")
                arr[i] = float(param.choices.index(val))
                
            else:
                raise SpaceError(f"Unknown parameter type: {type(param)}")
        
        return arr
    
    def from_array(self, arr: np.ndarray) -> Dict[str, Any]:
        """
        Convert continuous array back to config dict.
        
        Args:
            arr: 1D numpy array of shape (n_dims,)
            
        Returns:
            Configuration dict
        """
        if arr.shape[0] != self.n_dims:
            raise SpaceError(f"Array shape {arr.shape} doesn't match n_dims={self.n_dims}")
        
        cfg = {}
        for i, name in enumerate(self.param_names):
            param = self.spec[name]
            val = arr[i]
            
            if isinstance(param, Real):
                # Reverse log10 if needed
                v = 10 ** val if param.log10 else val
                # Clip to bounds
                v = np.clip(v, param.low, param.high)
                cfg[name] = float(v)
                
            elif isinstance(param, Integer):
                # Round to nearest integer
                v = int(np.round(val))
                # Clip to bounds
                v = np.clip(v, param.low, param.high)
                cfg[name] = int(v)
                
            elif isinstance(param, Categorical):
                # Round to nearest index
                idx = int(np.round(val))
                idx = np.clip(idx, 0, len(param.choices) - 1)
                cfg[name] = param.choices[idx]
                
            else:
                raise SpaceError(f"Unknown parameter type: {type(param)}")
        
        return cfg
    
    def validate(self, x: Dict[str, Any]) -> bool:
        """Check if configuration is valid."""
        try:
            for name, param in self.spec.items():
                val = x.get(name)
                if val is None:
                    return False
                if hasattr(param, 'check') and not param.check(val):
                    return False
            return True
        except Exception:
            return False
    
    def distance(self, x1: Dict[str, Any], x2: Dict[str, Any]) -> float:
        """Compute L2 distance in transformed space."""
        arr1 = self.to_array(x1)
        arr2 = self.to_array(x2)
        return float(np.linalg.norm(arr1 - arr2))