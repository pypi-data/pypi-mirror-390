"""
Smoke test to verify HBOptimize is working correctly before publishing
"""
import numpy as np
from hboptimize import HBOptimize, SearchSpace, Real, Integer, Categorical, CVRisk
from hboptimize.runners.sklearn_adapter import set_data

print("Running smoke test...")
print("=" * 60)

# Create simple dataset
X = np.random.RandomState(0).randn(120, 10)
y = X[:,0] - 0.5*X[:,1] + np.random.randn(120)*0.2
set_data(X, y)

# Define search space
space = SearchSpace({
    "model": Categorical(("ridge","rf")),
    "alpha": Real(1e-6, 1e2, log10=True),
    "n_estimators": Integer(50, 150)
})

# Create risk estimator
risk = CVRisk(k=4, repeats=1, metric="mse", fixed_splits=True, seed=0)

# Run optimization
print("Running optimization with 10 evaluations...")
from hboptimize.api import Config
config = Config(budget_evals=10, seed=0)
bo = HBOptimize(space=space, risk=risk, config=config)
best_cfg, best_val = bo.run()

print("\n" + "=" * 60)
print("✓ Smoke test PASSED!")
print(f"Best config: {best_cfg}")
print(f"Best CV MSE: {best_val:.6f}")
print("=" * 60)
