"""
Example 1: Ridge Regression Hyperparameter Tuning

This example demonstrates basic usage of HBOptimize for tuning Ridge regression
hyperparameters on a synthetic regression dataset.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from hboptimize import HBOptimize, SearchSpace, Real, Integer, Categorical, CVRisk, Config # type: ignore
from hboptimize.runners.sklearn_adapter import set_data # type: ignore

def main():
    print("=" * 70)
    print("Example 1: Ridge Regression Hyperparameter Tuning")
    print("=" * 70)
    
    # Create synthetic dataset
    np.random.seed(42)
    n_samples, n_features = 300, 20
    X = np.random.randn(n_samples, n_features)
    # True weights: sparse signal
    true_weights = np.zeros(n_features)
    true_weights[:5] = [2.0, -1.5, 3.0, -0.5, 1.0]
    y = X @ true_weights + np.random.randn(n_samples) * 0.5
    
    print(f"\nDataset: {n_samples} samples, {n_features} features")
    print(f"True signal: 5 non-zero weights")
    print(f"Noise level: 0.5")
    
    # Set dataset for CV evaluation
    set_data(X, y)
    
    # Define search space
    space = SearchSpace({
        'model': Categorical(('ridge',)),
        'alpha': Real(1e-3, 1e2, log10=True),
        'max_iter': Integer(100, 2000),
    })
    
    # Create CV risk estimator
    risk = CVRisk(k=5, repeats=3, metric='mse')
    
    # Configure optimization
    config = Config(
        budget_evals=30,
        batch_size=1,
        seed=42
    )
    
    # Run Bayesian Optimization
    print(f"\nRunning Bayesian Optimization...")
    print(f"  Budget: {config.budget_evals} evaluations")
    print(f"  CV: {risk.k}-fold, {risk.repeats} repeats")
    print("-" * 70)
    
    opt = HBOptimize(space, risk, config=config)
    best_params, best_score = opt.run()

    print("-" * 70)
    print("\nOptimization Complete!")
    print(f"\nBest Configuration:")
    for key, value in best_params.items():
        if key != 'model':
            print(f"  {key}: {value}")
    print(f"\nBest CV MSE: {best_score:.6f}")
    print(f"Total evaluations: {len(opt.store)}")
    
    # Show baseline performance (default alpha=1.0)
    print(f"\nBaseline (alpha=1.0): ", end="")
    baseline_cfg = {'model': 'ridge', 'alpha': 1.0, 'max_iter': 1000}
    baseline_mean, baseline_std, _ = risk.evaluate(baseline_cfg)
    print(f"{baseline_mean:.6f}")
    print(f"Improvement: {(baseline_mean - best_score) / baseline_mean * 100:.2f}%")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
