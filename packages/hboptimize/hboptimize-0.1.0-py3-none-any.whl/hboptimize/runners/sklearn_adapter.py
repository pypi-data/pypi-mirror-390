"""Sklearn model adapter for risk evaluation."""
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from ..exceptions import ConfigError


# Global dataset storage (user sets this before calling CV)
_DATASET: Tuple[np.ndarray, np.ndarray] | None = None


def set_data(X: np.ndarray, y: np.ndarray) -> None:
    """
    Set the dataset to be used for CV evaluation.
    
    Args:
        X: Feature matrix (n_samples, n_features)
        y: Target vector (n_samples,)
    """
    global _DATASET
    _DATASET = (X, y)


def get_data() -> Tuple[np.ndarray, np.ndarray]:
    """Get the currently set dataset."""
    if _DATASET is None:
        raise ConfigError("No dataset set. Call set_data(X, y) first.")
    return _DATASET


def build_estimator(cfg: Dict[str, Any], random_state: int = 0):
    """
    Build sklearn estimator from config dict.
    
    Args:
        cfg: Configuration dictionary with model hyperparameters
        random_state: Random seed for reproducibility
        
    Returns:
        Fitted sklearn estimator
        
    Example config:
        {"model": "ridge", "alpha": 0.1}
        {"model": "rf", "n_estimators": 100, "max_depth": 10}
    """
    model_type = cfg.get("model", "ridge")
    
    if model_type == "ridge":
        alpha = cfg.get("alpha", 1.0)
        return Ridge(alpha=alpha, random_state=random_state)
    
    elif model_type == "lasso":
        alpha = cfg.get("alpha", 1.0)
        return Lasso(alpha=alpha, random_state=random_state)
    
    elif model_type == "rf":
        n_estimators = cfg.get("n_estimators", 100)
        max_depth = cfg.get("max_depth", None)
        min_samples_split = cfg.get("min_samples_split", 2)
        return RandomForestRegressor(
            n_estimators=int(n_estimators),
            max_depth=int(max_depth) if max_depth else None,
            min_samples_split=int(min_samples_split),
            random_state=random_state
        )
    
    elif model_type == "gbm":
        n_estimators = cfg.get("n_estimators", 100)
        learning_rate = cfg.get("learning_rate", 0.1)
        max_depth = cfg.get("max_depth", 3)
        return GradientBoostingRegressor(
            n_estimators=int(n_estimators),
            learning_rate=float(learning_rate),
            max_depth=int(max_depth),
            random_state=random_state
        )
    
    elif model_type == "svr":
        C = cfg.get("C", 1.0)
        epsilon = cfg.get("epsilon", 0.1)
        return SVR(C=C, epsilon=epsilon)
    
    else:
        raise ConfigError(f"Unknown model type: {model_type}")
