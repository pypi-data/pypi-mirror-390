from __future__ import annotations
from typing import Dict, Any, Tuple, List
import time, numpy as np
import hashlib
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error
from .base import RiskEstimator
from ..exceptions import RiskComputationError
from ..utils.seeding import seed_all
from ..runners.sklearn_adapter import build_estimator
from ..runners.sklearn_adapter import get_data


METRICS = {
    "mse": lambda y, yhat: mean_squared_error(y, yhat),
    "mae": lambda y, yhat: mean_absolute_error(y, yhat),
}

class CVRisk(RiskEstimator):
    def __init__(self, k: int = 8, repeats: int = 1, metric: str = 'mse', 
                 fixed_splits: bool = True, seed: int = 0):
        self.k, self.repeats, self.metric = k, repeats, metric
        self.fixed_splits, self.seed = fixed_splits, seed
        if metric not in METRICS:
            raise RiskComputationError(f'Unsupported metric: {metric}')
        self._splits_cache: List[List[tuple[np.ndarray,np.ndarray]]] = []
        self._split_hash: str | None = None  # Hash of CV split indices

    def _get_splits(self, n: int) -> List[List[tuple[np.ndarray,np.ndarray]]]:
        if self._splits_cache and self.fixed_splits:
            return self._splits_cache
        rng = np.random.default_rng(self.seed)
        all_reps = []
        for r in range(self.repeats):
            kf = KFold(n_splits=self.k, shuffle=True, random_state=int(rng.integers(0, 2**31-1)))
            rep = [(tr, vl) for tr, vl in kf.split(np.arange(n))]
            all_reps.append(rep)
        if self.fixed_splits:
            self._splits_cache = all_reps
            # Compute hash of split indices for reproducibility tracking
            self._split_hash = self._compute_split_hash(all_reps)
        return all_reps
    
    def _compute_split_hash(self, splits: List[List[tuple[np.ndarray,np.ndarray]]]) -> str:
        """
        Compute hash of CV split indices for reproducibility.
        Useful for debugging and ensuring same splits across runs.
        """
        hasher = hashlib.sha256()
        for rep in splits:
            for tr_idx, vl_idx in rep:
                # Hash the indices
                hasher.update(tr_idx.tobytes())
                hasher.update(vl_idx.tobytes())
        return hasher.hexdigest()[:16]  # Return first 16 chars

    def evaluate(self, cfg: Dict[str, Any]) -> Tuple[float, float, Dict[str, Any]]:
        """
        Evaluate configuration using repeated K-fold cross-validation.
        
        Args:
            cfg: Configuration dictionary with hyperparameters
            
        Returns:
            Tuple of (mean_score, std_score, metadata)
            
        Raises:
            RiskComputationError: If evaluation fails
        """
        try:
            # Expect user to have set a dataset in adapter
            X, y = get_data()
            n = X.shape[0]
            splits = self._get_splits(n)
            metric_fn = METRICS[self.metric]

            t0 = time.time()
            scores: List[float] = []
            
            for rep in splits:
                for tr_idx, vl_idx in rep:
                    try:
                        seed_all(self.seed)  # keep paired randomness fixed across cfgs
                        est = build_estimator(cfg, random_state=self.seed)
                        est.fit(X[tr_idx], y[tr_idx])
                        yhat = est.predict(X[vl_idx])
                        scores.append(float(metric_fn(y[vl_idx], yhat)))
                    except Exception as e:
                        raise RiskComputationError(
                            f"Failed to evaluate fold: {e}"
                        ) from e
            
            mean = float(np.mean(scores))
            std = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0
            
            # Include split hash in metadata for reproducibility
            meta = {
                'time': time.time() - t0, 
                'n_scores': len(scores),
            }
            if self._split_hash:
                meta['split_hash'] = self._split_hash
            
            return mean, std, meta
            
        except RiskComputationError:
            raise
        except Exception as e:
            raise RiskComputationError(
                f"CV evaluation failed for config {cfg}: {e}"
            ) from e
