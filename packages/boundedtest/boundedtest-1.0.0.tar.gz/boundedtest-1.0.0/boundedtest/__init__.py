"""
BoundedTest: GLS-based unit root tests for bounded processes

This package implements the unit root tests for bounded time series proposed by
Carrion-i-Silvestre and Gadea (2013) in Economics Letters.

Main Features:
--------------
- GLS-detrending with bound-specific non-centrality parameter
- OLS-detrending for comparison
- M-type test statistics (MZα, MSB, MZt)
- Parametric and non-parametric long-run variance estimation
- Critical values for different bounds
- Iterative estimation procedure for bounds

References:
-----------
Carrion-i-Silvestre, J.L. and Gadea, M.D. (2013). GLS-based unit root tests
for bounded processes. Economics Letters, 120(2), 184-187.

Author: Merwan Roudane
Email: merwanroudane920@gmail.com
"""

__version__ = "1.0.0"
__author__ = "Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .core import (
    bounded_unit_root_test,
    BoundedTestResult,
)

from .statistics import (
    compute_mz_alpha,
    compute_msb,
    compute_mz_t,
)

from .detrending import (
    ols_detrend,
    gls_detrend,
    estimate_bounds,
)

from .lrv import (
    estimate_lrv_np,
    estimate_lrv_ar,
)

__all__ = [
    # Main function
    'bounded_unit_root_test',
    'BoundedTestResult',
    
    # Test statistics
    'compute_mz_alpha',
    'compute_msb',
    'compute_mz_t',
    
    # Detrending
    'ols_detrend',
    'gls_detrend',
    'estimate_bounds',
    
    # LRV estimation
    'estimate_lrv_np',
    'estimate_lrv_ar',
]
