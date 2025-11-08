# Changelog

All notable changes to HBOptimize will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-03

### Added
- Core Bayesian Optimization loop with bias-variance estimation
- Heteroskedastic Gaussian Process surrogate model using sklearn
- Noisy Expected Improvement acquisition function
- Differential evolution-based acquisition optimization
- Repeated K-fold cross-validation risk estimator
- Sklearn adapter with support for Ridge, Lasso, RF, GBM, SVR
- Search space with Real, Integer, and Categorical parameters
- Parameter transforms (log10 for continuous variables)
- Sobol and Latin Hypercube sampling for space-filling designs
- Simple result storage and best configuration tracking
- Reproducibility utilities with seed management
- Pydantic-based configuration validation

### Features
- **Space Definition**: Flexible parameter specification with automatic transforms
- **GP Surrogate**: Matern kernel with ARD support, noise modeling
- **Risk Estimation**: CV with fixed splits for fair comparison across configs
- **API**: Both full `run()` loop and interactive `suggest()`/`observe()` pattern
- **Type Safety**: Full type hints and Pydantic validation

### Documentation
- README with quick start and examples
- Basic API reference
- Installation instructions
- MIT License

### Known Limitations
- No visualization tools yet (planned for v0.2.0)
- Single-fidelity only (multi-fidelity in v0.3.0)
- Sequential evaluation only (parallel batch in v0.4.0)
- GP warnings not suppressed (minor cleanup needed)

## [Unreleased]

### Planned for v0.2.0
- Visualization of optimization progress
- Convergence plots
- Parameter importance analysis
- Interactive progress bars

### Planned for v0.3.0
- Multi-fidelity support (early stopping, data subsampling)
- Budget-aware acquisition functions
- Cost modeling

### Planned for v0.4.0
- True parallel batch evaluation
- Distributed optimization support
- Async evaluation backend

### Planned for v0.5.0
- GPyTorch integration for better GP scalability
- Neural network surrogate options
- Custom acquisition functions

---

[0.1.0]: https://github.com/DashDecker/HBOptimize/releases/tag/v0.1.0
