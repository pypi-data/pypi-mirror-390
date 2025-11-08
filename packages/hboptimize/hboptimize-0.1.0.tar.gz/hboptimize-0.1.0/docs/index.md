# HBOptimize Documentation

Welcome to HBOptimize - a lightweight Bayesian Optimization library focused on bias-variance aware hyperparameter tuning.

## Quick Links

- [Quick Start Guide](quickstart.md)
- [API Reference](api.md)
- [Examples](../examples/)

## Overview

HBOptimize provides a simple yet powerful interface for hyperparameter optimization using Bayesian Optimization with bias-variance decomposition through repeated cross-validation.

## Key Features

- **Bias-Variance Aware**: Repeated K-fold CV estimates both mean and variance
- **Heteroskedastic GP**: Models observation noise in the surrogate
- **Noisy Expected Improvement**: Acquisition function for noisy objectives
- **Sklearn Integration**: Built-in support for Ridge, Lasso, RF, GBM, SVR

## Installation

```bash
pip install -e .
```

## Basic Usage

```python
from hboptimize import HBOptimize, SearchSpace, Real, CVRisk
from hboptimize.runners.sklearn_adapter import set_data

# Prepare data
set_data(X_train, y_train)

# Define search space
space = SearchSpace({'alpha': Real(1e-4, 1e2, log10=True)})

# Optimize
risk = CVRisk(k=5, repeats=3)
opt = HBOptimize(space, risk)
best_params, best_score = opt.run()
```

See [Quick Start](quickstart.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
