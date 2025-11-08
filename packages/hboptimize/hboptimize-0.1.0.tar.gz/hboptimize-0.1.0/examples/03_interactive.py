"""
Example 3: Interactive Optimization

This example shows the suggest-observe pattern for more control
over the optimization process, including custom logging and early stopping.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
from hboptimize import HBOptimize, SearchSpace, Real, Integer, Categorical, CVRisk # type: ignore
from hboptimize.runners.sklearn_adapter import set_data # type: ignore

def main():
    print("=" * 70)
    print("Example 3: Interactive Optimization with Custom Control")
    print("=" * 70)
    
    # Dataset
    np.random.seed(456)
    X = np.random.randn(200, 10)
    y = X[:, 0] + 2*X[:, 1] - X[:, 2] + np.random.randn(200) * 0.2
    set_data(X, y)
    
    print(f"\nDataset: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Search space
    space = SearchSpace({
        'model': Categorical(('ridge', 'lasso')),
        'alpha': Real(1e-4, 1e1, log10=True),
        'max_iter': Integer(100, 1500),
    })
    
    # Risk estimator
    risk = CVRisk(k=5, repeats=2, metric='mse')
    
    # Create optimizer (no config = manual control)
    opt = HBOptimize(space, risk)
    
    print("\nRunning interactive optimization...")
    print(f"Will stop if no improvement for 10 iterations")
    print("-" * 70)
    
    best_so_far = float('inf')
    no_improvement_count = 0
    max_no_improvement = 10
    
    for iteration in range(50):
        # Get next suggestion
        suggestions = opt.suggest(n=1)
        
        for cfg in suggestions:
            # Evaluate
            mean, std, meta = risk.evaluate(cfg)
            
            # Observe result
            opt.observe(cfg, mean, std, cost=meta.get('time'))
            
            # Track best
            current_best_params, current_best_score = opt.best()
            
            # Check for improvement
            if current_best_score < best_so_far - 1e-6:  # Small tolerance
                improvement = best_so_far - current_best_score
                best_so_far = current_best_score
                no_improvement_count = 0
                print(f"Iter {iteration+1:3d}: Score={current_best_score:.6f} "
                      f"(Improvement={improvement:.6f}) Model={current_best_params['model']}")
            else:
                no_improvement_count += 1
                print(f"Iter {iteration+1:3d}: Score={current_best_score:.6f} "
                      f"(no improvement {no_improvement_count}/{max_no_improvement})")
            
            # Early stopping
            if no_improvement_count >= max_no_improvement:
                print(f"\nStopping early: No improvement for {max_no_improvement} iterations")
                break
        
        if no_improvement_count >= max_no_improvement:
            break
    
    print("-" * 70)
    
    # Final results
    best_params, best_score = opt.best()
    print(f"\nOptimization Complete!")
    print(f"\nTotal evaluations: {len(opt.store)}")
    print(f"\nBest Configuration:")
    for key, value in best_params.items():
        print(f"  {key}: {value}")
    print(f"\nBest CV MSE: {best_score:.6f}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
