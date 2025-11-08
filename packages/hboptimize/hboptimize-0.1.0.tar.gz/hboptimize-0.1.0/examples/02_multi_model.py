"""
Example 2: Comparing Multiple Model Types

This example shows how to optimize across different model types
(Ridge, Lasso, Random Forest) to find the best model and hyperparameters.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from hboptimize import HBOptimize, SearchSpace, Real, Integer, Categorical, CVRisk, Config # type: ignore
from hboptimize.runners.sklearn_adapter import set_data # type: ignore

def main():
    print("=" * 70)
    print("Example 2: Multi-Model Hyperparameter Tuning")
    print("=" * 70)
    
    # Create synthetic dataset with non-linear pattern
    np.random.seed(123)
    n_samples = 500
    X = np.random.randn(n_samples, 15)
    # Non-linear combination
    y = (X[:, 0] ** 2 + 
         2 * X[:, 1] + 
         np.sin(X[:, 2] * 3) + 
         np.random.randn(n_samples) * 0.3)
    
    print(f"\nDataset: {n_samples} samples, {X.shape[1]} features")
    print("Pattern: Non-linear (includes squared and sine terms)")
    
    set_data(X, y)
    
    # Define search space covering multiple models
    space = SearchSpace({
        'model': Categorical(('ridge', 'lasso', 'rf')),
        
        # Linear model parameters
        'alpha': Real(1e-3, 1e2, log10=True),
        'max_iter': Integer(100, 1000),
        
        # Random Forest parameters
        'n_estimators': Integer(10, 200),
        'max_depth': Integer(3, 20),
        'min_samples_split': Integer(2, 20),
    })
    
    # CV with fewer repeats for faster evaluation
    risk = CVRisk(k=5, repeats=2, metric='mse')
    
    # Run optimization
    config = Config(budget_evals=40, batch_size=1, seed=123)
    
    print(f"\nOptimizing over: Ridge, Lasso, Random Forest")
    print(f"Budget: {config.budget_evals} evaluations")
    print("-" * 70)
    
    opt = HBOptimize(space, risk, config=config)
    best_params, best_score = opt.run()

    print("-" * 70)
    print("\nOptimization Complete!")
    print(f"\nBest Model: {best_params['model']}")
    print(f"Best Configuration:")
    for key, value in best_params.items():
        if key != 'model':
            print(f"  {key}: {value}")
    print(f"\nBest CV MSE: {best_score:.6f}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
