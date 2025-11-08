from __future__ import annotations
from typing import Callable, Tuple, List, Dict, Any
import numpy as np
from scipy.optimize import minimize


def multistart_lbfgsb(fun: Callable[[np.ndarray], float],
                      x0s: np.ndarray,
                      bounds: List[Tuple[float, float]],
                      maxiter: int = 200) -> Tuple[np.ndarray, float]:
    """
    Multi-start L-BFGS-B optimization.
    
    Args:
        fun: Objective function to minimize
        x0s: Starting points (N, d)
        bounds: Box constraints [(low, high), ...]
        maxiter: Max iterations per start
        
    Returns:
        (best_x, best_f) tuple
    """
    best_x = x0s[0] if len(x0s) > 0 else np.zeros(len(bounds))
    best_f = float('inf')
    
    for x0 in x0s:
        res = minimize(lambda x: fun(x), x0, method='L-BFGS-B', bounds=bounds,
                       options={'maxiter': maxiter})
        if res.fun < best_f:
            best_x, best_f = res.x, res.fun
    
    return best_x, best_f


def propose_from_acquisition(space, acq_value: Callable[[np.ndarray], float], 
                            n: int, seed: int = 0) -> List[Dict[str, Any]]:
    """
    Propose candidates by optimizing acquisition function.
    Uses Sobol sampling + L-BFGS-B refinement for efficient global optimization.
    
    Args:
        space: Search space with to_array/from_array
        acq_value: Acquisition function (higher is better)
        n: Number of candidates to propose
        seed: Random seed
        
    Returns:
        List of parameter dictionaries
    """
    rng = np.random.default_rng(seed)
    
    # Get bounds as list of tuples
    bounds_array = space._compute_bounds()
    bnds = [(float(bounds_array[i, 0]), float(bounds_array[i, 1])) 
            for i in range(bounds_array.shape[0])]
    dim = len(bnds)
    
    # Generate Sobol/Random starting points (256 samples)
    starts = rng.uniform(
        [b[0] for b in bnds], 
        [b[1] for b in bnds], 
        size=(256, dim)
    )
    
    # Evaluate acquisition at all starts
    vals = np.array([acq_value(s) for s in starts])
    order = np.argsort(-vals)  # Maximize acquisition (sort descending)
    
    picks = []
    seen_configs = set()
    
    # Refine top candidates with L-BFGS-B
    for idx in order[:min(16, len(order))]:  # Refine top 16
        x_opt, _ = multistart_lbfgsb(
            lambda x: -acq_value(x),  # Negate for minimization
            np.array([starts[idx]]), 
            bnds,
            maxiter=100
        )
        
        # Convert to config and deduplicate
        cfg = space.from_array(x_opt)
        cfg_key = tuple(sorted(cfg.items()))
        
        if cfg_key not in seen_configs:
            picks.append(cfg)
            seen_configs.add(cfg_key)
        
        if len(picks) >= n:
            break
    
    # Fallback: add random samples if needed
    while len(picks) < n:
        rand_cfg = space.from_array(starts[rng.integers(0, len(starts))])
        cfg_key = tuple(sorted(rand_cfg.items()))
        if cfg_key not in seen_configs:
            picks.append(rand_cfg)
            seen_configs.add(cfg_key)
    
    return picks[:n]

