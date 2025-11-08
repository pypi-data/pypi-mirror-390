from __future__ import annotations
import warnings
import numpy as np
from typing import Tuple
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel, WhiteKernel
from sklearn.exceptions import ConvergenceWarning

# Suppress GP convergence warnings for cleaner output (specific to sklearn GP)
warnings.filterwarnings('ignore', category=ConvergenceWarning)


class HeteroGP:
    """
    Gaussian Process surrogate with heteroscedastic noise modeling.
    Uses sklearn's GP with per-observation noise (alpha) based on CV standard error.
    Optionally applies log transform to handle skewed objectives.
    """
    
    def __init__(self, space, kernel_type: str = "Matern32", ard: bool = True, 
                 noise_floor: float = 1e-8, use_log_warp: bool = False, fit_every: int = 1):
        self.space = space
        self.X = []  # Observed inputs (transformed space)
        self.y = []  # Observed means
        self.s2 = []  # Observed variances (SE² = std²/n_scores)
        self.noise_floor = noise_floor
        self.use_log_warp = use_log_warp
        self.y_min = None  # Track minimum for log transform
        self.fit_every = max(1, fit_every)  # Refit GP every N observations
        self._since_last_fit = 0  # Counter for throttling refits
        
        # Build kernel
        n_dims = space.n_dims if hasattr(space, 'n_dims') else 1
        
        # Matern kernel with ARD (automatic relevance determination)
        if kernel_type == "Matern32":
            nu = 1.5
        elif kernel_type == "Matern52":
            nu = 2.5
        else:  # Default to Matern32
            nu = 1.5
        
        lengthscales = np.ones(n_dims)
        base_kernel = ConstantKernel(1.0, constant_value_bounds=(1e-3, 1e3)) * \
                      Matern(length_scale=lengthscales, length_scale_bounds=(1e-3, 1e3), nu=nu)
        
        # Add white noise kernel with small floor
        self.kernel = base_kernel + WhiteKernel(noise_level=noise_floor, 
                                                 noise_level_bounds=(1e-12, 1e-1))
        
        self.gp = GaussianProcessRegressor(
            kernel=self.kernel,
            normalize_y=True,  # Standardize y for better hyperparameter learning
            n_restarts_optimizer=3,
            alpha=1e-10  # Will be overridden per-observation
        )
        self._fitted = False
    
    def _warp_y(self, y: np.ndarray) -> np.ndarray:
        """Apply log warp to objective (helps with skewed distributions)."""
        if not self.use_log_warp:
            return y
        
        # log(y - y_min + eps) where eps ensures positivity
        if self.y_min is None:
            self.y_min = float(np.min(y)) - 0.1 * np.abs(np.min(y))
        
        eps = 1e-6
        return np.log(y - self.y_min + eps)
    
    def _unwarp_y(self, y_warped: float, var_warped: float) -> Tuple[float, float]:
        """Inverse transform with delta method for variance."""
        if not self.use_log_warp:
            return y_warped, var_warped
        
        eps = 1e-6
        # y = exp(y_warped) + y_min - eps
        y_orig = np.exp(y_warped) + self.y_min - eps
        
        # Delta method: Var[exp(Y)] ≈ exp(2μ) * Var[Y]
        var_orig = np.exp(2 * y_warped) * var_warped
        
        return float(y_orig), float(var_orig)

    def update(self, x_vec: np.ndarray, mean: float, std: float | None, n_scores: int | None = None):
        """
        Add new observation and refit GP.
        
        Args:
            x_vec: Parameter vector in transformed space
            mean: Mean CV risk
            std: Standard deviation across CV folds
            n_scores: Number of CV scores (folds × repeats) for SE calculation
        """
        self.X.append(np.asarray(x_vec, float))
        self.y.append(float(mean))
        
        # Convert CV std -> variance of the mean (standard error squared)
        # Var[mean] ≈ std² / n_scores
        if std is None or n_scores in (None, 0):
            var_obs = self.noise_floor
        else:
            var_obs = max((std ** 2) / float(n_scores), self.noise_floor)
        self.s2.append(var_obs)
        
        # Increment refit counter
        self._since_last_fit += 1
        
        # Refit GP with all data (heteroscedastic noise via alpha)
        # Only refit every fit_every observations to save computation
        if len(self.X) >= 3 and self._since_last_fit >= self.fit_every:  # Need at least 3 points
            X_array = np.vstack(self.X)
            y_array = np.array(self.y)
            
            # Apply warp if enabled
            y_warped = self._warp_y(y_array)
            
            alpha = np.array(self.s2)  # Per-observation noise variance
            
            try:
                # Set heteroscedastic alpha and fit
                self.gp.set_params(alpha=alpha)
                self.gp.fit(X_array, y_warped)
                self._fitted = True
                self._since_last_fit = 0  # Reset counter after refit
            except Exception as e:
                print(f"Warning: GP fit failed: {e}")
                self._fitted = False
    
    def predict(self, x_vec: np.ndarray) -> tuple[float, float]:
        """
        Predict mean and variance at x_vec.
        
        Returns:
            (mean, variance) tuple in original space
        """
        if not self._fitted or len(self.X) < 2:
            # Not enough data - return empirical prior
            prior_mean = float(np.mean(self.y)) if self.y else 0.0
            prior_var = float(np.var(self.y)) if len(self.y) > 1 else 1.0
            return prior_mean, prior_var
        
        x_vec = np.atleast_2d(x_vec)
        
        try:
            mu_warped, sigma_warped = self.gp.predict(x_vec, return_std=True)  # type: ignore
            var_warped = float(sigma_warped[0] ** 2)
            
            # Unwarp if log transform was used
            mu, var = self._unwarp_y(float(mu_warped[0]), var_warped)
            return mu, var
        except Exception as e:
            print(f"Warning: GP prediction failed: {e}")
            # Fallback to empirical mean/var
            return float(np.mean(self.y)), float(np.var(self.y))
    
    def sample_y(self, x_vec: np.ndarray, n_samples: int = 1) -> np.ndarray:
        """Sample from posterior (for Thompson Sampling)."""
        if not self._fitted:
            return np.random.randn(n_samples) * 0.1
        
        x_vec = np.atleast_2d(x_vec)
        try:
            return self.gp.sample_y(x_vec, n_samples=n_samples).flatten()
        except Exception:
            mu, var = self.predict(x_vec)
            return np.random.randn(n_samples) * np.sqrt(var) + mu