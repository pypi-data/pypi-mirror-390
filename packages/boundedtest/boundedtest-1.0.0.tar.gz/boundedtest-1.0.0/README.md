# BoundedTest: GLS-based Unit Root Tests for Bounded Processes

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Python implementation of unit root tests for bounded time series based on Carrion-i-Silvestre and Gadea (2013).

## Overview

`boundedtest` provides comprehensive tools for testing unit roots in time series that are constrained within bounds. The package implements:

- **GLS-detrending with bound-specific non-centrality parameter** κ̅(c,c̄)
- **OLS-detrending** for comparison
- **M-type test statistics**: MZα, MSB, and MZt
- **Parametric and non-parametric long-run variance estimation**
- **Critical values** tailored to different bound configurations

## Reference

This package implements the methodology from:

> Carrion-i-Silvestre, J.L. and Gadea, M.D. (2013). "GLS-based unit root tests for bounded processes." *Economics Letters*, 120(2), 184-187.

## Installation

```bash
pip install boundedtest
```

Or install from source:

```bash
git clone https://github.com/merwanroudane/boundedtest.git
cd boundedtest
pip install -e .
```

## Quick Start

```python
import numpy as np
from boundedtest import bounded_unit_root_test

# Generate bounded data
np.random.seed(42)
data = np.cumsum(np.random.randn(200))
data = np.clip(data, -10, 10)  # Apply bounds

# Test for unit root with GLS-BOUNDS method (recommended)
result = bounded_unit_root_test(
    data=data,
    bounds=(-10, 10),
    statistic='mz_alpha',
    detrending='gls_bounds',
    lrv_method='np'
)

print(result)
```

## Main Features

### 1. Detrending Methods

- **`'ols'`**: Standard OLS detrending
- **`'gls_ers'`**: GLS detrending with standard κ = -7 (Elliott et al., 1996)
- **`'gls_bounds'`**: GLS detrending with bound-specific κ̅(c,c̄) (recommended)

### 2. Test Statistics

- **MZα**: Modified Phillips-Perron statistic
- **MSB**: Modified Sargan-Bhargava statistic  
- **MZt**: Modified t-statistic

### 3. LRV Estimation

- **Non-parametric** (`'np'`): Newey-West with automatic bandwidth selection
- **Parametric** (`'ar'`): AR-based with MAIC lag selection (Ng & Perron, 2001)

## Examples

### Example 1: Basic Usage

```python
import numpy as np
from boundedtest import bounded_unit_root_test

# Generate data
np.random.seed(123)
T = 200
data = np.cumsum(np.random.randn(T))
bounds = (-5, 5)
data = np.clip(data, bounds[0], bounds[1])

# Run test
result = bounded_unit_root_test(
    data=data,
    bounds=bounds,
    detrending='gls_bounds'
)

print(result)
print(f"\nReject H0 at 5%: {result.reject_5pct}")
```

### Example 2: Compare All Test Statistics

```python
results = bounded_unit_root_test(
    data=data,
    bounds=bounds,
    statistic='all',  # Compute all statistics
    detrending='gls_bounds'
)

# Results is a dictionary
for stat_name, result in results.items():
    print(f"\n{stat_name}:")
    print(f"  Statistic: {result.statistic:.4f}")
    print(f"  Critical (5%): {result.critical_values['5%']:.4f}")
    print(f"  Reject H0: {result.reject_5pct}")
```

### Example 3: Compare Detrending Methods

```python
methods = ['ols', 'gls_ers', 'gls_bounds']

for method in methods:
    result = bounded_unit_root_test(
        data=data,
        bounds=bounds,
        statistic='mz_alpha',
        detrending=method
    )
    print(f"\n{method.upper()}:")
    print(f"  MZα = {result.statistic:.4f}")
    print(f"  Reject H0 = {result.reject_5pct}")
```

### Example 4: With Pandas DataFrame

```python
import pandas as pd

# Create DataFrame
df = pd.DataFrame({
    'date': pd.date_range('2020-01-01', periods=200, freq='D'),
    'series': data
})

# Test using the series
result = bounded_unit_root_test(
    data=df['series'],
    bounds=bounds,
    detrending='gls_bounds'
)
```

### Example 5: Unemployment Rate (0-100% bounded)

```python
# Unemployment rate bounded between 0 and 100
unemployment = np.random.uniform(3, 10, size=100)  # Example data
unemployment += np.cumsum(np.random.randn(100)) * 0.2

result = bounded_unit_root_test(
    data=unemployment,
    bounds=(0, 100),
    detrending='gls_bounds'
)
```

## Understanding Results

The output includes:

- **Test Statistic Value**: The computed test statistic
- **Critical Values**: At 1%, 5%, and 10% significance levels
- **Rejection Decision**: Whether to reject the unit root null hypothesis
- **Bounds Information**: Original bounds and estimated c-parameters
- **Non-centrality Parameter** (κ̅): Used in GLS detrending
- **LRV Estimate**: Estimated long-run variance

### Interpretation

- **MZα and MZt**: Left-tail tests. Reject H₀ if statistic < critical value.
- **MSB**: Right-tail test. Reject H₀ if statistic > critical value.
- **H₀**: Series has a unit root (is I(1))
- **H₁**: Series is stationary (is I(0))

## Advanced Usage

### Generating Bounded Processes

```python
from boundedtest.regulated_ou import generate_bounded_ar1

# Generate bounded AR(1) process
data = generate_bounded_ar1(
    T=200,
    bounds=(-5, 5),
    rho=1.0,  # Unit root
    sigma=1.0,
    burnin=100,
    seed=42
)
```

### Custom Critical Values via Simulation

```python
from boundedtest.regulated_ou import compute_critical_values

# Compute critical values for specific bounds
cv = compute_critical_values(
    c_lower=-0.5,
    c_upper=0.5,
    kappa=0,
    n_sim=10000,
    alpha=0.05
)

print(cv)
```

### Accessing Individual Components

```python
from boundedtest import (
    ols_detrend,
    gls_detrend,
    compute_mz_alpha,
    estimate_lrv_np,
    get_kappa
)

# Manual detrending
y_tilde, _, _ = ols_detrend(data)

# Compute LRV
from boundedtest.statistics import compute_ar1_residuals
residuals = compute_ar1_residuals(y_tilde)
s2 = estimate_lrv_np(residuals)

# Compute statistic
mz_alpha = compute_mz_alpha(y_tilde, s2)
```

## API Reference

### Main Function

```python
bounded_unit_root_test(
    data,           # array-like: Time series data
    bounds,         # tuple: (lower_bound, upper_bound)
    statistic='mz_alpha',  # str: Test statistic to compute
    detrending='gls_bounds',  # str: Detrending method
    lrv_method='np',  # str: LRV estimation method
    deterministics='constant'  # str: Deterministic components
) -> BoundedTestResult
```

## Monte Carlo Simulations

The package includes utilities for Monte Carlo experiments:

```python
from boundedtest.regulated_ou import simulate_bounded_process

# Simulate under H0
data_h0 = simulate_bounded_process(
    T=200,
    b_lower=-5,
    b_upper=5,
    alpha=1.0,  # Unit root
    sigma=1.0
)

# Simulate under H1  
data_h1 = simulate_bounded_process(
    T=200,
    b_lower=-5,
    b_upper=5,
    alpha=0.95,  # Stationary
    sigma=1.0
)
```

## Requirements

- Python >= 3.8
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- Pandas >= 1.3.0
- Statsmodels >= 0.13.0

## Citation

If you use this package in your research, please cite:

```bibtex
@article{carrion2013gls,
  title={GLS-based unit root tests for bounded processes},
  author={Carrion-i-Silvestre, Josep Llu{\'\i}s and Gadea, Mar{\'\i}a Dolores},
  journal={Economics Letters},
  volume={120},
  number={2},
  pages={184--187},
  year={2013},
  publisher={Elsevier}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Merwan Roudane**  
Email: merwanroudane920@gmail.com  
GitHub: [@merwanroudane](https://github.com/merwanroudane)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This implementation is based on the methodology developed by Josep Lluís Carrion-i-Silvestre and María Dolores Gadea. The original MATLAB code and methodological guidance were instrumental in developing this Python package.

## See Also

- Original paper: [Economics Letters (2013)](https://doi.org/10.1016/j.econlet.2013.04.016)
- Elliott, Rothenberg & Stock (1996): "Efficient Tests for an Autoregressive Unit Root"
- Ng & Perron (2001): "Lag Length Selection and the Construction of Unit Root Tests"
- Cavaliere (2005): "Limited Time Series with a Unit Root"
