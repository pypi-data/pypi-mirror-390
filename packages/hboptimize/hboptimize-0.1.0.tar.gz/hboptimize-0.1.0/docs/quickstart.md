# Quick Start Guide

Get up and running with HBOptimize in 5 minutes.

## Installation

```bash
# Clone repository
git clone https://github.com/DashDecker/HBOptimize.git
cd HBOptimize

# Install in development mode
pip install -e .

# Or with visualization support
pip install -e ".[viz]"
```

## Your First Optimization

### Step 1: Prepare Your Data

```python
import numpy as np
from hboptimize.runners.sklearn_adapter import set_data

# Create or load your dataset
X = np.random.randn(200, 10)
y = X[:, 0] + 2*X[:, 1] + np.random.randn(200) * 0.1

# Register dataset for CV evaluation
set_data(X, y)
```

### Step 2: Define Search Space

```python
from hboptimize import SearchSpace, Real, Integer, Categorical

space = SearchSpace({
    # Model type (categorical)
    'model': Categorical(('ridge', 'lasso')),
    
    # Regularization strength (continuous, log-scale)
    'alpha': Real(1e-4, 1e2, log10=True),
    
    # Maximum iterations (integer)
    'max_iter': Integer(100, 2000),
})
```

### Step 3: Configure Cross-Validation

```python
from hboptimize import CVRisk

risk = CVRisk(
    k=5,          # 5-fold cross-validation
    repeats=3,    # Repeat 3 times for variance estimation
    metric='mse'  # Mean squared error
)
```

### Step 4: Run Optimization

```python
from hboptimize import HBOptimize, Config

# Configure optimization
config = Config(
    budget_evals=50,  # Number of configurations to try
    batch_size=1,     # Sequential evaluation
    seed=42          # For reproducibility
)

# Create optimizer
opt = HBOptimize(space, risk, config=config)

# Run!
best_params, best_score = bo.run()

print(f'Best parameters: {best_params}')
print(f'Best CV score: {best_score:.6f}')
```

## Complete Example

```python
import numpy as np
from hboptimize import HBOptimize, SearchSpace, Real, Integer, Categorical, CVRisk, Config
from hboptimize.runners.sklearn_adapter import set_data

# 1. Data
X = np.random.randn(200, 10)
y = X[:, 0] + 2*X[:, 1] + np.random.randn(200) * 0.1
set_data(X, y)

# 2. Search Space
space = SearchSpace({
    'model': Categorical(('ridge',)),
    'alpha': Real(1e-4, 1e2, log10=True),
    'max_iter': Integer(100, 2000),
})

# 3. Risk Estimator
risk = CVRisk(k=5, repeats=3, metric='mse')

# 4. Optimize
config = Config(budget_evals=30, seed=42)
opt = HBOptimize(space, risk, config=config)
best_params, best_score = bo.run()

print(best_params)
```

## Interactive Optimization

For more control, use the suggest-observe pattern:

```python
opt = HBOptimize(space, risk)

for i in range(50):
    # Get next configuration
    suggestions = bo.suggest(n=1)
    
    for cfg in suggestions:
        # Evaluate
        mean, std, meta = risk.evaluate(cfg)
        
        # Provide feedback
        bo.observe(cfg, mean, std, cost=meta.get('time'))
    
    # Check progress
    best_params, best_score = bo.best()
    print(f"Iteration {i+1}: Best = {best_score:.6f}")
```

## Parameter Types

### Real (Continuous)

```python
# Linear scale
Real(0.0, 1.0)

# Log scale (better for regularization, learning rates)
Real(1e-4, 1e2, log10=True)

# With default value
Real(0.0, 1.0, default_value=0.5)
```

### Integer

```python
# Simple range
Integer(10, 500)

# With default
Integer(10, 500, default_value=100)
```

### Categorical

```python
# Model types
Categorical(('ridge', 'lasso', 'rf'))

# Other discrete choices
Categorical(('linear', 'rbf', 'poly'))
Categorical((1, 2, 3, 4, 5))  # Numbers work too
```

## CV Configuration

```python
# Standard K-fold
CVRisk(k=5, repeats=1, metric='mse')

# Repeated for variance estimation
CVRisk(k=5, repeats=3, metric='mse')

# Fixed splits (same folds for all configs)
CVRisk(k=5, repeats=2, fixed_splits=True)

# Different metric
CVRisk(k=5, repeats=2, metric='mae')
```

## Supported Models

The sklearn adapter supports:

- **`ridge`**: Ridge Regression (params: alpha, max_iter)
- **`lasso`**: Lasso Regression (params: alpha, max_iter)
- **`rf`**: Random Forest (params: n_estimators, max_depth, min_samples_split)
- **`gbm`**: Gradient Boosting (params: n_estimators, learning_rate, max_depth)
- **`svr`**: SVR (params: C, epsilon, kernel)

## Next Steps

- Check out [examples/](../examples/) for more usage patterns
- Read the [API Reference](api.md) for detailed documentation
- Explore advanced features in the main README

## Common Issues

### Import Errors
Make sure you've installed the package:
```bash
pip install -e .
```

### Data Not Set
Always call `set_data(X, y)` before creating CVRisk or running optimization.

### Slow Optimization
- Reduce `k` or `repeats` in CVRisk
- Reduce `budget_evals` for testing
- Use simpler models first

## Getting Help

- Check the [examples/](../examples/)
- Open an issue on GitHub
- Read the API documentation
