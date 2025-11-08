# HBOptimize Examples

This directory contains example scripts demonstrating various features of HBOptimize.

## Running the Examples

All examples can be run directly from the command line:

```bash
# Example 1: Ridge regression tuning
python examples/01_ridge_tuning.py

# Example 2: Multi-model comparison
python examples/02_multi_model.py

# Example 3: Interactive optimization
python examples/03_interactive.py
```

## Example Descriptions

### 01_ridge_tuning.py
**Basic usage**: Demonstrates the simplest use case - tuning Ridge regression hyperparameters.
- Fixed model type
- Simple search space (alpha, max_iter)
- Full `run()` loop
- Shows improvement over baseline

### 02_multi_model.py
**Multi-model optimization**: Compares different model types to find the best.
- Multiple models: Ridge, Lasso, Random Forest
- Model-specific hyperparameters
- Non-linear synthetic dataset
- Demonstrates categorical parameter optimization

### 03_interactive.py
**Advanced control**: Shows the suggest-observe pattern for custom optimization loops.
- Manual iteration control
- Custom logging
- Early stopping based on convergence
- Demonstrates fine-grained control over optimization process

## Creating Your Own Examples

Template for a new example:

```python
import numpy as np
from hboptimize import HBOptimize, SearchSpace, Real, Integer, Categorical, CVRisk, Config
from hboptimize.runners.sklearn_adapter import set_data

# 1. Create dataset
X = np.random.randn(200, 10)
y = X[:, 0] + 2*X[:, 1] + np.random.randn(200) * 0.1
set_data(X, y)

# 2. Define search space
space = SearchSpace({
    'model': Categorical(('ridge', 'lasso', 'rf')),
    'param1': Real(low, high, log10=True),
    'param2': Integer(low, high),
})

# 3. Create risk estimator
risk = CVRisk(k=5, repeats=3, metric='mse')

# 4. Run optimization
config = Config(budget_evals=50, seed=42)
bo = HBOptimize(space, risk, config=config)
best_params, best_score = bo.run()
```

## Next Steps

After running these examples:
- Try with your own datasets
- Experiment with different search spaces
- Adjust CV parameters (k, repeats)
- Try different metrics ('mse' vs 'mae')
- Explore the suggest-observe pattern for custom workflows
