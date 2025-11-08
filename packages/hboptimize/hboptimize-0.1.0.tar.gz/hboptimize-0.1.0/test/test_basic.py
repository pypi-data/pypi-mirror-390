"""Basic end-to-end test of HBOptimize package."""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from hboptimize.core.search_space import SearchSpace # type: ignore
from hboptimize.types import Real, Integer, Categorical # type: ignore
from hboptimize.risk.cv import CVRisk # type: ignore
from hboptimize.api import HBOptimize, Config # type: ignore
from hboptimize.runners.sklearn_adapter import set_data # type: ignore


def main():
    print("=" * 60)
    print("Testing HBOptimize Basic Functionality")
    print("=" * 60)
    
    # Create synthetic dataset
    print("\n1. Creating synthetic dataset...")
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = X[:, 0] + 2*X[:, 1] + np.random.randn(100) * 0.1
    set_data(X, y)
    print(f"   Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Define search space
    print("\n2. Defining search space...")
    space = SearchSpace({
        'model': Categorical(('ridge',)),  # Fixed model type
        'alpha': Real(1e-4, 1e1, log10=True),
        'max_iter': Integer(100, 1000)
    })
    print(f"   Parameters: {space.param_names}")
    print(f"   Dimensions: {space.n_dims}")
    
    # Create risk estimator
    print("\n3. Creating CV risk estimator...")
    risk = CVRisk(k=3, repeats=2, metric='mse')
    print(f"   Metric: MSE")
    print(f"   CV: 3-fold, 2 repeats")
    
    # Create optimizer with small budget for testing
    print("\n4. Creating HBOptimize optimizer...")
    config = Config(budget_evals=10, batch_size=1, seed=42)
    bo = HBOptimize(space, risk, config=config)
    print(f"   Budget: {config.budget_evals} evaluations")
    print(f"   Batch size: {config.batch_size}")
    
    # Run optimization
    print("\n5. Running optimization...")
    print("-" * 60)
    try:
        best_params, best_score = bo.run()
        
        print("-" * 60)
        print("\nOptimization completed successfully!")
        print(f"\nBest parameters found:")
        for k, v in best_params.items():
            print(f"   {k}: {v}")
        print(f"\nBest CV score: {best_score:.6f}")
        print(f"Total evaluations: {len(bo.store)}")
        
    except Exception as e:
        print(f"\nError during optimization:")
        print(f"   {type(e).__name__}: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
